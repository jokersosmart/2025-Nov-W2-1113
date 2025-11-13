# 技術堆疊研究 - 社群留言爬蟲工具

**Feature**: 001-social-comment-scraper  
**Research Date**: 2025-11-14  
**Status**: Phase 0 Complete

---

## 決策摘要

### 後端技術堆疊

- **語言/版本**: Python 3.11+
- **理由**: Python 擁有最成熟的網頁爬蟲生態系統(BeautifulSoup4, Selenium, Playwright)、優秀的 Excel 生成函式庫(openpyxl, xlsxwriter)、強大的非同步支援用於速率限制,以及卓越的測試框架(pytest)可實現流暢的 TDD 工作流程。該語言的可讀性符合可維護性要求,並對繁體中文文字處理有一流的支援。
- **考慮過的替代方案**:
  - **Node.js**: 強大的生態系統(Puppeteer, Cheerio)但 Excel 生成函式庫較弱,且非同步測試模式更複雜
  - **Go**: 卓越的效能但爬蟲函式庫不夠成熟,DOM 操作的學習曲線較陡

### 前端技術堆疊

- **框架**: React 18.2+ with TypeScript 5.0+
- **理由**: React 的元件化架構天然支援無障礙功能(react-aria, reach-ui),擁有成熟的測試工具(Jest, React Testing Library)可實現 TDD,並提供優秀的表格編輯函式庫(TanStack Table, AG Grid Community)。TypeScript 增加了型別安全,對維護前後端資料契約至關重要。龐大的生態系統確保長期可維護性。
- **考慮過的替代方案**:
  - **Vue 3**: 學習曲線較簡單但無障礙函式庫生態系統較小
  - **Svelte**: 卓越效能但社群較小,且生產環境驗證的表格編輯方案較少
  - **Vanilla JS**: 需從頭建立太多東西,違反「避免過度工程」限制

### 網頁爬蟲策略

- **方法**: 混合式 - Playwright 無頭瀏覽器處理動態內容 + BeautifulSoup4 處理輕量級解析
- **主要函式庫**:
  - **Playwright 1.40+**(主要爬蟲引擎)
  - **BeautifulSoup4 4.12+**(HTML 解析)
- **反爬蟲機制應對**:
  - 隨機 User Agent(Playwright 的瀏覽器上下文)
  - 可配置速率限制(透過 asyncio.sleep 實現 3-5 秒間隔)
  - 具真實 Chrome/Firefox 指紋的無頭瀏覽器
  - 指數退避的請求重試
  - 偵測到限制時優雅降級
- **失敗模式**:
  - **平台結構變更**: 透過配置檔更新 CSS 選擇器(FR-021)
  - **速率限制偵測**: HTTP 429/異常回應 → 立即停止 + 使用者通知(FR-025)
  - **網路錯誤**: 重試邏輯(3 次嘗試) + 保留部分資料(FR-020a)
  - **認證牆**: 偵測並快速失敗並顯示清楚錯誤訊息(FR-014)
- **理由**: Playwright 提供現代非同步 API,優於 Selenium,處理 Instagram/Facebook 的 JavaScript 密集動態內容,支援多種瀏覽器以提高韌性,並對契約測試有優秀的 TypeScript 支援。BeautifulSoup4 在不需完整瀏覽器時處理輕量級解析(優化)。
- **考慮過的替代方案**:
  - **Selenium**: 較舊的 API,較慢,資源密集度更高
  - **官方 API**: Facebook Graph API 需要應用程式審查,Instagram API 對非商業帳號有嚴格限制,兩者都不適合「任意公開網址」需求
  - **Scrapy**: 對單次作業使用情境過度工程化,無無頭瀏覽器支援

### Excel 生成

- **函式庫**: openpyxl 3.1+
- **功能**:
  - 完整 .xlsx 支援(Office Open XML 格式)
  - 原生 Unicode/UTF-8 支援(完美處理繁體中文)
  - 儲存格格式化(時間戳記、文字換行、欄位寬度)
  - 公式支援(為「生成的回覆」未來擴充做準備)
  - 與 Microsoft Excel、Google Sheets、LibreOffice 相容
