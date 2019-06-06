@echo off
setlocal enabledelayedexpansion
rem MAETELドメインのprofessorsグループに所属しているユーザーの名前を取得する

if not "%USERDOMAIN%" == "MAETEL" (
	runas /noprofile /user:maetel\2180271 %~0
	exit /b
)

del %~p0\professors_name.csv
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