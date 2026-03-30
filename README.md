# 社群留言爬蟲工具 (COM_PAR)

一款全端網頁應用程式，讓非技術背景使用者也能輕鬆從 **Instagram** 與
**Facebook** 公開貼文爬取留言資料、線上編輯，並匯出為 Excel 檔案。

---

## 功能說明

- **爬取留言**：貼上任意 Facebook / Instagram 公開貼文網址，即可自動擷取
  貼文資訊與所有第一層留言（不含留言下的回覆串）
- **即時進度**：分批爬取並顯示進度條，可隨時取消並保留已爬取的資料
- **線上編輯**：在表格中直接填寫回覆窗口、回覆內容、客戶確認/修改處等欄位，或勾選刪除不需要的留言列
- **匯出 Excel**：一鍵下載 `.xlsx` 檔案，檔名含平台識別符與時間戳記（例：`facebook_comments_20251113_143052.xlsx`）
- **友善錯誤提示**：針對無效網址、貼文不存在、網路中斷、速率限制等情況提供清楚的錯誤訊息

---

## 技術架構

| 層級 | 技術 | 埠號 |
| ---- | ---- | ---- |
| 後端 API | Python 3.11+ · FastAPI · Playwright | 8000 |
| 前端 UI | Node.js 18+ · Vite · React · TypeScript | 5173 |
| 容器化 | Docker · Docker Compose | — |

---

## 系統需求

- **Python 3.11+**（手動啟動後端時需要）
- **Node.js 18+**（手動啟動前端時需要）
- **Docker & Docker Compose**（使用容器化方式時需要，建議使用）

---

## 快速開始

### 方式一：Docker（推薦）

```bash
docker-compose up
```

啟動後：

- 前端介面：<http://localhost:5173>
- 後端 API：<http://localhost:8000>

Container 名稱：`com_par_backend` / `com_par_frontend`

### 方式二：手動啟動

請參考 [SETUP.md](SETUP.md) 的詳細安裝步驟。

#### 後端

```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
playwright install chromium firefox  # 安裝爬蟲所需瀏覽器（Chromium 與 Firefox）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

---

## 專案結構

```text
.
├── backend/          # Python FastAPI 後端
│   ├── src/          # 應用程式原始碼（api / models / services / utils）
│   ├── tests/        # 後端測試（unit / integration / contract / performance）
│   ├── main.py       # 應用程式進入點
│   └── requirements.txt
├── frontend/         # Vite + React + TypeScript 前端
│   ├── src/          # 應用程式原始碼（components / pages / services / types）
│   └── tests/        # 前端測試（unit / integration / accessibility / lighthouse）
├── scripts/          # 輔助腳本（Lighthouse、負載測試）
├── specs/            # 功能規格書
│   └── 001-social-comment-scraper/
├── docs/             # 補充文件（API 參考、部署指南、使用手冊）
├── docker-compose.yml
├── SETUP.md          # 環境安裝詳細步驟
└── PRE_COMMIT.md     # Pre-commit hooks 設置說明
```

---

## 開發工作流程

### 後端

```bash
cd backend
# 啟動虛擬環境後執行：
uvicorn main:app --reload --host 0.0.0.0 --port 8000  # 開發伺服器
pytest --tb=short                                      # 執行測試
ruff check .                                           # Linter
black .                                                # Formatter
```

### 前端

```bash
cd frontend
npm run dev      # 開發伺服器
npm test         # 執行測試
npm run lint     # Linter
npm run format   # Formatter
```

---

## 相關文件

- [SETUP.md](SETUP.md) — 環境安裝與設定詳細步驟
- [PRE_COMMIT.md](PRE_COMMIT.md) — Pre-commit hooks 設置指南
- [docs/api-reference.md](docs/api-reference.md) — API 參考文件
- [docs/user-guide.md](docs/user-guide.md) — 使用手冊
- [docs/deploy.md](docs/deploy.md) — 部署指南
- [specs/001-social-comment-scraper/spec.md][spec] — 功能規格書

[spec]: specs/001-social-comment-scraper/spec.md
