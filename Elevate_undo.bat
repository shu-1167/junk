@echo off

rem Elevate.batで追加したレジストリを消すだけ

reg delete HKCU\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /f
reg delete HKCU\Software\Classes\ms-settings\shell\open\command /ve /f