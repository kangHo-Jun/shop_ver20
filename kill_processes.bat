@echo off
echo ========================================
echo   Cleaning up existing processes...
echo ========================================

echo [1/2] Terminating Python processes (v10 servers)...
taskkill /F /IM python.exe /T 2>nul
if errorlevel 1 (
    echo No python processes found.
) else (
    echo Python processes terminated.
)

echo [2/2] Terminating Microsoft Edge debug processes...
taskkill /F /IM msedge.exe /T 2>nul
if errorlevel 1 (
    echo No Edge processes found.
) else (
    echo Edge processes terminated.
)

echo.
echo Cleanup complete.
echo ========================================
pause
