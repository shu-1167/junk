@echo off
setlocal enabledelayedexpansion
rem �h���C���̃��[�U�[�������̐l���𒊏o����

set RUN_USER=2180271
rem �h���C���͑啶���̂ق�����������
set DOMAIN=MAETEL

for /f "usebackq" %%i in (`icacls "%~0" ^| find "%RUN_USER%"`) do (
	rem ���s�t�@�C���̌����`�F�b�N
	set /a isAcs=1
)

if not defined isAcs (
	rem �������Ȃ���΋���
	icacls "%~0" /grant %DOMAIN%\%RUN_USER%:F > NUL
)


if not "%USERDOMAIN%" == "%DOMAIN%" (
	rem �h���C�����[�U�[�łȂ���΃h���C�����[�U�[�ōĎ��s
	runas /noprofile /user:%DOMAIN%\%RUN_USER% "%~f0"
	exit /b
)

rem ���O�i���j����
set /p name="input name:"
rem ���[�U�[ID�̓�����(218)����
set /p num="input top number:"

for /f "usebackq skip=6 tokens=1-3 delims= " %%i in (`net user /domain`) do (
	rem �h���C���̃��[�U�[�ꗗ���擾
	for /l %%a in (1,1,3) do (
		if "%%a" == "1" (
			set user=%%i
		) else if "%%a" == "2" (
			set user=%%j
		) else (
			set user=%%k
		)
		
		for /f "usebackq delims=0 tokens=1" %%u in (`echo !user!`) do (
			rem 0�܂ł̕�����؂�o��
			set top_user=%%u
		)

		if "!user!" == "�R�}���h�͐���ɏI�����܂����B" (
			rem �ŏI�s
			echo No hit
		) else if defined num (
			rem ���[�U�[ID���w�莞
			if "%num%" == "!top_user!" (
				rem �w��ƈ�v���鎞
				echo  !user!
				for /f "usebackq skip=2 tokens=3 delims= " %%l in (`net user !user! /domain`) do (
					if "%%l" == "%name%" (
						rem HIT!
						net user !user! /domain
						pause
						exit /b
					)
				)
			) else (
				echo skip !user!
			)
		) else (
			rem ���w�莞
			echo !user!
			for /f "usebackq skip=2 tokens=3 delims= " %%l in (`net user !user! /domain`) do (
				if "%%l" == "%name%" (
					rem HIT!
					net user !user! /domain
					pause
					exit /b
				)
			)
		)
	)
)
pause