@echo off
setlocal enabledelayedexpansion

rem MAETELドメインのprofessorsグループに所属しているユーザーの名前を取得する
rem 同一ディレクトリにあるprofessors_user.txtにあるユーザー名から名前取得
rem 初期変数変更で対象変更可(実行ユーザー、ドメイン)

set RUN_USER=2180271
rem ドメインは大文字のほうがいいかも
set DOMAIN=MAETEL


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
del %~p0professors_name.csv
type nul > %~p0professors_name.csv
icacls %~p0professors_name.csv /grant %DOMAIN%\%RUN_USER%:F > NUL

for /f %%i in (%~p0professors_user.txt) do (
	rem ユーザー数分ループ
	set /a count=0
	echo %%i
	for /f "usebackq tokens=3,4 skip=2" %%j in (`net user %%i /domain`) do (
		set /a count=!count!+1
		if !count! EQU 1 (
			rem 名前部分のみ抽出
			echo %%i,%%j,%%k>>%~p0professors_name.csv
		)
	)
)