@echo off
setlocal enabledelayedexpansion
rem �v���L�V�̐ݒ���g�O���ύX����
rem �����̐ݒ���㏑�����܂��Bssh�_�C�i�~�b�N�t�H���[�h�����B
rem Socks�ȊO���Ή��\���Ǝv���܂�(���m�F)

rem set CONFIG="http=example.com:8888;https=example.com:8888;ftp=example.com:8888;socks=example.com:8888"
set CONFIG="socks=localhost:8080"


for /f "usebackq tokens=1,3" %%i in (`reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /f "ProxyEnable"`) do (
	if "%%i" == "ProxyEnable" (
		set regvalue=%%j
	)
)


if "%regvalue%" == "0x0" (
	rem �L����
	echo enabling...
	
	if defined TMP (
		rem %TMP%�ɏ������߂邩�`�F�b�N
		copy NUL "%TMP%\.tmp" > NUL 2>&1
		if exist "%TMP%\.tmp" (
			rem �������݉\
			del /f "%TMP%\.tmp"
			call :encode TMP
			for /f "usebackq" %%i in (`type "%TMP%\hex.out"`) do (
				set config_hex=%%i
			)
			del /f "%TMP%\hex.txt" "%TMP%\hex.out"
		) else (
			rem ���ϐ���TMP�����邪�A�������߂Ȃ��ꍇ
			call :encode %~p0
			for /f "usebackq" %%i in (`type "%~p0hex.out"`) do (
				set config_hex=%%i
			)
			del /f "%~p0hex.txt" "%~p0hex.out"
		)
	) else (
		rem ���ϐ���TMP���Ȃ��ꍇ
		call :encode %~p0
		for /f "usebackq" %%i in (`type "%~p0hex.out"`) do (
			set config_hex=%%i
		)
		del /f "%~p0hex.txt" "%~p0hex.out"
	)

	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v "ProxyEnable" /t REG_DWORD /d 1 /f > NUL
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v "DefaultConnectionSettings" /t REG_BINARY /d 46000000060000000300000014000000!config_hex!00000000000000000000000000000000000000000000000000000000000000000000000000000000 /f > NUL
) else (
	rem ������
	echo disabling...
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v "ProxyEnable" /t REG_DWORD /d 0 /f > NUL
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v "DefaultConnectionSettings" /t REG_BINARY /d 4600000006000000010000001400000000000000000000000000000000000000000000000000000000000000000000000000000000000000 /f > NUL
)
echo Done!
pause

exit /b


:encode
set write_dir=%1
if "%write_dir%" == "TMP" (
	rem TMP�f�B���N�g�����擾
	set write_dir=%TMP%\
) else (
	rem �������݊m�F
	copy NUL "%write_dir%.tmp" > NUL 2>&1
	if exist "%write_dir%.tmp" (
		rem �������݉\
		del /f "%write_dir%.tmp"
	) else (
		rem �������߂Ȃ�����
		echo Couldn't write file %write_dir%.tmp
		pause
		exit /b
	)
)

set /p null=%CONFIG%<NUL>"%write_dir%hex.txt"
certutil -f -encodehex "%write_dir%hex.txt" "%write_dir%hex.out" 12 > NUL 2>&1
exit /b
