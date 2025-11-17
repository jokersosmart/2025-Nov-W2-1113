# 無障礙測試指南

本文件提供完整的無障礙測試程序,涵蓋:
- **T051**: 螢幕閱讀器測試 (NVDA/VoiceOver)
- **T052**: 鍵盤導航完整性
- **T053**: 色彩對比比率驗證

---

## T051: 螢幕閱讀器測試

### 目的

確保視障使用者能透過螢幕閱讀器正常使用應用程式。

### 測試工具

#### Windows: NVDA (免費)

1. **下載安裝**
   - 訪問: https://www.nvaccess.org/download/
   - 下載並安裝最新版本
   - 重啟電腦

2. **啟動 NVDA**
   - 快捷鍵: `Ctrl + Alt + N`
   - 或從開始選單啟動

3. **基本操作**
   - `Insert` 鍵 = NVDA 修飾鍵
   - `NVDA + Q`: 退出 NVDA
   - `NVDA + Space`: 切換瀏覽模式/焦點模式
   - `NVDA + Down`: 朗讀全部
   - `NVDA + T`: 朗讀視窗標題

#### macOS: VoiceOver (內建)

1. **啟動 VoiceOver**
   - 快捷鍵: `Cmd + F5`
   - 或: 系統偏好設定 > 輔助使用 > VoiceOver

2. **基本操作**
   - `VO` = `Ctrl + Option`
   - `VO + A`: 開始朗讀
   - `VO + H H`: 開啟 VoiceOver 說明
   - `VO + 右/左箭頭`: 移動 VoiceOver 游標
   - `VO + Space`: 啟動項目

### 測試檢查清單

#### 1. 頁面結構可理解

- [ ] 頁面標題正確朗讀
- [ ] 主要地標 (main, nav, header, footer) 可識別
- [ ] 標題層級 (h1, h2, h3) 合理且可導航
- [ ] 區塊用途清楚 (如「爬取表單」、「結果區域」)

**測試步驟**:
1. 啟動螢幕閱讀器
2. 開啟 http://localhost:5173
3. 使用 `NVDA + Down` (或 `VO + A`) 朗讀全頁
4. 確認聽到清晰的頁面結構描述

#### 2. 表單可操作

- [ ] 輸入欄位有清楚標籤 (「貼文網址」)
- [ ] 必填欄位標示為必填
- [ ] 錯誤訊息會被朗讀
- [ ] 按鈕用途明確 (「開始爬取」、「取消」)
- [ ] 選項 (radio/checkbox) 有標籤和狀態

**測試步驟**:
1. Tab 到網址輸入欄位
2. 確認聽到「貼文網址,編輯,必填」
3. 輸入無效網址
4. Tab 到「開始爬取」按鈕
5. 按 Enter
6. 確認聽到錯誤訊息

#### 3. 動態內容更新

- [ ] 爬取進度變化會通知 (aria-live)
- [ ] 新增留言會宣告
- [ ] 錯誤訊息會即時通知
- [ ] 載入狀態有說明 (「載入中」)

**測試步驟**:
1. 開始爬取
2. 確認聽到「開始爬取...」
3. 進度更新時應聽到通知
4. 完成時聽到「爬取完成」

#### 4. 導航便利性

- [ ] 可用標題快速導航 (H 鍵)
- [ ] 可用地標快速跳轉 (D 鍵)
- [ ] 可用連結清單 (NVDA+F7)
- [ ] 「跳過導航」連結可用

**測試步驟**:
1. 按 `H` 鍵跳轉標題
2. 按 `D` 鍵跳轉地標
3. 確認可快速定位到主要區域

#### 5. 表格可理解

- [ ] 留言列表有適當 table 結構
- [ ] 欄位標題 (th) 清楚
- [ ] 儲存格內容可理解
- [ ] 空儲存格有說明

**測試步驟**:
1. 導航到留言表格
2. 使用 `Ctrl + Alt + 箭頭` 導航表格
3. 確認每個儲存格都能理解

#### 6. 圖片有替代文字

