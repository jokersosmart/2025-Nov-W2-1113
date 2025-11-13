# 資料模型 - 社群留言爬蟲工具

**Feature**: 001-social-comment-scraper  
**Date**: 2025-11-14  
**Source**: 從 spec.md 功能需求與關鍵實體提取

---

## 核心實體

### Post(貼文)

**描述**: 代表 Facebook 或 Instagram 上的一則公開貼文

**屬性**:

| 屬性名稱 | 類型 | 必填 | 驗證規則 | 說明 |
|---------|------|------|---------|------|
| `platform` | `Enum["facebook", "instagram"]` | ✓ | 僅限兩個值 | 貼文來源平台 |
| `post_url` | `string (URL)` | ✓ | 有效的 Facebook/Instagram 公開貼文網址 | 原始貼文連結(FR-007) |
| `post_time` | `datetime (ISO 8601)` | ✓ | 有效的日期時間格式 | 發文時間(FR-003) |
| `post_content` | `string` | ✓ | 最大長度 10,000 字元 | 貼文內容文字(FR-003) |
| `likes_count` | `integer` | ✓ | >= 0 | 按讚數(FR-003) |
| `comments_count` | `integer` | ✓ | >= 0 | 留言總數(FR-003) |

**關聯性**:

- 一個 Post 包含多個 Comment(一對多)

**狀態轉換**: 不適用(唯讀資料,爬取後不變更)

**範例**:

```json
{
  "platform": "facebook",
  "post_url": "https://www.facebook.com/example/posts/123456789",
  "post_time": "2025-11-13T14:30:52+08:00",
  "post_content": "這是一則範例貼文內容",
  "likes_count": 128,
  "comments_count": 45
}
```

---

### Comment(留言)

**描述**: 代表貼文下的一則第一層留言(不包含留言下的回覆串,FR-005)

**屬性**:

| 屬性名稱 | 類型 | 必填 | 驗證規則 | 說明 |
|---------|------|------|---------|------|
| `comment_id` | `string (UUID v4)` | ✓ | 系統生成,唯一 | 留言唯一識別碼 |
| `post_url` | `string (URL)` | ✓ | 外鍵,關聯至 Post | 所屬貼文連結 |
| `comment_time` | `datetime (ISO 8601)` | ✓ | 有效的日期時間格式 | 留言時間(FR-004) |
| `commenter_id` | `string` | ✓ | 格式: "名稱 (ID)" | 留言者識別(FR-004a),如 "John Doe (12345678)" 或 "@john_doe (12345678)" |
| `comment_content` | `string` | ✓ | 最大長度 5,000 字元 | 留言內容文字(FR-004) |
| `reply_window` | `string` | ✗ | 最大長度 100 字元 | 回覆窗口(使用者填寫,FR-010) |
| `reply_content` | `string` | ✗ | 最大長度 1,000 字元 | 回覆內容(使用者填寫,FR-010) |
| `customer_notes` | `string` | ✗ | 最大長度 500 字元 | 客戶確認/修改處(使用者填寫,FR-010) |
| `generated_reply` | `string` | ✗ | 最大長度 1,000 字元 | 生成的回覆(預留空白,未來擴充,FR-013) |

**關聯性**:

- 多個 Comment 屬於一個 Post(多對一)

**狀態轉換**: 不適用(單次作業流程,無狀態機)

**唯一性規則**:

- `comment_id` 必須在系統中唯一
- 同一 `post_url` 下的 `commenter_id` + `comment_time` 組合應唯一(用於去重)

**範例**:

```json
{
  "comment_id": "550e8400-e29b-41d4-a716-446655440000",
  "post_url": "https://www.facebook.com/example/posts/123456789",
  "comment_time": "2025-11-13T14:35:20+08:00",
  "commenter_id": "張小明 (87654321)",
  "comment_content": "這個產品很棒!想了解更多資訊。",
  "reply_window": "客服 A",
  "reply_content": "感謝您的詢問,我們會盡快與您聯繫。",
  "customer_notes": "高優先客戶",
  "generated_reply": ""
}
```

---

### EditData(編輯資料)

**描述**: 邏輯實體,代表使用者手動填寫的欄位(實際儲存在 Comment 實體中)

**屬性**(對應至 Comment 欄位):

- `reply_window`: 回覆窗口
- `reply_content`: 回覆內容
- `customer_notes`: 客戶確認/修改處

**驗證規則**:

- 所有欄位皆為選填(使用者可選擇性填寫)
- 欄位長度限制同 Comment 定義
- 允許空字串(使用者可清空已填寫內容)

**關聯性**:

- EditData 與 Comment 是一對一關係(邏輯分離,實體合併)

---

## 資料流程

### 1. 爬取階段(Scraping Phase)