- **理由**: openpyxl 是最活躍維護的純 Python Excel 函式庫,無二進位相依性(易於部署),支援 FR-013 所有必要欄位類型,且有優秀的文件。已足夠成熟可用於生產環境(pandas 內部使用)。
- **考慮過的替代方案**:
  - **xlsxwriter**: 更快但僅支援寫入(無法讀取現有檔案,限制未來擴充)
  - **pandas.to_excel()**: 為簡單使用情境增加重量級相依性,對結構化表格輸出來說過度複雜

### 測試框架

- **後端單元測試**: pytest 7.4+ with pytest-asyncio
- **前端單元測試**: Jest 29+ with React Testing Library
- **整合測試**: pytest with Playwright(API + 爬蟲端對端)
- **契約測試**: Pact(pact-python 2.0+)用於 API 契約
- **理由**:
  - **pytest**: 優越的 fixture 系統、參數化測試、非同步支援、優秀的 TDD 人體工學(監視模式、快速回饋)
  - **Jest + RTL**: React 的產業標準,內建 mocking、快照測試、快速平行執行
  - **Playwright 整合**: 重用爬蟲函式庫進行 E2E 測試,降低工具複雜度
  - **Pact**: 確保前後端 API 契約保持同步,對分離架構至關重要
  - 所有工具都支援測試優先開發,具監視模式與快速回饋循環

### 開發工具

- **後端 Linter**: Ruff 0.1+(取代 Flake8/pylint,快 10-100 倍)
- **後端 Formatter**: Black 23.0+(固執己見、零配置)
- **前端 Linter**: ESLint 8.0+ with typescript-eslint, eslint-plugin-jsx-a11y(無障礙)
- **前端 Formatter**: Prettier 3.0+(固執己見,與 ESLint 整合)
- **效能分析器**:
  - **後端**: cProfile + py-spy(生產環境取樣分析器)
  - **前端**: Chrome DevTools Lighthouse, React DevTools Profiler
  - **網路**: Playwright tracing 用於爬蟲瓶頸分析

---

## 最佳實踐摘要

### 速率限制實作

```python
import asyncio
from random import uniform

async def scrape_with_rate_limit(urls, min_delay=3.0, max_delay=5.0):
    results = []
    for url in urls:
        result = await scrape_single(url)
        results.append(result)
        # Random jitter prevents detection patterns
        await asyncio.sleep(uniform(min_delay, max_delay))
    return results
```

使用 `asyncio.Queue` 進行批次處理與並行控制:

```python
async def process_batch(batch_size=100):
    queue = asyncio.Queue()
    semaphore = asyncio.Semaphore(1)  # Only 1 concurrent request
    # Add configurable delay between batches in queue consumer
```

### 無障礙考量

- 使用 **react-aria** 或 **Radix UI** 原語進行鍵盤導航與螢幕閱讀器支援
- 為所有互動元素實作 ARIA 標籤(`aria-label`, `aria-describedby`)
- 確保色彩對比比率 ≥ 4.5:1(使用 `eslint-plugin-jsx-a11y`)
- 為鍵盤使用者提供焦點指示器
- 使用語意 HTML(`<button>`, `<table>`,而非 `<div onclick>`)
- 使用螢幕閱讀器測試(Windows 上的 NVDA,macOS 上的 VoiceOver)
- TanStack Table v8 對可編輯表格有內建 ARIA 支援

### 錯誤處理模式

```python
class ScraperError(Exception):
    """Base scraper exception with user-friendly messages"""
    def __init__(self, technical_msg, user_msg):
        self.technical_msg = technical_msg
        self.user_msg = user_msg  # Display this in UI (FR-014, FR-015, FR-016)

class RateLimitError(ScraperError):
    """Platform detected high request frequency"""
    pass

class InvalidURLError(ScraperError):
    """URL format incorrect or post inaccessible"""
    pass

# Usage in API
try:
    result = await scraper.scrape(url)
except RateLimitError as e:
    return JSONResponse(
        status_code=429,
        content={"error": e.user_msg, "details": e.technical_msg}
    )
```

