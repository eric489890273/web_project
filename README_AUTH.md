# 登入/註冊與歷史記錄功能說明

## 新增功能

### 1. 使用者認證系統
- **註冊**: `/register` - 新使用者註冊頁面
  - 需要提供使用者名稱(最少3個字元)、電子郵件和密碼(最少6個字元)
  - 密碼使用 werkzeug 加密存儲

- **登入**: `/login` - 使用者登入頁面
  - 使用使用者名稱和密碼登入
  - 登入後會建立 session

- **登出**: `/logout` - 登出功能
  - 清除使用者 session

### 2. 運動數據歷史記錄
- **儲存分析結果**: 在運動數據分析頁面(/statistics)完成分析後,可以選擇將結果儲存到個人歷史記錄
  - 只有登入的使用者才能儲存數據
  - 儲存的數據包括:
    - 運動類型、時長、體重、身高、年齡、性別
    - 心率、體溫
    - 計算結果:消耗卡路里、MET值、心率區間、效率分數

- **查看歷史記錄**: `/history` - 查看個人所有運動歷史記錄
  - 顯示統計卡片:總記錄數、總消耗卡路里、總運動時長、平均效率
  - 兩個圖表:
    - 卡路里消耗趨勢圖(折線圖)
    - 運動時長分布圖(柱狀圖)
  - 完整的記錄表格,可以排序
  - 每筆記錄都可以刪除

- **刪除記錄**: `/delete_history/<record_id>` - 刪除指定的歷史記錄
  - 只能刪除自己的記錄

### 3. 導航欄更新
所有頁面的導航欄現在會顯示:
- 未登入時:顯示「登入」和「註冊」按鈕
- 已登入時:顯示使用者名稱、「歷史記錄」連結和「登出」按鈕

## 資料庫結構

### users 表
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- 加密後的密碼
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### exercise_history 表
```sql
CREATE TABLE exercise_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_type TEXT NOT NULL,
    duration INTEGER NOT NULL,
    weight REAL,
    height REAL,
    age INTEGER,
    gender TEXT,
    heart_rate INTEGER,
    temperature REAL,
    calories REAL,
    met REAL,
    heart_rate_zone TEXT,
    efficiency_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

## 檔案變更

### 新增的檔案
1. `templates/login.html` - 登入頁面
2. `templates/register.html` - 註冊頁面
3. `templates/history.html` - 歷史記錄頁面
4. `data/users.db` - SQLite 資料庫(首次執行時自動創建)

### 修改的檔案
1. `app.py` - 新增認證和歷史記錄相關路由
2. `templates/index.html` - 更新導航欄
3. `templates/statistics.html` - 新增儲存功能和更新導航欄

## 使用流程

1. **首次使用**
   - 訪問 `/register` 註冊新帳號
   - 註冊成功後自動跳轉到登入頁面

2. **登入**
   - 訪問 `/login` 輸入使用者名稱和密碼
   - 登入成功後跳轉到首頁

3. **使用運動分析**
   - 訪問 `/statistics` 進行運動數據分析
   - 填寫表單並點擊「開始分析」
   - 查看分析結果

4. **儲存記錄**
   - 在分析結果下方點擊「保存此次分析到歷史記錄」
   - 系統會將完整的分析數據儲存到資料庫

5. **查看歷史**
   - 點擊導航欄的「歷史記錄」或分析結果下方的「查看歷史記錄」
   - 查看所有歷史記錄、圖表和統計數據

6. **管理記錄**
   - 在歷史記錄頁面可以刪除不需要的記錄

## 安全性

- 密碼使用 `werkzeug.security` 的 `generate_password_hash` 加密
- 使用 Flask session 管理使用者登入狀態
- 需要登入才能儲存和查看歷史記錄
- 使用者只能查看和刪除自己的記錄

## 技術棧

- **後端**: Flask 3.0.0
- **資料庫**: SQLite3
- **密碼加密**: werkzeug.security
- **前端**: Tailwind CSS, Chart.js (用於圖表)
- **模板引擎**: Jinja2
