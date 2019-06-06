@echo off
setlocal enabledelayedexpansion
rem MAETELドメインのprofessorグループのユーザーを抽出する

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

del %~p0\professors_user.txt
type nul > %~p0\professors_user.txt
icacls %~p0\professors_user.txt /grant maetel\2180271:F > NUL
for /f "usebackq skip=8 tokens=1-3 delims= " %%i in (`net group professors /domain`) do (
	for /l %%a in (1,1,3) do (
		if "%%a" == "1" (
			set user=%%i
		) else if "%%a" == "2" (
			set user=%%j
		) else (
			set user=%%k
		)
        echo !user!>>%~p0\professors_user.txt
    )
)