# COM_PAR — 社群留言爬蟲分析工具

**COM_PAR** 是一個全端社群留言爬蟲與分析平台，透過自動化瀏覽器技術爬取各大社群平台（Instagram、Facebook 等）的公開留言，並提供結構化 API 與直觀的 React 前端介面，方便進行資料分析與應用。

---

## ✨ 功能特色

- 🕷️ **社群留言爬取** — 支援 Instagram、Facebook 等平台公開留言的自動化抓取
- 🔌 **RESTful API** — Python FastAPI 後端，提供完整的爬蟲觸發與資料查詢介面
- 🖥️ **React 前端介面** — 現代化 Vite + React + TypeScript 前端，操作簡便
- 🐳 **Docker 一鍵部署** — Docker Compose 整合前後端，前端自動等待後端健康檢查通過後啟動
- 🧪 **完整測試覆蓋** — pytest（後端）+ Vitest（前端），保障程式碼品質
- 🔒 **程式碼品質工具** — ruff、black（後端）、ESLint、Prettier（前端）

---

## 🏗️ 技術架構

| 層級 | 技術 | 版本 |
|------|------|------|
| **後端語言** | Python | 3.11+ |
| **後端框架** | FastAPI | 最新穩定版 |
| **自動化瀏覽器** | Playwright | 最新穩定版 |
| **前端語言** | TypeScript | 5.0+ |
| **前端框架** | React | 18.2+ |
| **前端建置工具** | Vite | 最新穩定版 |
| **容器化** | Docker + Docker Compose | — |
| **後端測試** | pytest | — |
| **前端測試** | Vitest | — |
| **後端 Linter** | ruff | — |
| **後端 Formatter** | black | — |
| **前端 Linter** | ESLint | — |
| **前端 Formatter** | Prettier | — |

---

## 📋 系統需求

### 方式一（推薦）：Docker

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 或 Docker Engine + Docker Compose

### 方式二：手動安裝

- **Python 3.11+**
- **Node.js 18+** 與 npm
- Playwright 瀏覽器（Chromium / Firefox）

---

## 🚀 快速開始

### 方式一：Docker（推薦）

```bash
# 複製此 repo
git clone https://github.com/jokersosmart/2025-Nov-W2-1113.git
cd 2025-Nov-W2-1113

# 一鍵啟動前後端（首次執行會自動建置 image）
docker-compose up --build
```

啟動後：

- 後端 API：<http://localhost:8000>
- 前端介面：<http://localhost:5173>

> 前端服務會等待後端 health check 通過後才自動啟動。

### 方式二：手動安裝

請參閱 [SETUP.md](./SETUP.md) 取得詳細的環境設置步驟，包含：

- Python 虛擬環境建立
- Playwright 瀏覽器安裝
- Node.js 相依套件安裝
- 開發伺服器啟動方式

---

## 📁 目錄結構

```text
2025-Nov-W2-1113/
├── backend/          # Python FastAPI 後端
│   ├── src/          #   業務邏輯原始碼
│   ├── tests/        #   pytest 測試
│   ├── main.py       #   FastAPI 應用程式進入點
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # React + TypeScript 前端
│   ├── src/          #   元件與頁面原始碼
│   ├── tests/        #   Vitest 測試
│   ├── package.json
│   └── Dockerfile
├── tests/            # 跨層整合測試
├── specs/            # 功能規格文件
├── scripts/          # 輔助腳本（效能測試、燈塔稽核等）
├── docs/             # API 參考、部署指南、使用手冊
├── docker-compose.yml
├── SETUP.md          # 詳細環境設置指南
└── PRE_COMMIT.md     # Pre-commit hooks 說明
```

---

## 🛠️ 開發指令速查

### 後端（`cd backend`）

```bash
# 執行測試
pytest

# 程式碼檢查
ruff check .

# 程式碼格式化
black .

# 啟動開發伺服器（熱重載）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端（`cd frontend`）

```bash
# 啟動開發伺服器
npm run dev

# 程式碼檢查
npm run lint

# 程式碼格式化
npm run format

# 執行測試
npm test
```

---

## 📚 相關文件

| 文件 | 說明 |
|------|------|
| [SETUP.md](./SETUP.md) | 完整環境設置與安裝步驟 |
| [PRE_COMMIT.md](./PRE_COMMIT.md) | Pre-commit hooks 設定說明 |
| [docs/api-reference.md](./docs/api-reference.md) | API 端點參考文件 |
| [docs/deploy.md](./docs/deploy.md) | 部署指南 |
| [docs/user-guide.md](./docs/user-guide.md) | 使用者操作手冊 |

---

## Docker Container 名稱

| 服務 | Container Name | Port |
|------|---------------|------|
| 後端 | `com_par_backend` | 8000 |
| 前端 | `com_par_frontend` | 5173 |
