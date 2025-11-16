# 籃球數據分析功能說明

## 新增功能概述

已成功為個人運動數據分析系統添加了專門的籃球數據分析功能,包括完整的數據輸入、分析計算、歷史記錄和可視化圖表功能。

## 功能詳細說明

### 1. 籃球數據分析頁面 (`/basketball_stats`)

#### 數據輸入欄位:
- **比賽時間**: 上場時間(分鐘)
- **投籃數據**:
  - 投籃命中數 (FGM)
  - 投籃出手數 (FGA)
  - 三分命中數 (3PM)
  - 三分出手數 (3PA)
  - 罰球命中數 (FTM)
  - 罰球出手數 (FTA)
- **全能數據**:
  - 籃板數 (REB)
  - 助攻數 (AST)
  - 抄截數 (STL)
  - 阻攻數 (BLK)
  - 失誤數 (TO)

#### 計算指標:
1. **總得分** = (FGM - 3PM) × 2 + 3PM × 3 + FTM
2. **投籃命中率** = FGM / FGA × 100%
3. **三分命中率** = 3PM / 3PA × 100%
4. **罰球命中率** = FTM / FTA × 100%
5. **真實命中率 (TS%)** = PTS / (2 × (FGA + 0.44 × FTA)) × 100%
6. **效率值 (EFF)** = PTS + REB + AST + STL + BLK - (FGA - FGM) - (FTA - FTM) - TO
7. **助攻率** = AST / (FGA + 0.44 × FTA + TO) × 100%
8. **失誤率** = TO / (FGA + 0.44 × FTA + TO) × 100%
9. **場均得分** = PTS / 上場時間

#### 分析結果展示:
- **主要數據卡片** (4個):
  - 總得分 (橙色漸層)
  - 投籃命中率 (綠色漸層)
  - 三分命中率 (黃色漸層)
  - 效率值 (紫色漸層)

- **詳細分析區塊**:
  - 投籃分析: 投籃%、三分%、罰球%、真實命中率
  - 全能數據: 籃板、助攻、抄截、阻攻
  - 效率指標: 效率值、助攻率、失誤率、場均得分
  - 改進建議: 基於數據自動生成的個性化建議

#### 智能建議系統:
根據表現自動生成建議:
- 投籃命中率 < 40%: 建議加強基本動作訓練
- 投籃命中率 ≥ 50%: 表揚優秀表現
- 三分命中率 < 30%: 建議加強三分訓練或減少出手
- 三分命中率 ≥ 40%: 表揚職業級水準
- 罰球命中率 < 70%: 建議多練習罰球
- 效率值 < 10: 建議提高命中率並減少失誤
- 效率值 ≥ 20: 表揚全能表現
- 失誤率 > 20%: 提醒注意保護球
- 助攻 ≥ 5: 表揚組織能力
- 抄截+阻攻 ≥ 3: 表揚防守積極性

### 2. 籃球歷史記錄頁面 (`/basketball_history`)

#### 統計卡片:
- **總記錄數**: 顯示所有籃球數據記錄總數
- **總得分**: 累計所有比賽的總得分
- **平均命中率**: 所有記錄的平均投籃命中率
- **平均效率值**: 所有記錄的平均效率值

#### 趨勢圖表 (使用 Chart.js):
1. **得分趨勢圖** (折線圖)
   - 橙色線條
   - 顯示每次比賽的得分變化
   - 可視化進步或退步趨勢

2. **命中率趨勢圖** (雙折線圖)
   - 綠色: 投籃命中率
   - 黃色: 三分命中率
   - Y軸範圍 0-100%
   - 方便比較兩種命中率的變化

#### 完整記錄表格:
顯示欄位:
- 日期時間
- 比賽時長
- 得分 (橙色高亮)
- 投籃命中率 (顏色標示: ≥50%綠色, ≥40%黃色, <40%灰色)
- 三分命中率 (顏色標示: ≥40%綠色, ≥30%黃色, <30%灰色)
- 罰球命中率 (顏色標示: ≥80%綠色, ≥70%黃色, <70%灰色)
- 籃板數
- 助攻數
- 抄截數
- 效率值 (紫色高亮)
- 刪除按鈕

### 3. 頁面切換功能

#### 在分析頁面:
- **statistics.html**:
  - 左按鈕(紫粉漸層,當前頁): 運動數據分析
  - 右按鈕(灰色): 籃球數據分析

- **basketball_stats.html**:
  - 左按鈕(灰色): 運動數據分析
  - 右按鈕(橙紅漸層,當前頁): 籃球數據分析

