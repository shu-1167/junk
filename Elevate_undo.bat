@echo off

rem Elevate.bat‚Å’Ç‰Á‚µ‚½ƒŒƒWƒXƒgƒŠ‚ğÁ‚·‚¾‚¯

reg delete HKCU\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /f
reg delete HKCU\Software\Classes\ms-settings\shell\open\command /ve /f