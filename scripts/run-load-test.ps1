# 負載測試執行腳本
# 快速驗證 API p95 <= 200ms

Write-Host "=== 社群留言爬蟲工具 - 負載測試 ===" -ForegroundColor Cyan
Write-Host ""

# 檢查 API 伺服器是否運行
Write-Host "檢查 API 伺服器..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ API 伺服器運行中" -ForegroundColor Green
} catch {
    Write-Host "✗ API 伺服器未運行" -ForegroundColor Red
    Write-Host ""
    Write-Host "請先啟動 API 伺服器:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  uvicorn main:app --reload" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "開始負載測試..." -ForegroundColor Yellow
Write-Host "  使用者: 50" -ForegroundColor Gray
Write-Host "  生成速率: 5 users/sec" -ForegroundColor Gray
Write-Host "  持續時間: 1 分鐘" -ForegroundColor Gray
Write-Host ""

# 執行 Locust
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "load-test-report-$timestamp.html"
$csvPrefix = "load-test-results-$timestamp"

Push-Location backend/tests/performance

try {
    locust -f locustfile.py `
        --host=http://localhost:8000 `
        --users 50 `
        --spawn-rate 5 `
        --run-time 1m `
        --headless `
        --html="$reportFile" `
        --csv="$csvPrefix" `
        --print-stats

    Write-Host ""
    Write-Host "=== 測試完成 ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "報告檔案:" -ForegroundColor Cyan
    Write-Host "  HTML: backend/tests/performance/$reportFile" -ForegroundColor White
    Write-Host "  CSV:  backend/tests/performance/${csvPrefix}_*.csv" -ForegroundColor White
    Write-Host ""
    Write-Host "開啟 HTML 報告..." -ForegroundColor Yellow
    Start-Process "$reportFile"
    
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "提示: 檢查 p95 回應時間是否 <= 200ms" -ForegroundColor Cyan