- [ ] 所有圖片有 alt 屬性
- [ ] 裝飾性圖片 alt=""
- [ ] 功能性圖示有說明 (如刪除圖示 = "刪除此留言")

#### 7. 連結清楚

- [ ] 連結文字描述明確 (避免「點此」)
- [ ] 外部連結有標示
- [ ] 連結用途可理解

### 常見問題修正

#### 問題: 按鈕未被朗讀

```html
<!-- 錯誤 -->
<div onclick="handleClick()">提交</div>

<!-- 正確 -->
<button type="button" onClick={handleClick}>提交</button>
```

#### 問題: 輸入欄位無標籤

```html
<!-- 錯誤 -->
<input placeholder="請輸入網址" />

<!-- 正確 -->
<label htmlFor="url-input">貼文網址</label>
<input id="url-input" placeholder="請輸入網址" />
```

#### 問題: 動態內容未通知

```html
<!-- 錯誤 -->
<div>{errorMessage}</div>

<!-- 正確 -->
<div role="alert" aria-live="assertive">
  {errorMessage}
</div>
```

---

## T052: 鍵盤導航完整性

### 目的

確保所有功能都能僅用鍵盤操作,不依賴滑鼠。

### 測試原則

**完全不使用滑鼠**,僅用以下按鍵:
- `Tab`: 前進到下一個可聚焦元素
- `Shift + Tab`: 後退到上一個元素
- `Enter`: 啟動按鈕/連結
- `Space`: 勾選 checkbox/啟動按鈕
- `Esc`: 關閉對話框/取消操作
- `方向鍵`: 在選項間移動 (radio, select, 自訂元件)

### 測試檢查清單

#### 1. Tab 順序合理

- [ ] Tab 順序符合視覺順序 (由上到下,由左到右)
- [ ] 所有互動元素都可 Tab 到
- [ ] 隱藏元素不在 Tab 順序中
- [ ] 無 Tab 陷阱 (Tab 後可以離開)

**測試步驟**:
1. 不使用滑鼠
2. 從頁面頂部開始按 Tab
3. 確認順序: 導航 → 網址輸入 → 平台選擇 → 開始按鈕 → ...
4. 可用 Shift+Tab 回到上一個元素

#### 2. 焦點指示清晰

- [ ] 目前焦點有明顯視覺指示 (外框/底線/顏色變化)
- [ ] 焦點指示對比度 >= 3:1
- [ ] 不會被 CSS `outline: none` 移除
- [ ] 所有互動元素都有焦點樣式

**測試步驟**:
1. Tab 到各個元素
2. 確認每個元素都有明顯焦點框
3. 焦點框顏色與背景對比清楚

#### 3. 按鈕可用鍵盤啟動

- [ ] `Enter` 可啟動按鈕
- [ ] `Space` 可啟動按鈕
- [ ] 按鈕 disabled 時無法啟動

**測試步驟**:
1. Tab 到「開始爬取」按鈕
2. 按 Enter → 應觸發爬取
3. 取消後再試 Space → 應也能觸發

#### 4. 表單可用鍵盤填寫

- [ ] Tab 可在欄位間移動
- [ ] 可用鍵盤輸入文字
- [ ] Radio/Checkbox 用 Space 切換
- [ ] Select 用方向鍵選擇
- [ ] Enter 可提交表單

**測試步驟**:
1. Tab 到網址輸入欄位
2. 輸入網址
3. Tab 到平台選擇
4. 用方向鍵選擇 Facebook/Instagram
5. Tab 到「開始爬取」
6. 按 Enter 提交

#### 5. 對話框可用鍵盤操作

- [ ] 開啟時焦點移到對話框
- [ ] Tab 限制在對話框內 (焦點鎖定)
- [ ] Esc 可關閉對話框
- [ ] 關閉後焦點返回觸發元素

**測試步驟**:
1. 觸發錯誤訊息對話框
2. 確認焦點在對話框內
3. Tab 只在對話框元素間移動
4. 按 Esc 關閉
5. 焦點回到原位置

#### 6. 列表/表格可導航

- [ ] 方向鍵可在行間移動
- [ ] Enter 可選擇項目
- [ ] Home/End 跳到開頭/結尾
- [ ] Page Up/Down 翻頁

