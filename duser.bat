@echo off
setlocal enabledelayedexpansion
rem ドメインのユーザーから特定の人物を抽出する

rem 名前（性）入力
set /p name="input name:"
rem ユーザーIDの頭部分(218)入力
set /p num="input top number:"

for /f "usebackq skip=6 tokens=1-3 delims= " %%i in (`net user /domain`) do (
	rem ドメインのユーザー一覧を取得
	for /l %%a in (1,1,3) do (
		if "%%a" == "1" (
			set user=%%i
		) else if "%%a" == "2" (
			set user=%%j
		) else (
			set user=%%k
		)
		
		for /f "usebackq delims=0 tokens=1" %%u in (`echo !user!`) do (
			rem 0までの文字を切り出し
			set top_user=%%u
		)

		if "!user!" == "コマンドは正常に終了しました。" (
			rem 最終行
			echo unti
		) else if defined num (
			rem ユーザーID頭指定時
			if "%num%" == "!top_user!" (
				rem 指定と一致する時
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
			rem 未指定時
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