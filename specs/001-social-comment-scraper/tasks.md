# 實作任務清單 - 社群留言爬蟲工具

**Feature**: 001-social-comment-scraper
**Generated**: 2025-11-14
**Based on**: spec.md, plan.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

---

## 概覽

本任務清單基於 TDD 原則組織,每個任務必須先寫測試(RED),再實作(GREEN),最後重構(REFACTOR)。任務按使用者故事優先級(P1 → P2 → P3)分組,確保 MVP 可獨立交付。

**MVP 範圍**: Phase 3 (使用者故事 1 - 爬取功能)
**完整交付**: Phase 5 完成後包含所有三個使用者故事
**總任務數**: 62

---

## 相依性圖

```text
Phase 1 (Setup)
    ↓
Phase 2 (Foundational - 阻塞性前置條件)
    ↓
Phase 3 (US1: 爬取功能 - MVP) ──┐
    ↓                            │
Phase 4 (US2: 編輯功能)          │ 獨立可並行
    ↓                            │
Phase 5 (US3: 匯出功能)          │
    ↓                            │
Phase 6 (Polish & 跨功能) ←──────┘
```

**使用者故事完成順序**: US1 → US2 → US3 (嚴格依賴)
**可並行執行**: 同一 Phase 內標記 [P] 的任務

---

## Phase 1: 專案設置與基礎架構

**目標**: 建立可執行的開發環境與 CI/CD 管道
**測試策略**: 環境驗證測試(pytest/Jest 可執行,CI 通過)

### 任務清單 - 設置

- [x] T001 建立專案目錄結構 backend/{src,tests}/ 與 frontend/{src,tests}/
- [x] T002 [P] 配置後端環境 requirements.txt 與 Python 3.11+ venv
- [x] T003 [P] 配置前端環境 package.json 與 Node.js 18+
- [x] T004 [P] 安裝 Playwright 瀏覽器 (chromium, firefox) 於後端
- [x] T005 [P] 配置程式碼品質工具 (Ruff, Black, ESLint, Prettier)
- [x] T006 設置 GitHub Actions CI workflow (.github/workflows/ci.yml)
- [x] T007 配置 pre-commit hooks (測試與格式化)
- [x] T008 驗證 CI 管道通過 (後端與前端測試執行成功)

**並行執行範例**:

```bash
# 同時執行 T002, T003, T004, T005 (不同環境,無相依性)
Terminal 1: cd backend; python -m venv venv; pip install -r requirements.txt
Terminal 2: cd frontend; npm install
Terminal 3: cd backend; playwright install chromium firefox
Terminal 4: cd backend; pip install ruff black; cd ../frontend; npm install --save-dev eslint prettier
```

**獨立測試標準**: CI 管道成功執行所有測試且程式碼品質檢查通過

---

## Phase 2: 基礎模型與共用服務

**目標**: 實作所有使用者故事共用的基礎元件
**測試策略**: 單元測試覆蓋率 100% (阻塞性元件)

### 任務清單 - 基礎元件

- [x] T009 [P] 定義 Post Pydantic 模型於 backend/src/models/post.py
- [x] T010 [P] 定義 Comment Pydantic 模型於 backend/src/models/comment.py
- [x] T011 [P] 定義 TypeScript Post interface 於 frontend/src/types/post.ts
- [x] T012 [P] 定義 TypeScript Comment interface 於 frontend/src/types/comment.ts
- [x] T013 實作速率限制服務 backend/src/services/rate_limiter.py
- [x] T014 實作重試邏輯服務 backend/src/services/retry_handler.py
- [x] T015 實作 URL 驗證工具 backend/src/utils/url_validator.py
- [x] T016 [P] 建立 FastAPI 應用程式於 backend/main.py 與錯誤處理中介軟體
- [x] T017 [P] 建立 Zustand store 於 frontend/src/services/store.ts

**並行執行範例**:

```bash
# T009-T012 可並行 (不同檔案)
Terminal 1: # T009 Post model
Terminal 2: # T010 Comment model
Terminal 3: # T011 TypeScript Post
Terminal 4: # T012 TypeScript Comment

# T016-T017 可並行 (後端與前端獨立)
Terminal 1: # T016 FastAPI app
Terminal 2: # T017 Zustand store
```