#### 在歷史記錄頁面:
- **history.html**:
  - 左按鈕(紫粉漸層,當前頁): 運動數據歷史
  - 右按鈕(灰色): 籃球數據歷史

- **basketball_history.html**:
  - 左按鈕(灰色): 運動數據歷史
  - 右按鈕(橙紅漸層,當前頁): 籃球數據歷史

### 4. 數據庫結構

新增 `basketball_history` 表:

```sql
CREATE TABLE basketball_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    play_time INTEGER NOT NULL,           -- 上場時間
    fga INTEGER,                           -- 投籃出手
    fgm INTEGER,                           -- 投籃命中
    fg_pct REAL,                          -- 投籃命中率
    three_pa INTEGER,                      -- 三分出手
    three_pm INTEGER,                      -- 三分命中
    three_pct REAL,                       -- 三分命中率
    fta INTEGER,                           -- 罰球出手
    ftm INTEGER,                           -- 罰球命中
    ft_pct REAL,                          -- 罰球命中率
    rebounds INTEGER,                      -- 籃板
    assists INTEGER,                       -- 助攻
    steals INTEGER,                        -- 抄截
    blocks INTEGER,                        -- 阻攻
    turnovers INTEGER,                     -- 失誤
    points INTEGER,                        -- 總得分
    efficiency_rating REAL,                -- 效率值
    true_shooting_pct REAL,                -- 真實命中率
    assist_ratio REAL,                     -- 助攻率
    turnover_ratio REAL,                   -- 失誤率
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

### 5. 新增路由

```python
# 籃球數據分析頁面
@app.route('/basketball_stats')
def basketball_stats()

# 保存籃球數據
@app.route('/save_basketball', methods=['POST'])
def save_basketball()

# 籃球歷史記錄頁面
@app.route('/basketball_history')
def basketball_history()

# 刪除籃球歷史記錄
@app.route('/delete_basketball_history/<int:record_id>', methods=['POST'])
def delete_basketball_history(record_id)
```

## 設計特色

### 視覺設計:
- **配色方案**: 橙紅色系(籃球主題) vs 紫粉色系(運動主題)
- **圖標**: 使用 Font Awesome 6.4.0 的籃球相關圖標
- **漸層效果**: 主要按鈕使用橙到紅的漸層
- **懸浮效果**: 卡片懸浮時上移並加深陰影
- **顏色編碼**:
  - 命中率使用綠/黃/灰三色標示水準
  - 不同數據類型使用不同顏色高亮

### 用戶體驗:
1. **直觀的切換**: 在分析頁和歷史頁都有清晰的切換按鈕
2. **即時反饋**: 分析後立即顯示結果和保存選項
3. **視覺化數據**: 使用圖表展示趨勢,更易理解
4. **智能建議**: 根據表現自動生成個性化建議
5. **響應式設計**: 支援桌面和移動設備
6. **平滑動畫**: 結果顯示時有淡入動畫

### 數據安全:
- 需要登入才能保存和查看歷史
- 用戶只能查看和刪除自己的記錄
- 使用 session 驗證用戶身份

## 使用流程

1. **登入系統**: 訪問 `/login`
2. **選擇分析類型**:
   - 運動數據分析: `/statistics`
   - 籃球數據分析: `/basketball_stats`
3. **輸入數據**: 填寫比賽的各項數據
4. **查看分析**: 點擊「開始分析」查看詳細結果
5. **保存記錄**: 點擊「保存此次分析到歷史記錄」
6. **查看歷史**:
   - 運動數據歷史: `/history`
   - 籃球數據歷史: `/basketball_history`
7. **管理記錄**: 可以刪除不需要的歷史記錄

## 技術棧

- **後端**: Flask 3.0.0 + SQLite3
- **前端**: Tailwind CSS 3.x
- **圖表**: Chart.js
- **圖標**: Font Awesome 6.4.0
- **模板**: Jinja2

## 應用程式狀態

✅ 應用程式已啟動: http://127.0.0.1:5000
✅ 資料庫已初始化: `data/users.db`
✅ 所有功能已測試通過
✅ 頁面切換功能正常運作

## 文件列表

### 新增文件:
1. `templates/basketball_stats.html` - 籃球數據分析頁面
2. `templates/basketball_history.html` - 籃球歷史記錄頁面

### 修改文件:
1. `app.py` - 新增籃球相關路由和資料庫表
2. `templates/statistics.html` - 新增切換按鈕
3. `templates/history.html` - 新增切換按鈕

### 資料庫:
- `data/users.db` - 新增 `basketball_history` 表

所有功能已完整實現並可正常使用! 🏀
