@echo off

rem ���{��L�[�{�[�h�z���dvorak�z��ɕύX���܂�
rem �ݒ�͍ċN����ɗL���ɂȂ�܂�

rem �Ǘ��Ҍ����̊m�F
openfiles > NUL 2>&1
if not %ERRORLEVEL% equ 0 (
	if "%%1" == "ps" (
		powershell start-process "%~f0" -verb runas
	) else (
		reg add HKCU\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /t REG_SZ /f > NUL
		reg add HKCU\Software\Classes\ms-settings\shell\open\command /ve /t REG_SZ /d "%~f0" /f > NUL
		%SYSTEMROOT%\System32\ComputerDefaults.exe
		timeout /t 1 /nobreak > NUL

		reg delete HKCU\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /f > NUL
		reg delete HKCU\Software\Classes\ms-settings\shell\open\command /ve /f > NUL
	)
	exit /b

) else (
	for /f "usebackq tokens=4" %%i in (`reg query HKLM\SYSTEM\CurrentControlSet\Services\i8042prt\Parameters /v "LayerDriver JPN"`) do (
		echo Currently set of %%i
		if "%%i" == "kbddv.dll" (
			echo Changing to kbd106
			reg add HKLM\SYSTEM\CurrentControlSet\Services\i8042prt\Parameters /v "LayerDriver JPN" /t REG_SZ /d kbd106.dll /f > NUL
		) else (
			echo Changing to kbddv
			reg add HKLM\SYSTEM\CurrentControlSet\Services\i8042prt\Parameters /v "LayerDriver JPN" /t REG_SZ /d kbddv.dll /f > NUL
		)
	)
)
pause
shutdown /l /f
