# API 文件

## 目錄

1. [API 概覽](#api-概覽)
2. [認證](#認證)
3. [端點](#端點)
4. [錯誤處理](#錯誤處理)
5. [速率限制](#速率限制)

---

## API 概覽

**Base URL**: `http://localhost:8000`

**版本**: v0.1.0

**內容類型**: `application/json`

**特性**:
- RESTful API 設計
- 即時進度追蹤
- 自動生成 OpenAPI 規範
- 互動式 API 文件 (Swagger UI)

### 互動式文件

訪問以下網址查看完整 API 規範:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 認證

當前版本**不需要**認證。

未來版本可能會加入 API Token 認證機制。

---

## 端點

### 系統端點

#### GET /health

健康檢查端點,用於監控服務狀態。

**請求**:
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**回應**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "Social Comment Scraper API"
}
```

**狀態碼**:
- `200 OK`: 服務正常運行

---

#### GET /

根端點,返回 API 基本資訊。

**請求**:
```http
GET / HTTP/1.1
Host: localhost:8000
```

**回應**:
```json
{
  "message": "Welcome to Social Comment Scraper API",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health"
}
```

**狀態碼**:
- `200 OK`: 成功

---

### 爬取端點

#### POST /api/scrape

開始爬取貼文留言。

**請求**:
```http
POST /api/scrape HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "url": "https://www.facebook.com/example/posts/123456"
}
```

**請求參數**:

| 欄位 | 類型 | 必填 | 說明 |
|-----|------|------|------|
| url | string | ✅ | Facebook 或 Instagram 公開貼文網址 |

**回應**:
```json
{
  "scrape_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "開始爬取..."
}
```

**回應欄位**:

| 欄位 | 類型 | 說明 |
|-----|------|------|
| scrape_id | string (UUID) | 爬取任務 ID |
| status | string | 狀態: `pending`, `running`, `completed`, `failed`, `cancelled` |
| message | string | 狀態描述訊息 |

**狀態碼**:
- `200 OK`: 爬取任務已建立
- `400 Bad Request`: 無效的網址或參數
- `500 Internal Server Error`: 伺服器錯誤

**錯誤範例**:
```json
{
  "error": "Validation error",
  "message": "url is required",
  "details": [...]
}
```

---

#### GET /api/scrape/{scrape_id}/progress

查詢爬取進度。

**請求**:
```http
GET /api/scrape/550e8400-e29b-41d4-a716-446655440000/progress HTTP/1.1
Host: localhost:8000
```

**路徑參數**:

| 參數 | 類型 | 說明 |
|-----|------|------|
| scrape_id | string (UUID) | 爬取任務 ID |

**回應**:
```json
{
  "scrape_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 0.6,
  "total_comments": 200,
  "scraped_comments": 120,
  "error": null
}
```

**回應欄位**:

| 欄位 | 類型 | 說明 |
|-----|------|------|
| scrape_id | string | 爬取任務 ID |
| status | string | 狀態: `pending`, `running`, `completed`, `failed`, `cancelled` |
| progress | number | 進度 (0.0 - 1.0) |
| total_comments | number | 留言總數 |
| scraped_comments | number | 已爬取數量 |
| error | string \| null | 錯誤訊息 (如有) |

**狀態碼**:
- `200 OK`: 成功
- `404 Not Found`: 找不到指定的爬取任務

---

#### POST /api/scrape/{scrape_id}/cancel

取消爬取任務。

**請求**:
```http
POST /api/scrape/550e8400-e29b-41d4-a716-446655440000/cancel HTTP/1.1
Host: localhost:8000
```

**路徑參數**:

| 參數 | 類型 | 說明 |
|-----|------|------|
| scrape_id | string (UUID) | 爬取任務 ID |

**回應**:
```json
{
  "scrape_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "已取消爬取"
}
```

**回應欄位**:

| 欄位 | 類型 | 說明 |
|-----|------|------|
| scrape_id | string | 爬取任務 ID |
| status | string | 狀態: `cancelled` |
| message | string | 確認訊息 |

**狀態碼**:
- `200 OK`: 成功取消
- `404 Not Found`: 找不到指定的爬取任務

---

### 匯出端點

#### POST /api/export

匯出留言資料為 Excel 檔案。

**請求**:
```http
POST /api/export HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "post": {
    "platform": "facebook",
    "post_url": "https://www.facebook.com/example/posts/123456",
    "post_time": "2025-11-13T10:30:00Z",
    "post_content": "這是測試貼文",
    "likes_count": 150,
    "comments_count": 3
  },
  "comments": [
    {
      "comment_id": "c001",
      "post_url": "https://www.facebook.com/example/posts/123456",
      "comment_time": "2025-11-13T10:35:00Z",
      "commenter_id": "王小明 (12345678)",
      "comment_content": "很棒的分享!",
      "reply_window": "張專員",
      "reply_content": "感謝您的支持!",
      "customer_notes": "已確認",
      "generated_reply": null
    }
  ]
}
```

**請求參數**:

**post** 物件:

| 欄位 | 類型 | 必填 | 說明 |
|-----|------|------|------|
| platform | string | ✅ | 平台: `facebook` 或 `instagram` |
| post_url | string | ✅ | 貼文網址 |
| post_time | string (ISO 8601) | ✅ | 發文時間 |
| post_content | string | ✅ | 貼文內容 (max 10000 字) |
| likes_count | number | ✅ | 按讚數 |
| comments_count | number | ✅ | 留言總數 |

**comments** 陣列 (每個 comment):

| 欄位 | 類型 | 必填 | 說明 |
|-----|------|------|------|
| comment_id | string | ✅ | 留言 ID |
| post_url | string | ✅ | 貼文網址 |
| comment_time | string (ISO 8601) | ✅ | 留言時間 |
| commenter_id | string | ✅ | 留言者 ID (格式: 姓名 (ID)) |
| comment_content | string | ✅ | 留言內容 (max 5000 字) |
| reply_window | string \| null | ⬜ | 回覆窗口 (max 100 字) |
| reply_content | string \| null | ⬜ | 回覆內容 (max 1000 字) |
| customer_notes | string \| null | ⬜ | 客戶確認/修改處 (max 500 字) |
| generated_reply | string \| null | ⬜ | 生成的回覆 (max 1000 字) |

**回應**:

Binary stream (Excel 檔案)

**回應標頭**:
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="facebook_comments_20251116_143052.xlsx"
```

**狀態碼**:
- `200 OK`: 成功生成 Excel 檔案
- `400 Bad Request`: 無效的請求參數
- `500 Internal Server Error`: 伺服器錯誤

**錯誤範例**:
```json
{
  "error": "Validation error",
  "message": "post is required",
  "details": [...]
}
```

---

## 錯誤處理

### 錯誤回應格式

所有錯誤回應遵循統一格式:

```json
{
  "error": "錯誤類型",
  "message": "使用者友善的錯誤訊息",
  "details": "詳細錯誤資訊 (選用)"
}
```

### HTTP 狀態碼

| 狀態碼 | 說明 | 處理方式 |
|--------|------|----------|
| 200 OK | 成功 | - |
| 400 Bad Request | 請求參數錯誤 | 檢查請求參數 |
| 404 Not Found | 資源不存在 | 確認 ID 或路徑正確 |
| 422 Unprocessable Entity | 驗證錯誤 | 檢查資料格式與型別 |
| 429 Too Many Requests | 速率限制 | 等待後重試 |
| 500 Internal Server Error | 伺服器錯誤 | 聯繫技術支援 |
| 503 Service Unavailable | 服務暫時無法使用 | 稍後重試 |

### 常見錯誤

#### 1. 驗證錯誤 (400)

**原因**: 缺少必要欄位或格式錯誤

**範例**:
```json
{
  "error": "Validation error",
  "message": "url is required",
  "details": [
    {
      "loc": ["body", "url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**解決方法**: 檢查請求參數是否完整且格式正確

---

#### 2. 平台驗證錯誤 (400)

**原因**: platform 欄位只接受 `facebook` 或 `instagram`

**範例**:
```json
{
  "error": "Validation error",
  "message": "Input should be 'facebook' or 'instagram'",
  "details": [...]
}
```

**解決方法**: 確認 platform 值正確

---

#### 3. 爬取任務不存在 (404)

**原因**: 指定的 scrape_id 不存在

**範例**:
```json
{
  "error": "Not Found",
  "message": "Scrape job not found",
  "details": null
}
```

**解決方法**: 確認 scrape_id 正確

---

#### 4. 速率限制 (429)

**原因**: 請求過於頻繁

**範例**:
```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Please try again later.",
  "details": "Retry after 60 seconds"
}
```

**解決方法**: 等待指定時間後重試

---

## 速率限制

### 當前限制

目前版本**無速率限制**。

### 未來規劃

未來版本可能實施:
- 每 IP 每分鐘 60 次請求
- 每個爬取任務間隔至少 3 秒

### 最佳實踐

建議:
- 避免短時間內大量請求
- 使用進度端點時,建議輪詢間隔 >= 2 秒
- 大量留言分批爬取,每批間隔 3-5 秒

---

## 範例

### 完整爬取流程

```javascript
// 1. 開始爬取
const scrapeResponse = await fetch('http://localhost:8000/api/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://www.facebook.com/example/posts/123456'
  })
});
const { scrape_id } = await scrapeResponse.json();

