# 籃球運動員分析網站

一個使用 Flask 構建的現代化籃球數據分析平台，提供球員分析、即時比分和數據統計功能。

## 功能特色

### 🏀 球員分析
- 球員資料查詢與篩選
- 詳細的個人數據展示
- 數據趨勢圖表
- 命中率可視化

### 🏆 賽事比分
- 即時比賽比分更新
- 進行中/即將開始/已結束比賽分類
- 各節詳細比分
- 比賽統計數據

### 📊 數據分析
- 個人數據總覽
- 多維度數據圖表
- 進階數據分析
- 對位表現統計

## 技術棧

- **後端**: Flask 3.0
- **前端**: HTML5, Tailwind CSS
- **圖表**: Chart.js
- **圖示**: Font Awesome 6.4

## 安裝步驟

### 1. 克隆專案
```bash
cd c:\Users\user\Desktop\web_project
```

### 2. 創建虛擬環境（推薦）
```bash
python -m venv venv
```

### 3. 啟動虛擬環境

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. 安裝依賴
```bash
pip install -r requirements.txt
```

## 運行應用

### 開發模式
```bash
python app.py
```

應用將在 `http://localhost:5000` 啟動

### 生產模式
```bash
set FLASK_ENV=production
python app.py
```

## 專案結構

```
web_project/
│
├── app.py                 # Flask 應用主程式
├── requirements.txt       # Python 依賴
├── README.md             # 專案說明文件
│
├── templates/            # HTML 模板
│   ├── index.html           # 首頁
│   ├── player_analysis.html # 球員分析頁面
│   ├── live_scores.html     # 賽事比分頁面
│   └── statistics.html      # 數據分析頁面
│
└── static/               # 靜態資源（可選）
    ├── css/
    ├── js/
    └── images/
```

## API 端點

### 球員相關
- `GET /api/players` - 獲取所有球員列表
- `GET /api/player/<id>` - 獲取單個球員詳情
- `GET /api/player/<id>/games` - 獲取球員最近比賽數據

### 比賽相關
- `GET /api/games` - 獲取所有比賽
- `GET /api/games/live` - 獲取進行中的比賽（即時更新）

### 統計相關
- `GET /api/statistics` - 獲取統計數據
- `GET /api/statistics/trend` - 獲取數據趨勢

## 頁面路由

- `/` - 首頁
- `/player_analysis` - 球員分析
- `/live_scores` - 賽事比分
- `/statistics` - 數據分析

## 特色功能

### 即時更新
比賽比分支援模擬即時更新，每次請求 `/api/games/live` 都會返回動態變化的比分。

### 響應式設計
使用 Tailwind CSS 構建，完美支援桌面、平板和移動設備。

### 動畫效果
- 淡入淡出動畫
- 滑動效果
- Hover 互動
- 脈衝動畫（LIVE 標記）

### 數據可視化
使用 Chart.js 提供多種圖表：
- 折線圖（趨勢分析）
- 圓餅圖（投籃分布）
- 雷達圖（五維能力）
- 進度條（命中率）

## 開發說明

### 添加新球員
在 `app.py` 的 `PLAYERS_DATA` 列表中添加新的字典：

```python
{
    'id': 5,
    'name': '球員姓名',
    'team': '球隊名稱',
    'position': '位置',
    'number': '號碼',
    'ppg': 得分,
    'apg': 助攻,
    'rpg': 籃板,
    'fg_pct': 命中率,
    'three_pct': 三分命中率
}
```

### 修改模板
HTML 模板位於 `templates/` 目錄，可以直接編輯修改樣式和內容。

### 添加新 API
在 `app.py` 中使用 `@app.route()` 裝飾器添加新的路由。

## 瀏覽器支援

- Chrome (推薦)
- Firefox
- Safari
- Edge

## 授權

MIT License

## 作者

籃球分析系統開發團隊

## 更新日誌

### v1.0.0 (2025-11-06)
- 初始版本發布
- 實現基礎功能
- 添加 API 支援
- 完成響應式設計
