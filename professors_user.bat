@echo off
setlocal enabledelayedexpansion
rem MAETELドメインのprofessorsグループのユーザーを抽出する
rem 初期変数変更で対象変更可(実行ユーザー、ドメイン、グループ)

set RUN_USER=2180271
rem ドメインは大文字のほうがいいかも
set DOMAIN=MAETEL
set GROUP=professors

rem 現在のコードページを取得
for /f "usebackq tokens=2 delims=:" %%i in (`chcp`) do (
	set def_codepage=%%i
)
rem 英語環境へ
chcp 65001 > NUL

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
		rem 空欄、最終行は無視
		if not "!user!" == "" (
			if "%%i" == "The" (
				if "%%j" == "command" (
					if "%%k" == "completed" (
						goto :finish
					)
				)
			)
			echo !user!>>%~p0professors_user.txt
		)
    )
)

:finish
rem 元のコードページへ
chcp%def_codepage% > NUL