```text
使用者輸入 post_url
  ↓
後端爬蟲服務驗證 URL(FR-014)
  ↓
建立 Post 實體(爬取發文時間、內容、按讚數、留言總數)
  ↓
分批爬取留言(每批最多 100 則,間隔 3-5 秒,FR-018, FR-024)
  ↓
為每則留言建立 Comment 實體
  ↓
回傳給前端顯示於表格(FR-009)
```

**錯誤處理**:

- URL 無效 → 回傳 `InvalidURLError`(FR-014)
- 網路異常 → 回傳 `NetworkError`,允許重試(FR-015)
- 貼文無留言 → 回傳空的 `comments` 陣列,顯示提示(FR-016)
- 速率限制 → 回傳 `RateLimitError`,停止爬取(FR-025)

### 2. 編輯階段(Editing Phase)

```text
前端表格顯示所有 Comment
  ↓
使用者點擊欄位進行編輯(FR-010)
  ↓
前端即時更新狀態(Zustand)
  ↓
使用者可勾選並刪除 Comment(FR-011)
  ↓
所有變更僅存於瀏覽器記憶體(無後端持久化)
```

**資料保留規則**:

- 編輯內容不保存至資料庫
- 重新整理頁面會遺失所有編輯
- 使用者需在編輯後立即匯出(單次作業流程假設)

### 3. 匯出階段(Export Phase)

```text
使用者點擊「匯出 Excel」(FR-012)
  ↓
前端收集當前狀態的所有 Comment
  ↓
傳送至後端 API
  ↓
後端使用 openpyxl 生成 .xlsx 檔案
  ↓
檔名格式: {platform}_comments_{timestamp}.xlsx (FR-026, FR-027)
  ↓
回傳檔案供下載
```

**Excel 欄位對應**(FR-013):

| Excel 欄位標題 | 對應 Post/Comment 屬性 | 資料類型 |
|---------------|----------------------|---------|
| 發文時間 | `Post.post_time` | 日期時間 |
| 貼文連結 | `Post.post_url` | 超連結 |
| 貼文內容 | `Post.post_content` | 文字(自動換行) |
| 按讚數 | `Post.likes_count` | 數字 |
| 留言總數 | `Post.comments_count` | 數字 |
| 留言時間 | `Comment.comment_time` | 日期時間 |
| 留言者 ID | `Comment.commenter_id` | 文字 |
| 留言內容 | `Comment.comment_content` | 文字(自動換行) |
| 回覆窗口 | `Comment.reply_window` | 文字 |
| 回覆內容 | `Comment.reply_content` | 文字(自動換行) |
| 客戶確認/修改處 | `Comment.customer_notes` | 文字(自動換行) |
| 生成的回覆 | `Comment.generated_reply` | 文字(預留空白) |

---

## 資料驗證

### 後端驗證(Pydantic Models)

```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum

class PlatformEnum(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"

class Post(BaseModel):
    platform: PlatformEnum
    post_url: HttpUrl
    post_time: datetime
    post_content: str = Field(..., max_length=10000)
    likes_count: int = Field(..., ge=0)
    comments_count: int = Field(..., ge=0)

class Comment(BaseModel):
    comment_id: str  # UUID v4
    post_url: HttpUrl
    comment_time: datetime
    commenter_id: str = Field(..., max_length=200)
    comment_content: str = Field(..., max_length=5000)
    reply_window: str | None = Field(None, max_length=100)
    reply_content: str | None = Field(None, max_length=1000)
    customer_notes: str | None = Field(None, max_length=500)
    generated_reply: str | None = Field(None, max_length=1000)
```

### 前端驗證(TypeScript Interfaces)

```typescript
enum Platform {
  Facebook = "facebook",
  Instagram = "instagram"
}

interface Post {
  platform: Platform;
  post_url: string;
  post_time: string; // ISO 8601
  post_content: string;
  likes_count: number;
  comments_count: number;
}

interface Comment {
  comment_id: string;
  post_url: string;
  comment_time: string; // ISO 8601
  commenter_id: string;
  comment_content: string;
  reply_window?: string;
  reply_content?: string;
  customer_notes?: string;
  generated_reply?: string;
}
```

---

## 擴充性考量

為未來擴充方向(規格中列出但第一階段不實作)保留的設計空間:

1. **留言分類**: `Comment` 可新增 `category` 欄位(如 "FAQ", "客訴", "詢價")
2. **責任分配**: `reply_window` 可改為外鍵關聯至 `User` 實體
3. **自動回應**: `generated_reply` 欄位已預留,未來可整合 LLM API
4. **批次爬取**: `Post` 可新增 `scraping_session_id` 以追蹤批次作業
5. **歷史記錄**: 若需保存歷史,可新增 `ScrapingSession` 實體與持久化儲存

目前設計保持簡單(符合「避免過度工程」限制),但結構清晰可擴充。
