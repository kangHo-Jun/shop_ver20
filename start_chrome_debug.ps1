########################################
# Chrome Debug Mode Start Script
# For ERP Upload (Playwright)
########################################

Write-Host "========================================"
Write-Host "Chrome Browser Debug Mode Start"
Write-Host "========================================"
Write-Host ""

# Chrome path
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Check Chrome path
if (-Not (Test-Path $chromePath)) {
    Write-Host "[ERROR] Chrome not found: $chromePath"
    Write-Host ""
    Write-Host "Please install Chrome or check the path."
    exit 1
}

Write-Host "[OK] Chrome path: $chromePath"
Write-Host ""

# Kill existing Chrome processes
Write-Host "Checking existing Chrome processes..."
$chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
if ($chromeProcesses) {
    Write-Host "[INFO] Chrome is running. Closing all Chrome processes..."
    Stop-Process -Name "chrome" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "[OK] Chrome closed"
}
Write-Host ""

# User data directory
$userDataDir = "$env:LOCALAPPDATA\Google\Chrome\User Data"

Write-Host "Browser settings:"
Write-Host "  - Debug port: 9222"
Write-Host "  - Profile: Default"
Write-Host "  - URL: https://login.ecount.com/Login/KR/"
Write-Host ""

# Start Chrome
Write-Host "[Running] Starting Chrome in debug mode..."

try {
    Start-Process -FilePath $chromePath -ArgumentList @(
        "--remote-debugging-port=9222",
        "--user-data-dir=`"$userDataDir`"",
        "--profile-directory=Default",
        "https://login.ecount.com/Login/KR/"
    )

    Start-Sleep -Seconds 3

    Write-Host ""
    Write-Host "[Done] Chrome is running"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Check if Chrome browser window is open"
    Write-Host "2. Login to ERP (save credentials recommended)"
    Write-Host "3. Trigger upload from V10 server"
    Write-Host ""
    Write-Host "Check port:"
    Write-Host "  netstat -an | findstr :9222"
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "[ERROR] Chrome start failed"
    exit 1
}
