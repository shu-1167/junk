@echo off

rem Elevate.bat�Œǉ��������W�X�g������������

reg delete HKCU\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /f
reg delete HKCU\Software\Classes\ms-settings\shell\open\command /ve /f