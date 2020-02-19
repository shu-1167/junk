@echo off
rem プロキシの設定をSocks localhost:8080 でトグル変更する
rem 既存の設定を上書きします。sshダイナミックフォワード向け。


for /f "usebackq tokens=1,3" %%i in (`reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /f "ProxyEnable"`) do (
	if "%%i" == "ProxyEnable" (
		set regvalue=%%j
	)
)

if "%regvalue%" == "0x0" (
	rem 有効化
	echo enabling...
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v "ProxyEnable" /t REG_DWORD /d 1 /f > NUL
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v "DefaultConnectionSettings" /t REG_BINARY /d 46000000060000000300000014000000736f636b733d6c6f63616c686f73743a3830383000000000000000000000000000000000000000000000000000000000000000000000000000000000 /f > NUL
) else (
	rem 無効化
	echo disabling...
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v "ProxyEnable" /t REG_DWORD /d 0 /f > NUL
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v "DefaultConnectionSettings" /t REG_BINARY /d 46000000060000000100000014000000736f636b733d6c6f63616c686f73743a3830383000000000000000000000000000000000000000000000000000000000000000000000000000000000 /f > NUL
)
echo Done!
pause

exit /b