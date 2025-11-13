# Implementation Plan: 社群平台留言爬蟲工具

**Branch**: `001-social-comment-scraper` | **Date**: 2025-11-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-social-comment-scraper/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

開發一個線上 Web 應用程式，讓非技術背景使用者能透過貼上網址，從 Facebook 與 Instagram 公開貼文爬取第一層留言資料。系統提供線上編輯功能（回覆窗口、回覆內容、客戶確認/修改處），並支援將整理後的資料匯出為 Excel 檔案（.xlsx 格式）。核心技術方案基於 Web 爬蟲模式，實作保守速率控制（3-5 秒間隔）以避免平台限制，並提供進度追蹤與取消機制。系統無需使用者登入，為單次作業流程（爬取→編輯→匯出），不保存歷史記錄。

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+(後端) + TypeScript 5.0+ / React 18.2+(前端)  
**Primary Dependencies**:

- 後端: FastAPI 0.104+, Playwright 1.40+, openpyxl 3.1+, BeautifulSoup4 4.12+
- 前端: React 18.2+, TypeScript 5.0+, TanStack Table v8, Zustand 4.4+, Axios 1.6+

**Storage**: 無需持久化儲存(瀏覽器記憶體暫存,關閉即清除)  
**Testing**:

- 後端: pytest 7.4+ with pytest-asyncio
- 前端: Jest 29+ with React Testing Library
- 整合: Playwright(API + 爬蟲 E2E)
- 契約: Pact(pact-python 2.0+)

**Target Platform**: 現代瀏覽器(Chrome, Firefox, Safari, Edge 最新兩個版本)
**Project Type**: web(前端 + 後端 API)  
**Performance Goals**:

- 爬取少於 100 則留言時間 <= 60 秒(含速率控制間隔)
- UI 互動響應時間 <= 100ms
- 支援單一貼文最多數千則留言的分批處理

**Constraints**:

- API 回應時間 p95 <= 200ms(憲章要求)
- 爬取速率必須每批次間隔 3-5 秒(避免平台限制)
- 不可觸發社群平台反爬蟲機制
- 第一次使用 90% 使用者無需說明即可操作(SC-005)

**Scale/Scope**:

- 單一使用者單次作業流程
- 支援 Facebook + Instagram 兩大平台
- 預期單一貼文留言數通常 < 數千則

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. 代碼品質標準

- [ ] 使用自動化格式化工具與 linter（語言/框架確定後選擇工具）
- [ ] 所有公開 API 與複雜邏輯需有清楚文件
- [ ] 程式碼以職責分明、低耦合模組組織（前端元件化、後端分層架構）
- [ ] 遵循 SOLID 原則，避免深度巢狀與過長函式
- [ ] 所有變更須通過同儕審查

### II. 測試標準（不可協商）

- [ ] 強制採用 TDD（紅—綠—重構循環）
- [ ] 單元測試最低 80% 覆蓋率，關鍵路徑 100%
- [ ] 必須包含單元測試、整合測試、契約測試
- [ ] 測試必須為確定性、快速、隔離並清楚描述預期行為
- [ ] 所有測試在 CI 中必須通過方可合併

### III. 使用者體驗一致性

- [ ] 建立可重用元件與設計系統（UI 元件庫）
- [ ] UI 元件、術語、流程與互動模式在各功能間一致
- [ ] 遵守 WCAG 2.1 AA 標準（鍵盤操作、螢幕閱讀器、色彩對比）
- [ ] 錯誤訊息清晰、可行並引導使用者解決問題（見 FR-014, FR-015, FR-016, FR-025）
- [ ] 使用者操作立即提供視覺回饋（載入狀態、進度指示見 FR-019）
- [ ] 使用者文件清楚且容易找到

### IV. 性能要求

- [ ] API 端點 p95 <= 200ms
- [ ] UI 互動響應時間 <= 100ms
- [ ] 系統能在峰值負載下運作（單一使用者爬取數千則留言）
- [ ] 避免記憶體洩漏與過度配置（特別是大量資料處理時）
- [ ] 使用分析與 profiler 偵測瓶頸
- [ ] 主要功能上線前通過負載測試

**初步評估(Phase 0 前)**: ✅ PASS

- 無明顯違規項目
- 所有品質門檻可在標準 Web 應用程式架構下實現
- 性能目標明確且可量化(SC-001 至 SC-011)
- UX 一致性需求已在規格中定義(FR-006 至 FR-020c)
- 測試優先流程可透過標準 TDD 實踐達成

