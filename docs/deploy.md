# 部署文件

## 目錄

1. [系統需求](#系統需求)
2. [本地開發環境](#本地開發環境)
3. [Docker 部署](#docker-部署)
4. [生產環境部署](#生產環境部署)
5. [環境變數配置](#環境變數配置)
6. [健康檢查](#健康檢查)
7. [疑難排解](#疑難排解)

---

## 系統需求

### 後端需求

- **Python**: 3.11 或更高版本
- **套件管理**: pip
- **虛擬環境**: venv (建議)

### 前端需求

- **Node.js**: 18.x 或更高版本
- **套件管理**: npm 9.x 或更高版本

### Docker 部署需求

- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本

---

## 本地開發環境

### 1. Clone 專案

```bash
git clone https://github.com/jokersosmart/2025-Nov-W2-1113.git
cd COM_PAR
```

### 2. 後端設置

```powershell
# 進入後端目錄
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
.\venv\Scripts\Activate.ps1  # PowerShell
# 或
.\venv\Scripts\activate.bat  # CMD

# 安裝依賴
pip install -r requirements.txt

# 啟動後端服務
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

後端服務將運行在 `http://localhost:8000`

**API 文件**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 前端設置

```powershell
# 開啟新的 terminal,進入前端目錄
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
```

前端應用將運行在 `http://localhost:5173`

### 4. 執行測試

**後端測試**:
```powershell
cd backend

# 執行所有測試
pytest

# 執行測試並生成覆蓋率報告
pytest --cov=src --cov-report=html

# 執行特定測試檔案
pytest tests/contract/test_export_contract.py -v
```

**前端測試**:
```powershell
cd frontend

# 執行單元測試
npm run test

# 執行測試並顯示覆蓋率
npm run test:coverage

# 執行整合測試
npm run test:integration
```

---

## Docker 部署

### 使用 Docker Compose (推薦)

**優點**:
- 一鍵啟動前後端
- 自動配置網路
- 統一管理容器

**步驟**:

```bash
# 1. 在專案根目錄執行
docker-compose up -d

# 2. 查看服務狀態
docker-compose ps

# 3. 查看日誌
docker-compose logs -f

# 4. 停止服務
docker-compose down

# 5. 重新建置並啟動
docker-compose up --build -d
```

**服務訪問**:
- 前端: http://localhost:5173
- 後端 API: http://localhost:8000
- API 文件: http://localhost:8000/docs

### 單獨執行後端容器

```bash
# 建置映像
cd backend
docker build -t com-par-backend .

# 執行容器
docker run -d \
  --name com-par-backend \
  -p 8000:8000 \
  -e ENV=production \
  com-par-backend

# 查看日誌
docker logs -f com-par-backend

# 停止容器
docker stop com-par-backend

# 移除容器
docker rm com-par-backend
```

### 單獨執行前端容器

```bash
# 建置映像
cd frontend
docker build -t com-par-frontend .

# 執行容器
docker run -d \
  --name com-par-frontend \
  -p 5173:5173 \
  -e VITE_API_URL=http://localhost:8000 \
  com-par-frontend

# 查看日誌
docker logs -f com-par-frontend

# 停止容器
docker stop com-par-frontend

# 移除容器
docker rm com-par-frontend
```

---

## 生產環境部署

### 建議架構

```
Internet
    |
    v
Load Balancer (Nginx/Traefik)
    |
    ├── Frontend (Static Files)
    |
    └── Backend API (Gunicorn/Uvicorn)
```

### 1. 後端生產部署

#### 使用 Gunicorn + Uvicorn Workers

```bash
# 安裝 Gunicorn
pip install gunicorn

# 啟動生產伺服器
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### 使用 Systemd Service

建立 `/etc/systemd/system/com-par-backend.service`:

```ini
[Unit]
Description=COM PAR Backend API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/com-par/backend
Environment="PATH=/opt/com-par/backend/venv/bin"
ExecStart=/opt/com-par/backend/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

啟動服務:
```bash
sudo systemctl enable com-par-backend
sudo systemctl start com-par-backend
sudo systemctl status com-par-backend
```

### 2. 前端生產部署

#### 建置生產版本

```bash
cd frontend

# 建置
npm run build

# 輸出在 dist/ 目錄
```

#### 使用 Nginx 提供靜態檔案

Nginx 配置 `/etc/nginx/sites-available/com-par`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端靜態檔案
    location / {
        root /opt/com-par/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 後端 API 代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

啟用配置:
```bash
sudo ln -s /etc/nginx/sites-available/com-par /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. HTTPS 配置 (Let's Encrypt)

```bash
# 安裝 Certbot
sudo apt install certbot python3-certbot-nginx

# 取得憑證
sudo certbot --nginx -d your-domain.com

# 自動續期
sudo certbot renew --dry-run
```

---

## 環境變數配置

### 後端環境變數

建立 `backend/.env`:

```env
# 環境
ENV=production

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# CORS 設定 (生產環境)
CORS_ORIGINS=https://your-domain.com

# 日誌等級
LOG_LEVEL=INFO

# 爬蟲配置
SCRAPE_BATCH_SIZE=100
SCRAPE_DELAY_SECONDS=3

# 速率限制
RATE_LIMIT_PER_MINUTE=60
```

### 前端環境變數

建立 `frontend/.env.production`:

```env
# API Base URL (生產環境)
VITE_API_URL=https://api.your-domain.com

# 應用配置
VITE_APP_TITLE=Social Comment Scraper
VITE_APP_VERSION=0.1.0
```

---

## 健康檢查

### 後端健康檢查

```bash
curl http://localhost:8000/health
```

**預期回應**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "Social Comment Scraper API"
}
```

### Docker 健康檢查

Docker Compose 已配置自動健康檢查:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

查看健康狀態:
```bash
docker ps
# STATUS 欄位會顯示 healthy 或 unhealthy
```

---

## 監控與日誌

### 日誌位置

**後端日誌**:
- Docker: `docker logs com-par-backend`
- Systemd: `journalctl -u com-par-backend -f`
- 檔案: `/var/log/com-par/backend.log`

**前端日誌**:
- Docker: `docker logs com-par-frontend`
- Nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

### 監控建議

**工具**:
- Prometheus + Grafana (指標監控)
- ELK Stack (日誌分析)
- Uptime Kuma (服務可用性監控)

**關鍵指標**:
- API 回應時間 (目標: p95 <= 200ms)
- 錯誤率 (目標: < 1%)
- 服務可用性 (目標: >= 99.9%)
- CPU/記憶體使用率

---

## 備份策略

### 無需資料庫

當前版本不使用持久化儲存,無需備份。

### 未來擴充建議

如果加入資料庫:
- 每日自動備份
- 保留最近 30 天備份
- 異地備份

---

## 疑難排解

### 常見問題

#### 1. 後端無法啟動

**症狀**: `uvicorn main:app` 失敗

**檢查**:
```bash
# 確認 Python 版本
python --version  # 應為 3.11+

# 確認依賴已安裝
pip list

# 檢查埠口是否被佔用
netstat -ano | findstr :8000
```

**解決方法**:
- 重新安裝依賴: `pip install -r requirements.txt`
- 更換埠口: `uvicorn main:app --port 8001`

---

#### 2. 前端無法連接後端

**症狀**: 前端顯示網路錯誤

**檢查**:
```bash
# 確認後端運行中
curl http://localhost:8000/health

# 檢查 CORS 設定
# 查看 backend/main.py 中的 allow_origins
```

**解決方法**:
- 確認 `VITE_API_URL` 設定正確
- 確認後端 CORS 允許前端網域

---

#### 3. Docker 容器無法啟動

**症狀**: `docker-compose up` 失敗

**檢查**:
```bash
# 查看詳細日誌
docker-compose logs

# 檢查埠口衝突
docker-compose ps
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

**解決方法**:
- 移除舊容器: `docker-compose down -v`
- 重新建置: `docker-compose build --no-cache`
- 檢查 docker-compose.yml 語法

---

#### 4. 健康檢查失敗

**症狀**: Docker 容器顯示 unhealthy

**檢查**:
```bash
# 進入容器檢查
docker exec -it com-par-backend /bin/bash
curl localhost:8000/health

# 查看容器日誌
docker logs com-par-backend
```

**解決方法**:
- 增加 start_period: `start_period: 60s`
- 檢查應用啟動時間
- 確認 /health 端點可訪問

---

#### 5. 前端建置失敗

**症狀**: `npm run build` 錯誤

**檢查**:
```bash
# 清除快取
rm -rf node_modules package-lock.json
npm install

# 檢查 Node.js 版本
node --version  # 應為 18.x+

# 檢查環境變數
cat .env.production
```

**解決方法**:
- 更新 Node.js 到 18.x+
- 清除並重新安裝依賴
- 檢查 TypeScript 錯誤

---

## 安全性建議

### 生產環境檢查清單

- [ ] 使用 HTTPS (Let's Encrypt)
- [ ] 設定防火牆規則
- [ ] 限制 CORS 來源
- [ ] 啟用速率限制
- [ ] 定期更新依賴套件
- [ ] 監控錯誤與異常
- [ ] 設定自動備份
- [ ] 使用環境變數儲存敏感資訊
- [ ] 定期安全掃描

---

## 效能優化

### 建議配置

**後端**:
- Workers 數量 = (CPU 核心數 * 2) + 1
- 啟用 Gzip 壓縮
- 配置 CDN (如需要)

**前端**:
- 啟用生產建置 (`npm run build`)
- 配置瀏覽器快取
- 使用 CDN 提供靜態資源
- 啟用 Gzip/Brotli 壓縮

---

## 擴展性考量

### 未來擴充方向

- 加入 Redis 作為快取層
- 使用訊息佇列處理爬取任務
- 水平擴展後端 API (Kubernetes)
- 使用 CDN 加速前端

---

**版本**: v0.1.0  
**最後更新**: 2025-11-16  
**作者**: COM_PAR Team
