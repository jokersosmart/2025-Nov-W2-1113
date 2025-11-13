# 快速入門指南 - 社群留言爬蟲工具

**Feature**: 001-social-comment-scraper  
**Date**: 2025-11-14  
**Target Audience**: 開發者、新進團隊成員

---

## 專案概述

本專案為一個線上 Web 應用程式,讓非技術背景使用者能透過貼上網址,從 Facebook 與 Instagram 公開貼文爬取留言資料,進行線上編輯,並匯出為 Excel 檔案。

**核心價值**:

- 🎯 簡化資料收集流程(無需程式背景)
- 📊 支援線上編輯與標註(回覆窗口、回覆內容、客戶備註)
- 📁 一鍵匯出 Excel 檔案供後續分析

**技術堆疊**:

- 後端: Python 3.11+ | FastAPI | Playwright | openpyxl
- 前端: React 18.2+ | TypeScript 5.0+ | TanStack Table | Zustand
- 測試: pytest | Jest | Pact

---

## 快速啟動

### 前置需求

- Python 3.11+ (後端)
- Node.js 18+ (前端)
- Git
- 現代瀏覽器(Chrome, Firefox, Safari, Edge 最新兩個版本)

### 1. 取得專案

```bash
git clone <repository-url>
cd COM_PAR
git checkout 001-social-comment-scraper
```

### 2. 後端設置

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 安裝相依套件
pip install -r requirements.txt

# 安裝 Playwright 瀏覽器
playwright install chromium firefox

# 執行測試(TDD 必要步驟)
pytest --tb=short

# 啟動開發伺服器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**後端將運行於**: `http://localhost:8000`  
**API 文件**: `http://localhost:8000/docs`(自動生成的 OpenAPI 文件)

### 3. 前端設置

```bash
# 開啟新的終端機視窗,進入前端目錄
cd frontend

# 安裝相依套件
npm install

# 執行測試
npm test

# 啟動開發伺服器
npm run dev
```

**前端將運行於**: `http://localhost:5173`(Vite 預設端口)

---

## 專案結構

```text
COM_PAR/
├── backend/
│   ├── src/
│   │   ├── models/          # Post, Comment Pydantic 模型
│   │   ├── services/        # 爬蟲邏輯、速率控制、Excel 生成
│   │   ├── api/             # FastAPI 路由 (/scrape, /export)
│   │   └── utils/           # 輔助函式(URL 驗證、時間格式化)
│   ├── tests/
│   │   ├── unit/            # 單元測試(80%+ 覆蓋率)
│   │   ├── integration/     # 整合測試(API + 爬蟲)
│   │   └── contract/        # Pact 契約測試
│   ├── requirements.txt     # Python 相依套件
│   └── main.py              # FastAPI 應用程式進入點
│
├── frontend/
│   ├── src/
│   │   ├── components/      # UI 元件(輸入框、按鈕、表格、進度條)
│   │   ├── pages/           # 主頁面(單頁應用程式)
│   │   ├── services/        # API 呼叫、狀態管理(Zustand)
│   │   └── styles/          # 設計系統、可重用樣式
│   ├── tests/
│   │   ├── unit/            # 元件單元測試
│   │   └── integration/     # 端對端流程測試
│   ├── package.json         # npm 相依套件
│   └── vite.config.ts       # Vite 配置
│
└── specs/001-social-comment-scraper/
    ├── spec.md              # 功能規格(已完成釐清)
    ├── plan.md              # 實作計畫(本文件所在位置)
    ├── research.md          # 技術堆疊研究
    ├── data-model.md        # 資料模型定義
    ├── contracts/           # API 契約(OpenAPI)
    └── quickstart.md        # 本文件
```

---

## 開發工作流程(TDD)

本專案**強制採用 TDD**(憲章原則 II),遵循紅—綠—重構循環:

### 後端 TDD 流程

```bash
# 1. 開啟監視模式(自動重新執行測試)
pytest --watch --tb=short

# 2. 寫測試(RED)
# tests/unit/test_scraper.py
def test_scrape_facebook_post_returns_comments():
    scraper = FacebookScraper()
    result = scraper.scrape("https://facebook.com/example/posts/123")
    assert len(result.comments) > 0
    assert result.post.platform == "facebook"

# 3. 執行測試,確認失敗(RED)
# 4. 實作最小程式碼使測試通過(GREEN)
# src/services/facebook_scraper.py
class FacebookScraper:
    def scrape(self, url: str) -> ScrapeResult:
        # 實作爬蟲邏輯...
        return ScrapeResult(...)

# 5. 執行測試,確認通過(GREEN)
# 6. 重構程式碼,保持測試通過(REFACTOR)
```

### 前端 TDD 流程

```bash
# 1. 開啟監視模式
npm test -- --watch

# 2. 寫測試(RED)
# tests/unit/CommentTable.test.tsx
test('renders comment table with edit functionality', () => {
  render(<CommentTable comments={mockComments} />);
  const firstComment = screen.getByText('這個產品真的很棒!');
  expect(firstComment).toBeInTheDocument();
});

# 3. 實作元件(GREEN)
# src/components/CommentTable.tsx
export function CommentTable({ comments }: Props) {
  return <TanStackTable data={comments} ... />;
}

# 4. 重構,保持測試通過(REFACTOR)
```

---

## 常見開發任務

### 新增 API 端點

