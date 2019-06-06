@echo off
setlocal enabledelayedexpansion

rem MAETELドメインのprofessorsグループに所属しているユーザーの名前を取得する
rem 同一ディレクトリにあるprofessors_user.txtにあるユーザー名から名前取得

for /f "usebackq" %%i in (`icacls %~0 ^| find "2180271"`) do (
	set /a isAcs=1
)

if not defined isAcs (
	icacls %~0 /grant maetel\2180271:F > NUL
)


if not "%USERDOMAIN%" == "MAETEL" (
	runas /noprofile /user:maetel\2180271 %~0
	exit /b
)

del %~p0\professors_name.csv
type nul > %~p0\professors_name.csv
icacls %~p0\professors_name.csv /grant maetel\2180271:F > NUL
for /f %%i in (%~p0\professors_user.txt) do (
	set /a count=0
	echo %%i
	for /f "usebackq tokens=3,4 skip=2" %%j in (`net user %%i /domain`) do (
		set /a count=!count!+1
		if !count! EQU 1 (
			echo %%i,%%j,%%k>>%~p0\professors_name.csv
		)
	)
)