@echo off
setlocal enabledelayedexpansion
rem MAETELドメインのprofessorsグループのユーザーを抽出する
rem 初期変数変更で対象変更可(実行ユーザー、ドメイン、グループ)

set RUN_USER=2180271
rem ドメインは大文字のほうがいいかも
set DOMAIN=MAETEL
set GROUP=professors


for /f "usebackq" %%i in (`icacls %~0 ^| find "%RUN_USER%"`) do (
	rem 実行ファイルの権限チェック
	set /a isAcs=1
)

if not defined isAcs (
	rem 権限がなければ許可
	icacls %~0 /grant %DOMAIN%\%RUN_USER%:F > NUL
)


if not "%USERDOMAIN%" == "%DOMAIN%" (
	rem ドメインユーザーでなければドメインユーザーで再実行
	runas /noprofile /user:%DOMAIN%\%RUN_USER% %~f0
	exit /b
)

rem 過去ファイルの削除、新ファイルの作成
del %~p0professors_user.txt
type nul > %~p0professors_user.txt
icacls %~p0professors_user.txt /grant %DOMAIN%\%RUN_USER%:F > NUL

for /f "usebackq skip=8 tokens=1-3 delims= " %%i in (`net group %GROUP% /domain`) do (
	rem ユーザーID部分のみ抽出
	for /l %%a in (1,1,3) do (
		rem 1行に3ユーザー表示されるので分割
		if "%%a" == "1" (
			set user=%%i
		) else if "%%a" == "2" (
			set user=%%j
		) else (
			set user=%%k
		)
        echo !user!>>%~p0professors_user.txt
    )
)