1. **寫契約測試**(RED):

   ```python
   # tests/contract/test_api_contract.py
   @pact.given('a valid post URL')
   @pact.upon_receiving('scrape request')
   def test_scrape_endpoint_contract():
       # 定義請求/回應契約...
   ```

2. **寫整合測試**(RED):

   ```python
   # tests/integration/test_scrape_api.py
   async def test_scrape_endpoint_returns_comments():
       response = await client.post("/api/scrape", json={"post_url": "...", "platform": "facebook"})
       assert response.status_code == 200
   ```

3. **實作端點**(GREEN):

   ```python
   # src/api/scrape.py
   @router.post("/scrape")
   async def start_scraping(request: ScrapeRequest):
       # 實作...
   ```

### 新增前端元件

1. **寫元件測試**(RED):

   ```typescript
   test('button triggers scraping action', async () => {
     render(<ScrapeButton url="..." />);
     fireEvent.click(screen.getByRole('button'));
     // Assert API called...
   });
   ```

2. **實作元件**(GREEN):

   ```typescript
   export function ScrapeButton({ url }: Props) {
     // 實作...
   }
   ```

### 執行程式碼品質檢查

```bash
# 後端
cd backend
ruff check .           # Linter
black . --check        # Formatter 檢查
black .                # 自動格式化

# 前端
cd frontend
npm run lint           # ESLint
npm run format:check   # Prettier 檢查
npm run format         # 自動格式化
```

---

## 測試指南

### 執行所有測試

```bash
# 後端
cd backend
pytest                         # 所有測試
pytest tests/unit/             # 僅單元測試
pytest tests/integration/      # 僅整合測試
pytest --cov=src --cov-report=html  # 覆蓋率報告

# 前端
cd frontend
npm test                       # 所有測試
npm test -- --coverage         # 覆蓋率報告
```

### 測試覆蓋率目標

- 單元測試: **最低 80%**(憲章要求)
- 關鍵路徑: **100%**(爬蟲邏輯、Excel 生成、API 端點)

### 契約測試

```bash
# 後端生成 Pact 檔案
cd backend
pytest tests/contract/ --pact

# 前端驗證 Pact 契約
cd frontend
npm run test:contract
```

---

## 效能目標

根據憲章原則 IV 與規格成功標準:

- API 回應時間 p95 <= 200ms
- UI 互動響應時間 <= 100ms
- 爬取少於 100 則留言時間 <= 60 秒(含 3-5 秒速率控制間隔)

### 效能測試

```bash
# 後端負載測試(使用 locust)
cd backend
locust -f tests/load/locustfile.py --host=http://localhost:8000

# 前端效能分析
# 使用 Chrome DevTools Lighthouse
# 或 React DevTools Profiler
```

---

## 無障礙(WCAG 2.1 AA)

本專案遵守 WCAG 2.1 AA 標準(憲章原則 III):

### 開發檢查清單

- [ ] 所有互動元素可透過鍵盤操作(Tab, Enter, Escape)
- [ ] 使用語意 HTML(`<button>`, `<table>`,非 `<div onclick>`)
- [ ] ARIA 標籤完整(`aria-label`, `aria-describedby`)
- [ ] 色彩對比比率 ≥ 4.5:1
- [ ] 焦點指示器清楚可見
- [ ] 錯誤訊息與螢幕閱讀器相容

### 無障礙測試工具

```bash
# 前端 - ESLint 無障礙檢查
npm run lint  # 包含 eslint-plugin-jsx-a11y

# 手動測試
# 1. 僅使用鍵盤操作整個流程
# 2. 使用螢幕閱讀器(Windows: NVDA, macOS: VoiceOver)
# 3. Chrome DevTools Lighthouse 無障礙稽核
```

---

## 常見問題排解

### Q1: Playwright 瀏覽器安裝失敗

```bash
# 確認 Python 虛擬環境已啟動
# 重新安裝瀏覽器
playwright install --force chromium firefox
```

### Q2: 前端無法連接後端 API

- 確認後端運行於 `http://localhost:8000`
- 檢查 CORS 配置(frontend/.env 中的 VITE_API_URL)
- 確認防火牆未阻擋端口 8000

### Q3: 測試覆蓋率不足 80%

```bash
# 產生覆蓋率報告並查看未覆蓋區域
pytest --cov=src --cov-report=html
# 開啟 htmlcov/index.html 查看詳細報告
```

### Q4: 速率限制導致爬蟲失敗

- 檢查 `config.py` 中的 `RATE_LIMIT_MIN_DELAY` 與 `RATE_LIMIT_MAX_DELAY`
- 預設為 3-5 秒,可根據實際情況調整(但不建議低於 3 秒)

---

## 下一步

1. **閱讀功能規格**: `specs/001-social-comment-scraper/spec.md`
2. **理解資料模型**: `specs/001-social-comment-scraper/data-model.md`
3. **檢視 API 契約**: `specs/001-social-comment-scraper/contracts/openapi.yaml`
4. **執行 `/speckit.tasks`**: 生成任務分解,開始實作第一個任務

---

## 資源連結

### 官方文件

- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright Python](https://playwright.dev/python/)
- [React](https://react.dev/)
- [TanStack Table](https://tanstack.com/table/latest)
- [pytest](https://docs.pytest.org/)
- [Jest](https://jestjs.io/)

### 內部文件

- [憲章](../../.specify/memory/constitution.md)
- [技術堆疊研究](./research.md)
- [實作計畫](./plan.md)

---

**準備好開始了嗎?** 執行測試,確認環境設置正確,然後開始 TDD 之旅! 🚀
