# Pre-commit Hooks 設置指南

## 安裝

### 1. 安裝 pre-commit

```powershell
# 在專案根目錄
pip install pre-commit
```

### 2. 安裝 hooks 到 git

```powershell
pre-commit install
pre-commit install --hook-type commit-msg
```

### 3. (可選) 手動執行所有檢查

```powershell
pre-commit run --all-files
```

## Hooks 說明

### 自動執行時機

- **Pre-commit**: 每次 `git commit` 前自動執行
- **Commit-msg**: 檢查 commit 訊息格式

### 檢查項目

#### 通用檢查
- 移除尾隨空白
- 檔案結尾換行
- YAML/JSON/TOML 格式驗證
- 大檔案檢查 (>1MB)
- 合併衝突標記

#### 後端 (Python)
- **Ruff**: Linting 與自動修正
- **Black**: 程式碼格式化
- **mypy**: 型別檢查

#### 前端 (TypeScript)
- **ESLint**: Linting 與自動修正
- **Prettier**: 程式碼格式化

#### Commit 訊息
- 符合 Conventional Commits 格式
- 格式: `type(scope): description`
- 類型: feat, fix, docs, style, refactor, test, chore

## 跳過 Hooks (緊急情況)

```powershell
# 跳過所有 hooks
git commit --no-verify -m "message"

# 跳過特定 hook
SKIP=eslint git commit -m "message"
```

## 更新 Hooks

```powershell
pre-commit autoupdate
```

## 疑難排解

### Hook 失敗
1. 檢查錯誤訊息
2. 手動執行該 hook: `pre-commit run <hook-id> --all-files`
3. 修正問題後重新 commit

### Node.js hooks 問題
確保 frontend/node_modules 已安裝:
```powershell
cd frontend
npm install
```

### Python hooks 問題
確保虛擬環境已啟動並安裝依賴:
```powershell
cd backend
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```
