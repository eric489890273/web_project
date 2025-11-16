# 籃球數據分析 - PER 更新說明

## 更新內容

### 1. 從 EFF 改為 PER
- **舊指標**: 效率值 (EFF - Efficiency Rating)
  - 公式: PTS + REB + AST + STL + BLK - (FGA - FGM) - (FTA - FTM) - TO
  - 問題: 單場數據無法準確反映球員效率

- **新指標**: PER (Player Efficiency Rating)
  - 公式: `[(得分+助攻+籃板+抄截+阻攻)-(投籃出手數-投籃命中數)-(罰球出手數-罰球命中數)-失誤數] / 總出場場次`
  - 優勢: 需要除以場次,更能反映球員的穩定表現

### 2. 顯示位置調整
- **單次分析頁面 (basketball_stats.html)**:
  - ❌ 不再顯示效率值卡片
  - ✅ 只顯示: 總得分、投籃命中率、三分命中率
  - ✅ 詳細分析區保留: 投籃分析、全能數據、效率指標、建議
  - ✅ 效率指標區移除 EFF 項目

- **歷史記錄頁面 (basketball_history.html)**:
  - ✅ 統計卡片顯示「平均 PER」
  - ✅ 表格中顯示每場的 PER 值
  - ✅ PER 在後端計算,根據總場次動態計算

### 3. 數據庫結構變更
```sql
-- 移除欄位
- efficiency_rating REAL

-- basketball_history 表現在包含:
- id, user_id, play_time
- fga, fgm, fg_pct
- three_pa, three_pm, three_pct
- fta, ftm, ft_pct
- rebounds, assists, steals, blocks, turnovers
- points
- true_shooting_pct, assist_ratio, turnover_ratio
- created_at
```

### 4. 後端計算邏輯 (app.py)
```python
# 在 basketball_history() 路由中計算 PER
total_games = len(records)

for record in records:
    per = 0
    if total_games > 0:
        per = (
            (record['points'] + record['assists'] + record['rebounds'] +
             record['steals'] + record['blocks']) -
            (record['fga'] - record['fgm']) -
            (record['fta'] - record['ftm']) -
            record['turnovers']
        ) / total_games
```

### 5. 前端調整
- **basketball_stats.html**:
  - 移除效率值主卡片
  - 移除效率值顯示區塊
  - JavaScript 不再計算和顯示 efficiency
  - 保存數據時不包含 efficiency_rating

- **basketball_history.html**:
  - 表頭: "效率值" → "PER"
  - 顯示格式: `{{ "%.1f"|format(record.per) }}`
  - 統計卡片: "平均效率值" → "平均 PER"

## 遷移步驟

1. ✅ 修改 `app.py` 中的數據庫結構定義
2. ✅ 更新 `save_basketball` 路由,移除 efficiency_rating
3. ✅ 更新 `basketball_history` 路由,添加 PER 計算
4. ✅ 修改 `basketball_stats.html`,移除效率值顯示
5. ✅ 修改 `basketball_history.html`,改為顯示 PER
6. ✅ 執行數據庫遷移腳本 `migrate_basketball_db.py`
7. ✅ 備份舊數據庫到 `data/users_backup.db`

## 影響範圍
- ✅ 單次分析頁: 簡化顯示,更專注於命中率
- ✅ 歷史記錄頁: 顯示更有意義的 PER 指標
- ✅ 數據庫: 減少冗余欄位
- ✅ 後端計算: PER 動態計算,始終準確

## 優勢
1. **更準確的效率評估**: PER 基於總場次,避免單場極端值影響
2. **簡化單次分析**: 用戶專注於命中率等即時指標
3. **歷史數據更有價值**: PER 能更好地反映長期表現趨勢
4. **數據庫優化**: 移除可計算欄位,減少存儲冗余

## 測試檢查清單
- [ ] 單次分析頁面正常顯示(無效率值卡片)
- [ ] 保存數據成功(不含 efficiency_rating)
- [ ] 歷史記錄頁面顯示 PER
- [ ] PER 計算正確(= 單場數據總和 / 總場次)
- [ ] 舊數據正常遷移
- [ ] 新數據正常保存和顯示

## 備註
- 舊數據庫已備份至 `data/users_backup.db`
- 如需回滾,可停止應用後恢復備份
- PER 公式可根據需要進一步調整