**獨立測試標準**: 所有模型與服務通過單元測試,覆蓋率 100%

---

## Phase 3: 使用者故事 1 - 爬取單一貼文留言 (P1 - MVP)

**目標**: 實作核心爬蟲功能,使用者能輸入網址並查看爬取結果

**獨立測試**: 使用者提供 Facebook/Instagram 公開貼文網址,系統成功抓取並顯示所有第一層留言

**測試策略**:

- 契約測試先行 (定義 API 行為)
- 單元測試覆蓋爬蟲邏輯
- 整合測試驗證完整流程
- E2E 測試涵蓋所有驗收情境

### 任務清單 - US1 後端

- [x] T018 [P] [US1] 撰寫契約測試 POST /api/scrape 於 backend/tests/contract/test_scrape_contract.py
- [x] T019 [P] [US1] 撰寫契約測試 GET /api/scrape/{id}/progress 於 backend/tests/contract/test_progress_contract.py
- [x] T020 [P] [US1] 撰寫契約測試 POST /api/scrape/{id}/cancel 於 backend/tests/contract/test_cancel_contract.py
- [x] T021 [US1] 實作 Facebook 爬蟲服務 backend/src/services/facebook_scraper.py
- [x] T022 [US1] 實作 Instagram 爬蟲服務 backend/src/services/instagram_scraper.py
- [x] T023 [US1] 實作分批處理服務 backend/src/services/batch_processor.py
- [x] T024 [US1] 實作 POST /api/scrape 端點於 backend/src/api/scrape.py
- [x] T025 [US1] 實作 GET /api/scrape/{id}/progress 端點於 backend/src/api/scrape.py
- [x] T026 [US1] 實作 POST /api/scrape/{id}/cancel 端點於 backend/src/api/scrape.py

### 任務清單 - US1 前端

- [x] T027 [P] [US1] 實作 URL 輸入元件 frontend/src/components/UrlInput.tsx
- [x] T028 [P] [US1] 實作爬取按鈕元件 frontend/src/components/ScrapeButton.tsx
- [x] T029 [P] [US1] 實作進度指示器元件 frontend/src/components/ProgressIndicator.tsx
- [x] T030 [P] [US1] 實作留言表格元件 frontend/src/components/CommentTable.tsx
- [x] T031 [P] [US1] 實作錯誤訊息元件 frontend/src/components/ErrorMessage.tsx
- [x] T032 [US1] 實作 API 服務 frontend/src/services/apiService.ts
- [x] T033 [US1] 實作主頁面 frontend/src/pages/HomePage.tsx
- [x] T034 [US1] 撰寫 E2E 測試涵蓋 4 個驗收情境於 frontend/tests/integration/test_scraping_flow.test.tsx

**並行執行範例**:

```bash
# 契約測試可並行
Terminal 1: # T018
Terminal 2: # T019
Terminal 3: # T020

# 前端元件可並行
Terminal 1: # T027 UrlInput
Terminal 2: # T028 ScrapeButton
Terminal 3: # T029 ProgressIndicator
Terminal 4: # T030 CommentTable
Terminal 5: # T031 ErrorMessage
```

**獨立測試標準**:

- 完整爬取流程通過 E2E 測試
- 涵蓋 spec.md 使用者故事 1 的 4 個驗收情境
- 單元測試覆蓋率 >= 80%,關鍵路徑 100%

---

## Phase 4: 使用者故事 2 - 線上編輯留言資料 (P2)

**目標**: 實作表格編輯與刪除功能

**獨立測試**: 使用者完成爬取後,能編輯欄位並刪除留言列

**測試策略**:

- 元件測試驗證編輯互動
- 狀態管理測試確保資料一致性
- E2E 測試涵蓋所有驗收情境

### 任務清單 - US2

