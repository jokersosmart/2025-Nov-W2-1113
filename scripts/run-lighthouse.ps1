# Lighthouse 稽核執行腳本

Write-Host "=== Lighthouse 前端效能與無障礙性稽核 ===" -ForegroundColor Cyan
Write-Host ""

# 檢查 Node.js
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js 未安裝" -ForegroundColor Red
    exit 1
}

# 檢查 Lighthouse
Write-Host "檢查 Lighthouse..." -ForegroundColor Yellow
try {
    $lhVersion = lighthouse --version
    Write-Host "✓ Lighthouse: $lhVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Lighthouse 未安裝,正在安裝..." -ForegroundColor Yellow
    npm install -g lighthouse
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Lighthouse 安裝失敗" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Lighthouse 安裝完成" -ForegroundColor Green
}

Write-Host ""
Write-Host "檢查前端伺服器..." -ForegroundColor Yellow

# 檢查前端伺服器是否運行
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ 前端伺服器運行中" -ForegroundColor Green
} catch {
    Write-Host "✗ 前端伺服器未運行" -ForegroundColor Red
    Write-Host ""
    Write-Host "請先啟動前端伺服器:" -ForegroundColor Yellow
    Write-Host "  cd frontend" -ForegroundColor White
    Write-Host "  npm run dev" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "開始 Lighthouse 稽核..." -ForegroundColor Yellow
Write-Host "  URL: http://localhost:5173" -ForegroundColor Gray
Write-Host "  類別: Performance, Accessibility, Best Practices, SEO" -ForegroundColor Gray
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportDir = "frontend/tests/lighthouse/reports"

# 創建報告目錄
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# 執行 Desktop 稽核
Write-Host "[1/2] 執行 Desktop 稽核..." -ForegroundColor Cyan
$desktopReport = "$reportDir/lighthouse-desktop-$timestamp.html"
$desktopJson = "$reportDir/lighthouse-desktop-$timestamp.json"

lighthouse http://localhost:5173 `
    --output html `
    --output json `
    --output-path "$reportDir/lighthouse-desktop-$timestamp" `
    --preset=desktop `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Desktop 稽核完成" -ForegroundColor Green
} else {
    Write-Host "✗ Desktop 稽核失敗" -ForegroundColor Red
}

Write-Host ""

# 執行 Mobile 稽核
Write-Host "[2/2] 執行 Mobile 稽核..." -ForegroundColor Cyan
$mobileReport = "$reportDir/lighthouse-mobile-$timestamp.html"
$mobileJson = "$reportDir/lighthouse-mobile-$timestamp.json"

lighthouse http://localhost:5173 `
    --output html `
    --output json `
    --output-path "$reportDir/lighthouse-mobile-$timestamp" `
    --preset=mobile `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Mobile 稽核完成" -ForegroundColor Green
} else {
    Write-Host "✗ Mobile 稽核失敗" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== 稽核完成 ===" -ForegroundColor Green
Write-Host ""

# 解析 JSON 報告並顯示分數
function Show-LighthouseScores {
    param($jsonPath, $platform)
    
    if (Test-Path $jsonPath) {
        $report = Get-Content $jsonPath | ConvertFrom-Json
        $categories = $report.categories
        
        Write-Host "$platform 分數:" -ForegroundColor Cyan
        
        $perf = [math]::Round($categories.performance.score * 100)
        $a11y = [math]::Round($categories.accessibility.score * 100)
        $bp = [math]::Round($categories.'best-practices'.score * 100)
        $seo = [math]::Round($categories.seo.score * 100)
        
        $perfColor = if ($perf -ge 90) { "Green" } elseif ($perf -ge 50) { "Yellow" } else { "Red" }
        $a11yColor = if ($a11y -ge 90) { "Green" } elseif ($a11y -ge 50) { "Yellow" } else { "Red" }
        $bpColor = if ($bp -ge 90) { "Green" } elseif ($bp -ge 50) { "Yellow" } else { "Red" }
        $seoColor = if ($seo -ge 90) { "Green" } elseif ($seo -ge 50) { "Yellow" } else { "Red" }
        
        Write-Host "  Performance:    $perf/100 " -NoNewline
        Write-Host $(if ($perf -ge 95) { "✓" } else { "✗" }) -ForegroundColor $perfColor
        
        Write-Host "  Accessibility:  $a11y/100 " -NoNewline
        Write-Host $(if ($a11y -ge 95) { "✓" } else { "✗" }) -ForegroundColor $a11yColor
        
        Write-Host "  Best Practices: $bp/100 " -NoNewline
        Write-Host $(if ($bp -ge 90) { "✓" } else { "⚠" }) -ForegroundColor $bpColor
        
        Write-Host "  SEO:            $seo/100 " -NoNewline
        Write-Host $(if ($seo -ge 90) { "✓" } else { "⚠" }) -ForegroundColor $seoColor
        
        Write-Host ""
        
        # 顯示關鍵指標
        $metrics = $report.audits
        if ($metrics.'first-contentful-paint') {
            $fcp = [math]::Round($metrics.'first-contentful-paint'.numericValue / 1000, 2)
            Write-Host "  FCP: ${fcp}s" -ForegroundColor Gray
        }
        if ($metrics.'largest-contentful-paint') {
            $lcp = [math]::Round($metrics.'largest-contentful-paint'.numericValue / 1000, 2)
            Write-Host "  LCP: ${lcp}s" -ForegroundColor Gray
        }
        if ($metrics.'total-blocking-time') {
            $tbt = [math]::Round($metrics.'total-blocking-time'.numericValue)
            Write-Host "  TBT: ${tbt}ms" -ForegroundColor Gray
        }
        if ($metrics.'cumulative-layout-shift') {
            $cls = [math]::Round($metrics.'cumulative-layout-shift'.numericValue, 3)
            Write-Host "  CLS: $cls" -ForegroundColor Gray
        }
        
        Write-Host ""
        
        # 檢查是否達成目標
        $success = $perf -ge 95 -and $a11y -ge 95
        return $success
    }
    return $false
}

$desktopSuccess = Show-LighthouseScores "$desktopJson" "Desktop"
$mobileSuccess = Show-LighthouseScores "$mobileJson" "Mobile"

Write-Host "報告檔案:" -ForegroundColor Cyan
Write-Host "  Desktop HTML: $desktopReport" -ForegroundColor White
Write-Host "  Desktop JSON: $desktopJson" -ForegroundColor White
Write-Host "  Mobile HTML:  $mobileReport" -ForegroundColor White
Write-Host "  Mobile JSON:  $mobileJson" -ForegroundColor White
Write-Host ""

# 開啟報告
Write-Host "開啟報告..." -ForegroundColor Yellow
if (Test-Path "$desktopReport.html") {
    Start-Process "$desktopReport.html"
}

Write-Host ""
if ($desktopSuccess -and $mobileSuccess) {
    Write-Host "✓ 成功達成目標 (Performance >= 95, Accessibility >= 95)" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ 未達成目標,請檢查報告並最佳化" -ForegroundColor Yellow
    exit 1
}