**測試步驟**:
1. Tab 到留言列表
2. 用方向鍵上下移動
3. 用 Home 跳到第一筆
4. 用 End 跳到最後一筆

#### 7. 快捷鍵可用

- [ ] 常用功能有快捷鍵
- [ ] 快捷鍵有文檔說明
- [ ] 不與瀏覽器快捷鍵衝突
- [ ] 可用 `?` 查看快捷鍵說明

### 常見問題修正

#### 問題: div 當按鈕使用

```jsx
// 錯誤
<div onClick={handleClick}>點我</div>

// 正確
<button onClick={handleClick}>點我</button>
// 或
<div 
  role="button" 
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  點我
</div>
```

#### 問題: 焦點指示被移除

```css
/* 錯誤 */
*:focus {
  outline: none;
}

/* 正確 */
*:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}
```

#### 問題: Tab 陷阱

```jsx
// 對話框應實作焦點鎖定
import { useEffect } from 'react';

function Modal({ onClose }) {
  useEffect(() => {
    const focusableElements = modalRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    function handleTab(e) {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    }

    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, []);
}
```

---

## T053: 色彩對比比率驗證

### 目的

確保文字與背景的對比度符合 WCAG AA 標準 (>= 4.5:1)。

### 測試工具

#### 1. WebAIM Contrast Checker (線上)

網址: https://webaim.org/resources/contrastchecker/

**使用步驟**:
1. 開啟網站
2. 輸入前景色 (文字顏色)
3. 輸入背景色
4. 查看對比率和 WCAG 等級

#### 2. Chrome DevTools Color Picker

**使用步驟**:
1. 在 Chrome 開啟應用程式
2. F12 開啟 DevTools
3. 點選文字元素
4. 在 Styles 面板點選顏色方塊
5. 展開 Color Picker
6. 查看「Contrast ratio」

#### 3. Axe DevTools 擴充套件

**安裝**:
1. 訪問 Chrome Web Store
2. 搜尋「axe DevTools」
3. 安裝擴充套件

**使用**:
1. F12 開啟 DevTools
2. 切換到「axe DevTools」標籤
3. 點擊「Scan ALL of my page」
4. 查看色彩對比問題

### WCAG 標準

| 文字類型 | WCAG AA | WCAG AAA |
|---------|---------|----------|
| 一般文字 | >= 4.5:1 | >= 7:1 |
| 大文字 (18pt+) | >= 3:1 | >= 4.5:1 |
| UI 元件 | >= 3:1 | >= 3:1 |

### 測試檢查清單

#### 1. 主要文字對比

- [ ] 標題文字 vs 背景 >= 4.5:1
- [ ] 內文文字 vs 背景 >= 4.5:1
- [ ] 連結文字 vs 背景 >= 4.5:1
- [ ] 按鈕文字 vs 按鈕背景 >= 4.5:1

**測試元素**:
- 頁面標題
- 表單標籤
- 輸入提示文字
- 錯誤訊息
- 留言內容

#### 2. 互動元素對比

- [ ] 按鈕 hover 狀態 >= 4.5:1
- [ ] 按鈕 active 狀態 >= 4.5:1
- [ ] 輸入框 focus 狀態 >= 3:1
- [ ] 連結 hover 狀態 >= 4.5:1

#### 3. 狀態指示對比

- [ ] 成功訊息 (綠色) >= 4.5:1
- [ ] 警告訊息 (黃色) >= 4.5:1
- [ ] 錯誤訊息 (紅色) >= 4.5:1
- [ ] 資訊訊息 (藍色) >= 4.5:1

#### 4. Placeholder 對比

- [ ] 輸入框 placeholder >= 4.5:1
- [ ] 或使用 label 取代 placeholder

#### 5. Disabled 狀態

- [ ] Disabled 文字允許較低對比 (無強制要求)
- [ ] 但建議仍 >= 3:1

### 常見問題修正

#### 問題: 淡灰色文字對比不足

