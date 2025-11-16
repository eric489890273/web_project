import sqlite3
import os

def migrate_database():
    """遷移數據庫,移除 efficiency_rating 欄位"""
    db_path = 'data/users.db'

    if not os.path.exists(db_path):
        print("數據庫文件不存在")
        return

    # 備份
    backup_path = 'data/users_backup.db'
    import shutil
    if os.path.exists(backup_path):
        os.remove(backup_path)
    shutil.copy(db_path, backup_path)
    print(f"已備份數據庫到 {backup_path}")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # 檢查是否有 efficiency_rating 欄位
        c.execute("PRAGMA table_info(basketball_history)")
        columns = [col[1] for col in c.fetchall()]

        if 'efficiency_rating' in columns:
            print("檢測到 efficiency_rating 欄位,開始遷移...")

            # 創建新表
            c.execute('''
                CREATE TABLE IF NOT EXISTS basketball_history_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    play_time INTEGER NOT NULL,
                    fga INTEGER,
                    fgm INTEGER,
                    fg_pct REAL,
                    three_pa INTEGER,
                    three_pm INTEGER,
                    three_pct REAL,
                    fta INTEGER,
                    ftm INTEGER,
                    ft_pct REAL,
                    rebounds INTEGER,
                    assists INTEGER,
                    steals INTEGER,
                    blocks INTEGER,
                    turnovers INTEGER,
                    points INTEGER,
                    true_shooting_pct REAL,
                    assist_ratio REAL,
                    turnover_ratio REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # 複製數據(不包括 efficiency_rating)
            c.execute('''
                INSERT INTO basketball_history_new
                (id, user_id, play_time, fga, fgm, fg_pct, three_pa, three_pm, three_pct,
                 fta, ftm, ft_pct, rebounds, assists, steals, blocks, turnovers, points,
                 true_shooting_pct, assist_ratio, turnover_ratio, created_at)
                SELECT id, user_id, play_time, fga, fgm, fg_pct, three_pa, three_pm, three_pct,
                       fta, ftm, ft_pct, rebounds, assists, steals, blocks, turnovers, points,
                       true_shooting_pct, assist_ratio, turnover_ratio, created_at
                FROM basketball_history
            ''')

            # 刪除舊表
            c.execute('DROP TABLE basketball_history')

            # 重命名新表
            c.execute('ALTER TABLE basketball_history_new RENAME TO basketball_history')

            conn.commit()
            print("遷移成功!已移除 efficiency_rating 欄位")
        else:
            print("數據庫已是最新版本,無需遷移")

    except Exception as e:
        conn.rollback()
        print(f"遷移失敗: {e}")
        # 恢復備份
        conn.close()
        if os.path.exists(backup_path):
            os.remove(db_path)
            shutil.copy(backup_path, db_path)
            print("已從備份恢復數據庫")
        return

    conn.close()
    print("數據庫遷移完成!")

if __name__ == '__main__':
    migrate_database()
