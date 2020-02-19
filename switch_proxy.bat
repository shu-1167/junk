@echo off
setlocal enabledelayedexpansion
rem プロキシの設定をトグル変更する
rem 既存の設定を上書きします。sshダイナミックフォワード向け。
rem Socks以外も対応可能かと思います(未確認)

rem set CONFIG="http=example.com:8888;https=example.com:8888;ftp=example.com:8888;socks=example.com:8888"
set CONFIG="socks=localhost:8080"


for /f "usebackq tokens=1,3" %%i in (`reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /f "ProxyEnable"`) do (
	if "%%i" == "ProxyEnable" (
		set regvalue=%%j
	)
)


if "%regvalue%" == "0x0" (
	rem 有効化
	echo enabling...
	
	if defined TMP (
		rem %TMP%に書き込めるかチェック
		copy NUL "%TMP%\.tmp" > NUL 2>&1
		if exist "%TMP%\.tmp" (
			rem 書き込み可能
			del /f "%TMP%\.tmp"
			call :encode TMP
			for /f "usebackq" %%i in (`type "%TMP%\hex.out"`) do (
				set config_hex=%%i
			)
			del /f "%TMP%\hex.txt" "%TMP%\hex.out"
		) else (
			rem 環境変数にTMPがあるが、書き込めない場合
			call :encode %~p0
			for /f "usebackq" %%i in (`type "%~p0hex.out"`) do (
				set config_hex=%%i
			)
			del /f "%~p0hex.txt" "%~p0hex.out"
		)
	) else (
		rem 環境変数にTMPがない場合
		call :encode %~p0
		for /f "usebackq" %%i in (`type "%~p0hex.out"`) do (
			set config_hex=%%i
		)
		del /f "%~p0hex.txt" "%~p0hex.out"
	)

	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v "ProxyEnable" /t REG_DWORD /d 1 /f > NUL
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections" /v "DefaultConnectionSettings" /t REG_BINARY /d 46000000060000000300000014000000!config_hex!00000000000000000000000000000000000000000000000000000000000000000000000000000000 /f > NUL
) else (
	rem 無効化
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
	rem TMPディレクトリを取得
	set write_dir=%TMP%\
) else (
	rem 書き込み確認
	copy NUL "%write_dir%.tmp" > NUL 2>&1
	if exist "%write_dir%.tmp" (
		rem 書き込み可能
		del /f "%write_dir%.tmp"
	) else (
		rem 書き込めなかった
		echo Couldn't write file %write_dir%.tmp
		pause
		exit /b
	)
)

set /p null=%CONFIG%<NUL>"%write_dir%hex.txt"
certutil -f -encodehex "%write_dir%hex.txt" "%write_dir%hex.out" 12 > NUL 2>&1
exit /b