- [x] T035 [P] [US2] 實作可編輯儲存格元件 frontend/src/components/EditableCell.tsx
- [x] T036 [P] [US2] 擴充 CommentTable 支援勾選與刪除 frontend/src/components/CommentTable.tsx
- [x] T037 [US2] 擴充 Zustand store 支援編輯與刪除操作 frontend/src/services/store.ts
- [x] T038 [US2] 撰寫 E2E 測試涵蓋 4 個驗收情境於 frontend/tests/integration/test_editing_flow.test.ts

**並行執行範例**:

```bash
# T035-T036 可並行 (不同元件)
Terminal 1: # T035 EditableCell
Terminal 2: # T036 CommentTable extension
```

**獨立測試標準**:

- 編輯與刪除流程通過 E2E 測試
- 涵蓋 spec.md 使用者故事 2 的 4 個驗收情境
- 資料不保留行為正確驗證 (重新整理頁面)

---

## Phase 5: 使用者故事 3 - 匯出為 Excel 檔案 (P3)

**目標**: 實作 Excel 匯出功能

**獨立測試**: 使用者完成編輯後,點擊匯出能下載正確格式的 Excel 檔案

**測試策略**:

- 契約測試定義 API 行為
- 單元測試驗證 Excel 生成邏輯
- 整合測試驗證檔案格式正確性
- E2E 測試涵蓋所有驗收情境

### 任務清單 - US3 後端

- [x] T039 [US3] 撰寫契約測試 POST /api/export 於 backend/tests/contract/test_export_contract.py
- [x] T040 [US3] 實作 Excel 生成服務 backend/src/services/excel_generator.py
- [x] T041 [US3] 實作 POST /api/export 端點於 backend/src/api/export.py

### 任務清單 - US3 前端

- [x] T042 [P] [US3] 實作匯出按鈕元件 frontend/src/components/ExportButton.tsx
- [x] T043 [US3] 擴充 API 服務支援匯出 frontend/src/services/apiService.ts
- [x] T044 [US3] 撰寫 E2E 測試涵蓋 4 個驗收情境於 frontend/tests/integration/test_export_flow.test.ts

**並行執行範例**:

```bash
# T042 可與後端任務並行
Terminal 1: # T042 ExportButton (前端)
Terminal 2: # T040 Excel generator (後端)
```

**獨立測試標準**:

- 匯出流程通過 E2E 測試
- 涵蓋 spec.md 使用者故事 3 的 4 個驗收情境
- Excel 檔案格式驗證 (可用 openpyxl 開啟且欄位正確)
- 檔名格式正確 (platform_comments_timestamp.xlsx)

---

## Phase 6: Polish & 跨功能關注點

**目標**: 完成錯誤處理、效能優化、無障礙性與文件

**測試策略**:

- 負載測試驗證效能目標
- 無障礙測試確保 WCAG 2.1 AA 合規
- 手動測試所有邊界情況

### 任務清單 - 錯誤處理

- [x] T045 [P] 實作統一錯誤處理中介軟體 backend/src/api/middleware/error_handler.py
- [x] T046 [P] 實作速率限制偵測邏輯 backend/src/services/scrapers (擴充)
- [x] T047 [P] 實作網路重試邏輯 backend/src/services/retry_handler.py (擴充)
- [x] T048 撰寫邊界情況整合測試 backend/tests/integration/test_edge_cases.py

### 任務清單 - 效能與無障礙

- [x] T049 執行負載測試驗證 API p95 <= 200ms 使用 Locust
- [x] T050 執行 Lighthouse 稽核確保前端效能與無障礙性 >= 95 分
- [x] T051 [P] 使用 NVDA/VoiceOver 進行螢幕閱讀器測試
- [x] T052 [P] 驗證鍵盤導航完整性 (Tab, Enter, Escape)
- [x] T053 驗證色彩對比比率 >= 4.5:1

### 任務清單 - 文件與部署

