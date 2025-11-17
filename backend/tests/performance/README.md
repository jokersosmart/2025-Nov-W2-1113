# 負載測試指南

## 目的

驗證系統在負載下的效能表現,確保:
- **p95 回應時間 <= 200ms** (成功標準)
- 錯誤率 < 1%
- 系統穩定性

## 前置需求

### 安裝 Locust

```bash
pip install locust
```

或使用專案虛擬環境:

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install locust
```

### 啟動 API 伺服器

```bash
cd backend
uvicorn main:app --reload
```

伺服器應運行於 `http://localhost:8000`

## 執行負載測試

### 方式 1: Web UI (推薦)

1. 啟動 Locust:
```bash
cd backend
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

2. 開啟瀏覽器訪問: `http://localhost:8089`

3. 設定測試參數:
   - **Number of users**: 50 (模擬50個並發使用者)
   - **Spawn rate**: 5 (每秒增加5個使用者)
   - **Host**: http://localhost:8000

4. 點擊 "Start swarming"

5. 觀察指標:
   - **p95**: 應 <= 200ms
   - **Failures**: 應 < 1%
   - **RPS (Requests per second)**: 觀察系統吞吐量

### 方式 2: 命令行

快速測試 (10個使用者, 30秒):
```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 30s \
  --headless \
  --print-stats
```

標準測試 (50個使用者, 2分鐘):
```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless \
  --html=load-test-report.html \
  --csv=load-test-results
```

壓力測試 (100個使用者, 5分鐘):
```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless \
  --html=stress-test-report.html
```

## 測試場景

### SocialCommentScraperUser
模擬真實使用者行為:
- 30% 健康檢查
- 20% 查詢根路由
- 20% 查詢不存在的爬取狀態
- 10% 無效URL爬取請求
- 10% 查詢OpenAPI文件
- 10% 匯出不存在的貼文

### FastAPIReadOnlyUser
唯讀操作使用者:
- 50% 健康檢查
- 30% 瀏覽API文件
- 20% 獲取OpenAPI schema

### StressTestUser
壓力測試使用者:
- 快速連續請求
- 短等待時間 (0.1-0.5秒)

## 選擇測試用戶類型

預設使用 `SocialCommentScraperUser`。指定其他類型:

```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 20 \
  --spawn-rate 5 \
  --run-time 1m \
  --headless \
  --user-classes FastAPIReadOnlyUser
```

混合測試 (多種使用者):
```bash
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 30 \
  --spawn-rate 5 \
  --run-time 2m \
  --headless \
  --user-classes SocialCommentScraperUser,FastAPIReadOnlyUser
```

## 成功標準

### 必須達成 (T049)
- ✅ **p95 <= 200ms**: 95%的請求回應時間不超過200毫秒
- ✅ **錯誤率 < 1%**: 失敗請求少於總請求的1%
- ✅ **無崩潰**: 測試期間系統不崩潰

### 建議目標
- **p50 <= 100ms**: 中位數回應時間
- **p99 <= 500ms**: 99%請求回應時間
- **RPS >= 50**: 每秒至少處理50個請求

## 結果解讀

### Locust Web UI 指標

1. **Total Requests**: 總請求數
2. **Failures**: 失敗數量與百分比
3. **Median**: p50 回應時間
4. **95%ile**: p95 回應時間 ← **關鍵指標**
5. **99%ile**: p99 回應時間
6. **Average**: 平均回應時間
7. **RPS**: 每秒請求數

### HTML 報告

查看生成的 `load-test-report.html`:
- 圖表顯示回應時間分布
- 失敗請求詳情
- 各端點效能對比

### CSV 結果

查看 `load-test-results_stats.csv`:
```csv
Type,Name,Request Count,Failure Count,Median,95%ile,99%ile,Average,Min,Max,RPS
GET,/health,1500,0,25,45,60,28,20,150,50.2
GET,/,1000,0,30,55,70,35,25,120,33.5
...
```

## 最佳化建議

如果 p95 > 200ms:

1. **檢查資料庫查詢**
   - 添加索引
   - 優化 SQL 查詢

2. **使用快取**
   - Redis 快取常用資料
   - 靜態內容 CDN

3. **並行處理**
   - 使用 asyncio
   - 批次處理請求

4. **硬體升級**
   - 增加 CPU/記憶體
   - 使用 SSD

## 持續監控

將負載測試整合至 CI/CD:

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * 0'  # 每週日凌晨2點

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start API
        run: |
          cd backend
          uvicorn main:app &
          sleep 5
      - name: Run Locust
        run: |
          pip install locust
          locust -f backend/tests/performance/locustfile.py \
            --host=http://localhost:8000 \
            --users 50 \
            --spawn-rate 5 \
            --run-time 2m \
            --headless \
            --html=report.html
      - name: Check p95
        run: |
          # Parse results and fail if p95 > 200ms
          python scripts/check_performance.py
```

## 故障排除

### 連線被拒絕
確認 API 伺服器正在運行:
```bash
curl http://localhost:8000/health
```

### 記憶體不足
減少並發使用者數量:
```bash
--users 20
```

### 埠號衝突
變更 Locust Web UI 埠號:
```bash
locust -f locustfile.py --web-port 8090
```

## 參考

- [Locust 官方文件](https://docs.locust.io/)
- [效能測試最佳實踐](https://martinfowler.com/articles/practical-test-pyramid.html)