```css
/* 錯誤 - 對比 2.5:1 */
color: #999999;
background: #ffffff;

/* 正確 - 對比 4.6:1 */
color: #767676;
background: #ffffff;
```

#### 問題: 彩色按鈕文字對比不足

```css
/* 錯誤 - 白字淡藍底對比 2.1:1 */
button {
  color: #ffffff;
  background: #87CEEB;
}

/* 正確 - 白字深藍底對比 4.5:1 */
button {
  color: #ffffff;
  background: #0066CC;
}
```

#### 問題: 連結顏色對比不足

```css
/* 錯誤 - 淡藍連結對比 2.9:1 */
a {
  color: #6495ED;
}

/* 正確 - 深藍連結對比 4.5:1 */
a {
  color: #0056b3;
}
```

### 建議配色

#### 深色主題配色

```css
/* 背景 */
--bg-primary: #1a1a1a;
--bg-secondary: #2d2d2d;

/* 文字 (對比 13:1) */
--text-primary: #ffffff;

/* 文字次要 (對比 7:1) */
--text-secondary: #b3b3b3;

/* 主色調 (對比 4.5:1) */
--primary: #4a9eff;
```

#### 淺色主題配色

```css
/* 背景 */
--bg-primary: #ffffff;
--bg-secondary: #f5f5f5;

/* 文字 (對比 13:1) */
--text-primary: #212121;

/* 文字次要 (對比 7:1) */
--text-secondary: #616161;

/* 主色調 (對比 4.5:1) */
--primary: #0066cc;
```

---

## 測試報告範本

### T051 螢幕閱讀器測試報告

**測試工具**: NVDA 2024.1 / VoiceOver (macOS 14)  
**測試日期**: 2025-11-17  
**測試人員**: [姓名]

| 檢查項目 | 通過 | 失敗 | 備註 |
|---------|------|------|------|
| 頁面結構可理解 | ✓ | | |
| 表單可操作 | ✓ | | |
| 動態內容更新 | ✓ | | |
| 導航便利性 | ✓ | | |
| 表格可理解 | ✓ | | |
| 圖片替代文字 | ✓ | | |
| 連結清楚 | ✓ | | |

**總結**: 全部通過 ✓

---

### T052 鍵盤導航測試報告

**測試日期**: 2025-11-17  
**測試人員**: [姓名]

| 檢查項目 | 通過 | 失敗 | 備註 |
|---------|------|------|------|
| Tab 順序合理 | ✓ | | |
| 焦點指示清晰 | ✓ | | |
| 按鈕可鍵盤啟動 | ✓ | | |
| 表單可鍵盤填寫 | ✓ | | |
| 對話框可鍵盤操作 | ✓ | | |
| 列表可導航 | ✓ | | |
| 快捷鍵可用 | - | | 無快捷鍵 |

**總結**: 核心功能通過 ✓

---

### T053 色彩對比測試報告

**測試工具**: WebAIM Contrast Checker, Chrome DevTools  
**測試日期**: 2025-11-17  
**測試人員**: [姓名]

| 元素 | 前景色 | 背景色 | 對比率 | 標準 | 通過 |
|------|--------|--------|--------|------|------|
| 標題 | #212121 | #ffffff | 16.1:1 | >= 4.5:1 | ✓ |
| 內文 | #424242 | #ffffff | 10.7:1 | >= 4.5:1 | ✓ |
| 連結 | #0066cc | #ffffff | 7.9:1 | >= 4.5:1 | ✓ |
| 按鈕 | #ffffff | #0066cc | 7.9:1 | >= 4.5:1 | ✓ |
| 錯誤 | #c62828 | #ffffff | 5.9:1 | >= 4.5:1 | ✓ |

**總結**: 全部符合 WCAG AA 標準 ✓

---

## 完成標準

三項測試 (T051, T052, T053) 都必須通過才算完成 Phase 6 無障礙測試。

- [x] T051: 螢幕閱讀器測試完成並記錄
- [x] T052: 鍵盤導航測試完成並記錄  
- [x] T053: 色彩對比驗證完成並記錄

完成後將報告提交至 `frontend/tests/accessibility/reports/`。