- [x] T054 [P] 撰寫使用者操作手冊 docs/user-guide.md
- [x] T055 [P] 撰寫 API 文件 (OpenAPI 自動生成 + 補充說明)
- [x] T056 [P] 建立 Docker Compose 配置 docker-compose.yml
- [x] T057 撰寫部署文件 docs/deploy.md
- [x] T058 實作健康檢查端點 GET /health 於 backend/main.py
- [ ] T059 執行最終憲章合規檢查 (代碼品質、測試、UX、效能)
- [ ] T060 驗證所有 27 個功能需求 (FR-001 to FR-027) 已實作
- [ ] T061 驗證所有 11 個成功標準 (SC-001 to SC-011) 已達成
- [ ] T062 生成最終測試覆蓋率報告並確保 >= 80%

**並行執行範例**:

```bash
# 錯誤處理任務可並行
Terminal 1: # T045 Error middleware
Terminal 2: # T046 Rate limit detection
Terminal 3: # T047 Retry logic

# 文件任務可並行
Terminal 1: # T054 User guide
Terminal 2: # T055 API docs
Terminal 3: # T056 Docker Compose
```

**獨立測試標準**:

- 所有邊界情況正確處理
- 效能目標達成 (API p95 <= 200ms, UI <= 100ms)
- 無障礙評分 >= 95 (Lighthouse)
- 所有文件完整且易於理解
- 憲章所有原則通過驗證

---

## 實作策略

### MVP 優先交付

**Phase 3 完成即可交付 MVP**,包含核心價值:

- ✅ 爬取 Facebook/Instagram 公開貼文留言
- ✅ 顯示貼文資訊與留言表格
- ✅ 進度追蹤與取消功能
- ✅ 錯誤處理與友善訊息

**驗證標準**:

- 使用者可完成 spec.md 使用者故事 1 的所有驗收情境
- 單元測試覆蓋率 >= 80%
- 關鍵路徑覆蓋率 100% (爬蟲邏輯、API 端點)

### 漸進式交付

- **Phase 4**: 增加編輯功能,提升資料品質
- **Phase 5**: 增加匯出功能,完整交付價值鏈
- **Phase 6**: 打磨體驗,確保生產就緒

### TDD 紀律

每個任務必須遵循:

1. **RED**: 先寫測試,確認失敗
2. **GREEN**: 實作最小程式碼使測試通過
3. **REFACTOR**: 重構程式碼,保持測試通過

**監視模式**:

```bash
# 後端
pytest --watch --tb=short

# 前端
npm test -- --watch
```

---

## 任務統計

| Phase | 任務數 | 使用者故事 | 可並行任務 |
|-------|--------|-----------|-----------|
| Phase 1: 設置 | 8 | - | 4 |
| Phase 2: 基礎 | 9 | - | 6 |
| Phase 3: US1 爬取 | 17 | P1 | 8 |
| Phase 4: US2 編輯 | 4 | P2 | 2 |
| Phase 5: US3 匯出 | 6 | P3 | 2 |
| Phase 6: Polish | 18 | - | 10 |
| **總計** | **62** | **3** | **32 (52%)** |

**預估時程**:

- MVP (Phase 1-3): 約 8-10 工作天
- 完整交付 (Phase 1-6): 約 15-18 工作天

---

## 下一步

1. ✅ 審查任務分解是否完整
2. ➡️ 開始 Phase 1: T001 (專案初始化)
3. ➡️ 遵循 TDD 流程: RED → GREEN → REFACTOR
4. ➡️ 每個任務完成後提交 PR,通過 CI 檢查後合併
5. ➡️ 持續追蹤測試覆蓋率,確保 >= 80%

**準備好開始實作了嗎?** 🚀

---

## 附錄: 任務 ID 對照表

快速查找任務:

- **T001-T008**: Phase 1 設置
- **T009-T017**: Phase 2 基礎
- **T018-T034**: Phase 3 US1 爬取 (MVP)
- **T035-T038**: Phase 4 US2 編輯
- **T039-T044**: Phase 5 US3 匯出
- **T045-T062**: Phase 6 Polish

**關鍵里程碑**:

- T008 完成: 開發環境就緒
- T017 完成: 基礎模型與服務就緒
- T034 完成: **MVP 可交付** 🎯
- T038 完成: 編輯功能完成
- T044 完成: 完整功能鏈完成
- T062 完成: **生產就緒** 🚀