// 2. 輪詢進度
const pollProgress = setInterval(async () => {
  const progressResponse = await fetch(
    `http://localhost:8000/api/scrape/${scrape_id}/progress`
  );
  const progress = await progressResponse.json();
  
  console.log(`已爬取: ${progress.scraped_comments}/${progress.total_comments}`);
  
  if (progress.status === 'completed') {
    clearInterval(pollProgress);
    console.log('爬取完成!');
  }
}, 2000);

// 3. (選用) 取消爬取
// await fetch(`http://localhost:8000/api/scrape/${scrape_id}/cancel`, {
//   method: 'POST'
// });
```

### 匯出 Excel

```javascript
const exportResponse = await fetch('http://localhost:8000/api/export', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    post: {
      platform: 'facebook',
      post_url: 'https://www.facebook.com/example/posts/123456',
      post_time: '2025-11-13T10:30:00Z',
      post_content: '測試貼文',
      likes_count: 150,
      comments_count: 3
    },
    comments: [
      {
        comment_id: 'c001',
        post_url: 'https://www.facebook.com/example/posts/123456',
        comment_time: '2025-11-13T10:35:00Z',
        commenter_id: '王小明 (12345678)',
        comment_content: '很棒!',
        reply_window: '張專員',
        reply_content: '感謝支持!',
        customer_notes: '已確認',
        generated_reply: null
      }
    ]
  })
});

// 下載檔案
const blob = await exportResponse.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'facebook_comments_20251116_143052.xlsx';
a.click();
```

---

## 變更記錄

### v0.1.0 (2025-11-16)

- 初始版本
- 支援 Facebook/Instagram 爬取
- 支援進度追蹤與取消
- 支援匯出 Excel

---

**版本**: v0.1.0  
**最後更新**: 2025-11-16  
**作者**: COM_PAR Team
