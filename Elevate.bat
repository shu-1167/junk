@echo off

rem UAC�̊m�F�����Ō������i�ł��܂�
rem ���s���郆�[�U�[��Administrators�O���[�v�ɑ����Ă���K�v������܂�

rem ��������s������A�ꕔ�s����o��\��������̂ŁA
rem Elevate_undo.bat�����s���Č��ɖ߂��Ă������ق��������Ǝv���܂��i�����͌l�̎��R�j

rem Windows 10 Pro 1809(17763.437)�ɂē���m�F
rem Windows 10 Pro 1903(18362.418)�ł�����m�F

reg add HKCU\Software\Classes\ms-settings\shell\open\command /v DelegateExecute /t REG_SZ /f
reg add HKCU\Software\Classes\ms-settings\shell\open\command /ve /t REG_SZ /d "%SYSTEMROOT%\System32\cmd.exe" /f
%SYSTEMROOT%\System32\ComputerDefaults.exe