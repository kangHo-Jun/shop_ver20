@echo off
REM ============================================================
REM 로그인된 Edge를 디버그 모드로 재시작
REM 기존 프로필을 사용하여 로그인 상태 유지
REM ============================================================

echo ============================================================
echo 영림 로그인 Edge 브라우저 디버그 모드 재시작
echo ============================================================
echo.

echo [1/3] 현재 Edge 브라우저 종료 중...
echo.
echo *** 중요 ***
echo Edge 브라우저의 모든 창을 수동으로 닫아주세요.
echo 창을 모두 닫으신 후 Enter를 누르세요...
pause >nul

echo.
echo [2/3] 3초 대기 중...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Edge 브라우저를 디버그 모드로 재시작 중...
echo.
echo *** 브라우저 설정 ***
echo - 디버그 포트: 9333
echo - 기본 프로필 사용 (로그인 상태 유지됨)
echo - 영림 사이트 자동 열기
echo.

REM Edge를 디버그 모드로 실행 (영림 로그인된 프로필 사용)
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" ^
  --remote-debugging-port=9333 ^
  --user-data-dir="C:\Users\DS-Sales0\AppData\Local\Microsoft\Edge\User Data" ^
  --profile-directory="Default" ^
  http://door.yl.co.kr/oms/main.jsp

echo.
echo ============================================================
echo [완료] Edge 브라우저가 디버그 모드로 실행되었습니다!
echo ============================================================
echo.
echo 다음 확인사항:
echo 1. Edge 브라우저가 열렸는지 확인
echo 2. 영림 사이트 로그인 상태 확인
echo 3. 로그인되어 있으면 성공!
echo.
echo 이제 V10 서버를 재시작하면 이 브라우저에 연결됩니다.
echo.
pause
