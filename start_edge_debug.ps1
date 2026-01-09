# PowerShell script to start Edge in debug mode with existing profile
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Edge 브라우저 디버그 모드 시작" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Edge 경로
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edgePath)) {
    $edgePath = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}

if (-not (Test-Path $edgePath)) {
    Write-Host "[ERROR] Edge를 찾을 수 없습니다" -ForegroundColor Red
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host "[OK] Edge 경로: $edgePath" -ForegroundColor Green
Write-Host ""

# 설정 (Chrome 포트 9222 사용 - erp_upload_automation_v2.py와 호환)
$debugPort = 9222
$userDataDir = "C:\Users\DS-Sales0\AppData\Local\Microsoft\Edge\User Data"
$profileDir = "Default"
$url = "https://login.ecount.com/Login/KR/"

Write-Host "브라우저 설정:" -ForegroundColor Yellow
Write-Host "  - 디버그 포트: $debugPort (Chrome 호환)"
Write-Host "  - 프로필: $profileDir"
Write-Host "  - URL: $url (이카운트 ERP 로그인)"
Write-Host ""

# Edge 실행
Write-Host "[실행중] Edge를 디버그 모드로 시작합니다..." -ForegroundColor Yellow

$arguments = @(
    "--remote-debugging-port=$debugPort",
    "--user-data-dir=`"$userDataDir`"",
    "--profile-directory=$profileDir",
    $url
)

Start-Process -FilePath $edgePath -ArgumentList $arguments

Write-Host ""
Write-Host "[완료] Edge가 실행되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "1. Edge 브라우저 창이 열렸는지 확인하세요"
Write-Host "2. 이카운트 ERP에 로그인하세요 (로그인 버튼 클릭)"
Write-Host "3. 로그인 후 test_erp_upload_final.py를 실행할 수 있습니다"
Write-Host ""
Write-Host "포트 확인:" -ForegroundColor Yellow
Write-Host "  netstat -an | findstr :9222"
Write-Host ""
Read-Host "계속하려면 Enter를 누르세요"
