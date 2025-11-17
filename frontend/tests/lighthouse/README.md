# Lighthouse 效能與無障礙性稽核

## 目的

使用 Google Lighthouse 驗證前端應用程式的:
- **效能 (Performance)**: >= 95 分
- **無障礙性 (Accessibility)**: >= 95 分
- **最佳實踐 (Best Practices)**: >= 90 分
- **SEO**: >= 90 分

## 前置需求

### 安裝 Lighthouse

```bash
npm install -g lighthouse
# 或
npm install --save-dev lighthouse
```

### 啟動前端開發伺服器

```bash
cd frontend
npm run dev
```

應用程式應運行於 `http://localhost:5173`

## 執行 Lighthouse 稽核

### 方式 1: Chrome DevTools (推薦)

1. 開啟 Chrome 瀏覽器
2. 訪問 `http://localhost:5173`
3. 按 F12 開啟 DevTools
4. 切換到 "Lighthouse" 標籤
5. 選擇稽核類別:
   - ✓ Performance
   - ✓ Accessibility
   - ✓ Best practices
   - ✓ SEO
6. 選擇設備: Desktop 或 Mobile
7. 點擊 "Analyze page load"
8. 等待稽核完成 (約 30-60 秒)
9. 檢視報告

### 方式 2: 命令行

#### 桌面版稽核

```bash
lighthouse http://localhost:5173 \
  --output html \
  --output-path ./lighthouse-report-desktop.html \
  --preset=desktop \
  --view
```

#### 行動版稽核

```bash
lighthouse http://localhost:5173 \
  --output html \
  --output-path ./lighthouse-report-mobile.html \
  --preset=mobile \
  --view
```

#### 產生 JSON 報告

```bash
lighthouse http://localhost:5173 \
  --output json \
  --output-path ./lighthouse-report.json \
  --preset=desktop
```

### 方式 3: 使用腳本 (自動化)

執行 PowerShell 腳本:

```powershell
.\scripts\run-lighthouse.ps1
```

或 npm 腳本:

```bash
cd frontend
npm run lighthouse
```

## 成功標準 (T050)

### 必須達成

- ✅ **Performance >= 95**: 效能分數至少 95 分
- ✅ **Accessibility >= 95**: 無障礙性分數至少 95 分

### 建議目標

- **Best Practices >= 90**: 最佳實踐分數至少 90 分
- **SEO >= 90**: SEO 分數至少 90 分
- **First Contentful Paint (FCP) < 1.8s**: 首次內容繪製
- **Largest Contentful Paint (LCP) < 2.5s**: 最大內容繪製
- **Total Blocking Time (TBT) < 200ms**: 總阻塞時間
- **Cumulative Layout Shift (CLS) < 0.1**: 累積版面配置位移

## 結果解讀

### 分數範圍

- **90-100**: 優秀 (綠色) ✓
- **50-89**: 需改進 (橘色) ⚠️
- **0-49**: 不佳 (紅色) ✗

### Performance 指標

| 指標 | 優秀 | 需改進 | 不佳 |
|------|------|--------|------|
| FCP | < 1.8s | 1.8-3s | > 3s |
| LCP | < 2.5s | 2.5-4s | > 4s |
| TBT | < 200ms | 200-600ms | > 600ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |
| Speed Index | < 3.4s | 3.4-5.8s | > 5.8s |

### Accessibility 常見問題

- **缺少 alt 屬性**: 圖片應有替代文字
- **色彩對比不足**: 文字與背景對比 >= 4.5:1
- **缺少 ARIA 標籤**: 互動元素應有適當標籤
- **無鍵盤存取**: 所有功能可用鍵盤操作
- **缺少表單標籤**: 輸入欄位應有關聯標籤

## 最佳化建議

### 提升 Performance

1. **程式碼分割**
   ```typescript
   // 使用動態 import
   const Component = lazy(() => import('./Component'));
   ```

2. **圖片最佳化**
   ```html
   <img src="image.webp" loading="lazy" alt="描述" />
   ```

3. **啟用快取**
   ```typescript
   // vite.config.ts
   build: {
     rollupOptions: {
       output: {
         manualChunks: {
           vendor: ['react', 'react-dom']
         }
       }
     }
   }
   ```

4. **移除未使用的程式碼**
   ```bash
   npm run build -- --analyze
   ```

### 提升 Accessibility

1. **語義化 HTML**
   ```html
   <main>
     <section aria-label="爬取表單">
       <form>...</form>
     </section>
   </main>
   ```

2. **ARIA 標籤**
   ```html
   <button aria-label="開始爬取">開始</button>
   <div role="alert" aria-live="polite">錯誤訊息</div>
   ```

3. **鍵盤導航**
   ```typescript
   onKeyDown={(e) => {
     if (e.key === 'Enter') handleSubmit();
   }}
   ```

4. **色彩對比**
   - 使用工具: https://webaim.org/resources/contrastchecker/
   - 文字 vs 背景: >= 4.5:1
   - 大文字: >= 3:1

### 提升 Best Practices

1. **HTTPS** (生產環境)
2. **安全標頭**
   ```typescript
   // vite.config.ts
   server: {
     headers: {
       'X-Content-Type-Options': 'nosniff',
       'X-Frame-Options': 'DENY'
     }
   }
   ```

3. **錯誤處理**
   - 使用 Error Boundary
   - 顯示友善錯誤訊息

### 提升 SEO

1. **Meta 標籤**
   ```html
   <meta name="description" content="社群留言爬蟲工具" />
   <meta name="viewport" content="width=device-width, initial-scale=1" />
   ```

2. **語言宣告**
   ```html
   <html lang="zh-TW">
   ```

3. **語義化標題**
   ```html
   <h1>主標題</h1>
   <h2>次標題</h2>
   ```

## 自動化稽核

### CI/CD 整合

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on:
  pull_request:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
      
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            http://localhost:5173
          uploadArtifacts: true
          temporaryPublicStorage: true
```

### 使用 Lighthouse CI

```bash
# 安裝
npm install -g @lhci/cli

# 初始化
lhci autorun

# 自訂設定
# lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:5173"],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.95}],
        "categories:accessibility": ["error", {"minScore": 0.95}]
      }
    }
  }
}
```

## 常見問題

### Q: 本地稽核分數與生產環境不同?

A: 正常。生產環境通常較快因為:
- 啟用壓縮
- CDN 加速
- 快取機制

### Q: Performance 分數不穩定?

A: 多次執行取平均值:
```bash
lighthouse http://localhost:5173 --runs=5
```

### Q: 如何只測試特定類別?

A: 使用 `--only-categories` 參數:
```bash
lighthouse http://localhost:5173 \
  --only-categories=performance,accessibility
```

### Q: 如何在 CI 中執行?

A: 使用 headless Chrome:
```bash
lighthouse http://localhost:5173 \
  --chrome-flags="--headless" \
  --output json
```

## 資源

- [Lighthouse 官方文件](https://developers.google.com/web/tools/lighthouse)
- [Web Vitals](https://web.dev/vitals/)
- [WCAG 2.1 指南](https://www.w3.org/WAI/WCAG21/quickref/)
- [色彩對比檢查器](https://webaim.org/resources/contrastchecker/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

## 報告範例

成功的稽核應顯示:

```
Performance: 98/100 ✓
Accessibility: 100/100 ✓
Best Practices: 92/100 ✓
SEO: 91/100 ✓

Metrics:
- First Contentful Paint: 0.8s
- Largest Contentful Paint: 1.2s
- Total Blocking Time: 50ms
- Cumulative Layout Shift: 0.02
- Speed Index: 1.5s
```
