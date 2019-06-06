@echo off
setlocal enabledelayedexpansion

rem MAETEL�h���C����professors�O���[�v�ɏ������Ă��郆�[�U�[�̖��O���擾����
rem ����f�B���N�g���ɂ���professors_user.txt�ɂ��郆�[�U�[�����疼�O�擾
rem �����ϐ��ύX�őΏەύX��(���s���[�U�[�A�h���C��)

set RUN_USER=2180271
rem �h���C���͑啶���̂ق�����������
set DOMAIN=MAETEL


for /f "usebackq" %%i in (`icacls %~0 ^| find "%RUN_USER%"`) do (
	rem ���s�t�@�C���̌����`�F�b�N
	set /a isAcs=1
)

if not defined isAcs (
	rem �������Ȃ���΋���
	icacls %~0 /grant %DOMAIN%\%RUN_USER%:F > NUL
)


if not "%USERDOMAIN%" == "%DOMAIN%" (
	rem �h���C�����[�U�[�łȂ���΃h���C�����[�U�[�ōĎ��s
	runas /noprofile /user:%DOMAIN%\%RUN_USER% %~f0
	exit /b
)

rem �ߋ��t�@�C���̍폜�A�V�t�@�C���̍쐬
del %~p0professors_name.csv
type nul > %~p0professors_name.csv
icacls %~p0professors_name.csv /grant %DOMAIN%\%RUN_USER%:F > NUL

for /f %%i in (%~p0professors_user.txt) do (
	rem ���[�U�[�������[�v
	set /a count=0
	echo %%i
	for /f "usebackq tokens=3,4 skip=2" %%j in (`net user %%i /domain`) do (
		set /a count=!count!+1
		if !count! EQU 1 (
			rem ���O�����̂ݒ��o
			echo %%i,%%j,%%k>>%~p0professors_name.csv
		)
	)
)