# COM_PAR — 社群平台留言爬蟲工具

一款專為**非技術背景使用者**設計的線上留言爬取工具，支援 **Facebook** 與 **Instagram** 公開貼文。只需貼上貼文網址，即可自動爬取所有留言、線上編輯，並匯出為 Excel 檔案。

---

## 功能特色

- 🔗 **一鍵爬取**：輸入貼文網址，自動抓取所有第一層留言（留言時間、留言者 ID、留言內容）
- 📊 **線上表格瀏覽與編輯**：直接在瀏覽器中編輯「回覆窗口」、「回覆內容」、「客戶確認/修改處」等欄位，或刪除不需要的留言列
- 📥 **匯出 Excel 檔案**：一鍵下載 `.xlsx`，檔名自動帶入平台名稱與時間戳記（如 `facebook_comments_20251113_143052.xlsx`）
- 🛡️ **保守爬取策略**：每批次間隔 3–5 秒，避免觸發平台速率限制；支援中途取消並保留已爬取資料
- 👤 **無需登入**：任何人透過網址即可使用，不需帳號或程式背景

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端 | Python 3.11+、FastAPI、Playwright、uvicorn |
| 前端 | Node.js 18+、Vite、TypeScript |
| 容器化 | Docker、Docker Compose |
| 測試 | pytest（後端）、Vitest / Jest（前端） |
| 程式碼品質 | ruff、black、ESLint、Prettier、pre-commit |

---

## 快速開始

### 方式一：Docker（推薦）

確認已安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)，然後執行：

```bash
docker compose up --build
```

啟動後：
- 前端：http://localhost:5173
- 後端 API：http://localhost:8000

### 方式二：本地開發

詳細安裝步驟請參考 [SETUP.md](./SETUP.md)。以下為快速摘要：

**後端**

```bash
cd backend
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium firefox
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**前端**

```bash
cd frontend
npm install
npm run dev
```

---

## 專案結構

```
2025-Nov-W2-1113/
├── backend/                  # Python FastAPI 後端
│   ├── main.py               # 應用程式進入點
│   ├── src/                  # 主要業務邏輯（爬蟲、API 路由）
│   ├── tests/                # 後端測試
│   ├── requirements.txt      # Python 相依套件
│   └── Dockerfile
├── frontend/                 # 前端（Vite + TypeScript）
│   ├── src/                  # 元件與頁面
│   ├── tests/                # 前端測試
│   ├── package.json
│   └── Dockerfile
├── specs/                    # 功能規格文件
│   └── 001-social-comment-scraper/
│       ├── spec.md           # 完整功能規格與驗收情境
│       └── plan.md           # 開發計劃
├── docs/                     # 補充文件
├── scripts/                  # 工具腳本
├── SETUP.md                  # 環境設置指南
├── docker-compose.yml        # Docker 容器編排設定
└── .pre-commit-config.yaml   # pre-commit 鉤子設定
```

---

## 開發指令

### 後端

```bash
cd backend

# 執行測試
pytest

# 執行 linter
ruff check .

# 執行 formatter
black .

# 啟動開發伺服器（自動重載）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend

# 執行測試
npm test

# 執行 linter
npm run lint

# 執行 formatter
npm run format

# 啟動開發伺服器（port 5173）
npm run dev
```

### 如何修改爬蟲邏輯

爬蟲核心邏輯位於 `backend/src/`，修改時的主要切入點：

- **新增平台支援**：在爬蟲模組中新增對應的解析邏輯
- **調整爬取速率**：修改批次間隔時間（預設 3–5 秒）
- **調整 Excel 欄位**：修改匯出模組中的欄位定義
- **調整前端 UI**：修改 `frontend/src/` 中的元件與頁面

---

## 文件

- [SETUP.md](./SETUP.md)：完整環境設置指南
- [specs/001-social-comment-scraper/spec.md](./specs/001-social-comment-scraper/spec.md)：功能規格與驗收情境
- [specs/001-social-comment-scraper/plan.md](./specs/001-social-comment-scraper/plan.md)：開發計劃與任務清單