**Phase 1 設計後重新檢查**: ✅ PASS

### I. 代碼品質標準

- [x] 使用自動化格式化工具與 linter: Ruff(後端), Black(後端), ESLint(前端), Prettier(前端)
- [x] 所有公開 API 與複雜邏輯需有清楚文件: OpenAPI 自動文件 + 程式碼註解
- [x] 程式碼以職責分明、低耦合模組組織: 前後端分離,後端分層(models/services/api),前端元件化
- [x] 遵循 SOLID 原則,避免深度嵌套與過長函式: TypeScript + Python 型別提示,函式單一職責
- [x] 所有變更須通過同儕審查: Git workflow + PR 審查

### II. 測試標準(不可協商)

- [x] 強制採用 TDD(紅—綠—重構循環): pytest watch mode + Jest watch mode 支援
- [x] 單元測試最低 80% 覆蓋率,關鍵路徑 100%: pytest-cov + Jest coverage 報告
- [x] 必須包含單元測試、整合測試、契約測試: pytest(單元+整合) + Pact(契約) + Jest(前端單元)
- [x] 測試必須為確定性、快速、隔離並清楚描述預期行為: 標準測試框架最佳實踐
- [x] 所有測試在 CI 中必須通過方可合併: GitHub Actions workflow 配置

### III. 使用者體驗一致性

- [x] 建立可重用元件與設計系統(UI 元件庫): React components + TanStack Table
- [x] UI 元件、術語、流程與互動模式在各功能間一致: 單頁應用程式,統一設計語言
- [x] 遵守 WCAG 2.1 AA 標準(鍵盤操作、螢幕閱讀器、色彩對比): react-aria/Radix UI + eslint-plugin-jsx-a11y
- [x] 錯誤訊息清晰、可行並引導使用者解決問題(見 FR-014, FR-015, FR-016, FR-025): 標準化 ErrorResponse schema
- [x] 使用者操作立即提供視覺回饋(載入狀態、進度指示見 FR-019): Progress API + 前端狀態管理
- [x] 使用者文件清楚且容易找到: quickstart.md + 規格文件完整

### IV. 性能要求

- [x] API 端點 p95 <= 200ms: FastAPI 非同步架構 + 效能分析工具(cProfile, py-spy)
- [x] UI 互動響應時間 <= 100ms: React 效能最佳化 + Lighthouse 監控
- [x] 系統能在峰值負載下運作(單一使用者爬取數千則留言): 分批處理 + asyncio 控制
- [x] 避免記憶體洩漏與過度配置(特別是大量資料處理時): Python GC + React memo/useMemo
- [x] 使用分析與 profiler 偵測瓶頸: Chrome DevTools + pytest-benchmark
- [x] 主要功能上線前通過負載測試: Locust 負載測試腳本

**結論**: 所有憲章原則可在所選技術堆疊下實現,無需複雜度證明(Complexity Tracking)。

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── src/
│   ├── models/          # 資料實體（Post, Comment, EditData）
│   ├── services/        # 爬蟲邏輯、速率控制、平台適配器
│   ├── api/             # REST API 端點
│   └── utils/           # 輔助函式（驗證網址、時間格式化等）
└── tests/
    ├── unit/            # 單元測試（80%+ 覆蓋率）
    ├── integration/     # 整合測試（API + 爬蟲服務）
    └── contract/        # API 契約測試

frontend/
├── src/
│   ├── components/      # UI 元件（輸入框、按鈕、表格、進度條等）
│   ├── pages/           # 主頁面（單頁應用程式）
│   ├── services/        # API 呼叫、狀態管理
│   └── styles/          # 設計系統、可重用樣式
└── tests/
    ├── unit/            # 元件單元測試
    └── integration/     # 端對端流程測試
```

**Structure Decision**: 選擇 Web 應用程式架構（Option 2），因功能需求明確為線上 Web App（FR-017），需前端提供使用者介面與後端處理爬蟲邏輯。前後端分離架構支援：

- 前端專注於 UX 一致性與即時回饋（憲章原則 III）
- 後端專注於爬蟲邏輯、速率控制與資料處理（FR-001 至 FR-027）
- 測試分層清晰，符合 TDD 要求（憲章原則 II）
- 可獨立擴展前後端技術堆疊

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