前端錯誤顯示:

```typescript
// Use React Error Boundary for graceful degradation
// Display user_msg from API errors with retry actions
// Log technical_msg to console for debugging
```

### TDD 工作流程

**後端(pytest 監視模式)**:

```bash
# Terminal 1: Watch mode for instant feedback
pytest --watch --tb=short

# Write failing test first (RED)
def test_scrape_facebook_post():
    result = scraper.scrape("https://facebook.com/...")
    assert result.comments_count == 5

# Implement minimum code (GREEN)
# Refactor while tests pass (REFACTOR)
```

**前端(Jest 監視模式)**:

```bash
# Terminal 1: Watch mode
npm test -- --watch

# RED: Write failing component test
test('displays comment table after scraping', async () => {
  render(<CommentScraper />);
  // Assert table renders
});

# GREEN: Implement component
# REFACTOR: Extract reusable components
```

**整合測試(Playwright)**:

```python
# tests/integration/test_scraping_flow.py
@pytest.mark.integration
async def test_full_scraping_flow():
    # RED: Define end-to-end behavior
    async with async_playwright() as p:
        page = await p.chromium.launch()
        result = await scrape_instagram_post(page, url)
        assert len(result.comments) > 0
    # GREEN: Implement scraper
    # REFACTOR: Extract page object patterns
```

**契約測試**:

```python
# Define contract in tests/contracts/api_contract.py
@pact.given('a valid Facebook post URL')
@pact.upon_receiving('scrape request')
@pact.with_request(method='POST', path='/api/scrape')
@pact.will_respond_with(200, body={...})
def test_scrape_contract():
    # Ensures frontend-backend API compatibility
    pass
```

---

## 額外建議

### 後端框架

- **FastAPI 0.104+**: 現代非同步框架,自動 OpenAPI 文件,優秀的型別提示支援(與 Pact 整合),內建驗證(Pydantic)

### 狀態管理(前端)

- **Zustand 4.4+**: 輕量級,TypeScript 優先,最小樣板程式碼(避免單次作業狀態的 Redux 複雜度)

### HTTP 客戶端(前端)

- **Axios 1.6+**: 成熟,TypeScript 支援,用於錯誤處理的請求/回應攔截器

### CI/CD 建議

- **GitHub Actions**: 公開 repo 免費,優秀的 Python/Node 支援
- **Pre-commit hooks**: 在提交前執行 Black, Ruff, Prettier, ESLint
- **覆蓋率強制執行**: Codecov 整合以強制執行 80% 門檻

### 部署策略

- **後端**: Docker 容器(Python 3.11-slim 基礎映像包含 Playwright 瀏覽器)
- **前端**: 靜態建置(Vite 用於優化的生產環境包)
- **託管**: Vercel/Netlify(前端) + Railway/Fly.io(後端)以求簡單

### 安全性考量

- 前後端分離的 CORS 配置
- URL 輸入驗證(防止 SSRF 攻擊)
- Content Security Policy 標頭
- API 端點速率限制(防止濫用)

---

## 未解決的 NEEDS CLARIFICATION 已解決

所有技術背景中的 NEEDS CLARIFICATION 項目已透過本研究解決:

- **Language/Version**: Python 3.11+(後端) + TypeScript 5.0+ / React 18.2+(前端)
- **Primary Dependencies**:
  - 後端: FastAPI 0.104+, Playwright 1.40+, openpyxl 3.1+, BeautifulSoup4 4.12+
  - 前端: React 18.2+, TypeScript 5.0+, TanStack Table v8, Zustand 4.4+, Axios 1.6+
- **Testing**:
  - 後端: pytest 7.4+ with pytest-asyncio
  - 前端: Jest 29+ with React Testing Library
  - 整合: Playwright
  - 契約: Pact(pact-python 2.0+)

此技術堆疊平衡了成熟度、開發者體驗、測試人體工學,以及社群媒體爬蟲與 Excel 匯出的特定需求,同時為專注的網頁應用程式保持簡單性。
