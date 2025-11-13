# 環境設置指南

## 前置需求

### 後端 (Python 3.11+)

**Python 尚未安裝**。請依照以下步驟安裝：

1. **下載 Python 3.11+**:
   - 前往 https://www.python.org/downloads/
   - 下載 Python 3.11 或更新版本
   - ✅ 勾選 "Add Python to PATH"

2. **驗證安裝**:
   ```powershell
   python --version  # 應顯示 Python 3.11.x 或更高
   ```

3. **建立虛擬環境**:
   ```powershell
   cd backend
   python -m venv venv
   ```

4. **啟動虛擬環境**:
   ```powershell
   # PowerShell
   .\venv\Scripts\Activate.ps1
   
   # 如果遇到執行政策錯誤,執行:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

5. **安裝相依套件**:
   ```powershell
   pip install -r requirements.txt
   ```

6. **安裝 Playwright 瀏覽器**:
   ```powershell
   playwright install chromium firefox
   ```

7. **驗證測試環境**:
   ```powershell
   pytest --version
   ```

### 前端 (Node.js 18+)

1. **安裝 Node.js**:
   - 前往 https://nodejs.org/
   - 下載 LTS 版本 (18.x 或更新)

2. **驗證安裝**:
   ```powershell
   node --version  # 應顯示 v18.x.x 或更高
   npm --version
   ```

3. **安裝相依套件**:
   ```powershell
   cd frontend
   npm install
   ```

4. **驗證測試環境**:
   ```powershell
   npm test -- --version
   ```

## 開發工作流程

### 後端開發

```powershell
cd backend

# 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 執行測試 (TDD watch mode)
pytest --watch --tb=short

# 執行 linter
ruff check .

# 執行 formatter
black .

# 啟動開發伺服器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端開發

```powershell
cd frontend

# 執行測試 (watch mode)
npm test -- --watch

# 執行 linter
npm run lint

# 執行 formatter
npm run format

# 啟動開發伺服器
npm run dev
```

## 目前狀態

✅ **T001 完成**: 專案目錄結構已建立
✅ **T002-T005 部分完成**: 配置檔案已建立

❌ **待完成**:
- 安裝 Python 3.11+
- 安裝 Node.js 18+
- 建立 Python 虛擬環境
- 安裝後端相依套件
- 安裝 Playwright 瀏覽器
- 安裝前端相依套件

## 下一步

1. 安裝 Python 3.11+ 與 Node.js 18+
2. 執行上述安裝指令
3. 繼續 T006: 設置 CI/CD 管道
