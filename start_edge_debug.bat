@echo off
REM ============================================================
REM 영림 Edge 브라우저를 디버그 모드로 실행
REM V10 서버가 이 브라우저에 연결합니다
REM ============================================================

echo ============================================================
echo 영림 Edge 브라우저 디버그 모드 실행
echo ============================================================
echo.

REM 기존 Edge 브라우저 종료 확인
echo [1/3] 기존 Edge 브라우저 확인 중...
tasklist /FI "IMAGENAME eq msedge.exe" 2>NUL | find /I /N "msedge.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [경고] Edge 브라우저가 실행 중입니다.
    echo        영림 사이트 로그인 상태를 유지하려면 종료하지 마세요.
    echo.
    choice /C YN /M "기존 브라우저를 종료하고 디버그 모드로 재시작하시겠습니까?"
    if errorlevel 2 goto :skip_kill
    if errorlevel 1 goto :do_kill
) else (
    echo [OK] 실행 중인 Edge 브라우저가 없습니다.
    goto :start_browser
)

:do_kill
echo [2/3] Edge 브라우저 종료 중...
taskkill /F /IM msedge.exe >NUL 2>&1
timeout /t 3 /nobreak >NUL
echo [OK] 브라우저 종료 완료
goto :start_browser

:skip_kill
echo [정보] 브라우저 종료를 건너뜁니다.
echo.
echo 주의: 기존 브라우저가 디버그 포트 9333으로 실행되지 않았다면
echo       V10 서버가 연결할 수 없습니다.
echo.
pause
exit

:start_browser
echo [3/3] 디버그 모드로 Edge 브라우저 실행 중...
echo.

REM Edge 브라우저를 디버그 포트 9333으로 실행 (기존 Default 프로필 사용)
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" ^
  --remote-debugging-port=9333 ^
  --user-data-dir="C:\Users\DS-Sales0\AppData\Local\Microsoft\Edge\User Data" ^
  --profile-directory="Default" ^
  --no-first-run ^
  --no-default-browser-check ^
  http://door.yl.co.kr/oms/main.jsp

echo.
echo ============================================================
echo [완료] Edge 브라우저가 디버그 모드로 실행되었습니다!
echo ============================================================
echo.
echo 다음 단계:
echo 1. 브라우저에서 영림 사이트에 로그인하세요
echo 2. 로그인 상태를 유지하세요
echo 3. V10 서버를 실행하세요
echo.
echo 주의사항:
echo - 이 브라우저 창을 닫지 마세요
echo - 디버그 포트: 9333
echo - 프로필 위치: %cd%\edge_automation_profile
echo.
echo 이제 V10 서버가 이 브라우저에 자동으로 연결됩니다.
echo.
pause
