from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import csv
import os
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # 請在生產環境中更改此密鑰

# 資料庫初始化
def init_db():
    """初始化資料庫"""
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()

    # 用戶表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 運動數據歷史記錄表
    c.execute('''
        CREATE TABLE IF NOT EXISTS exercise_history (
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
    ''')

    conn.commit()
    conn.close()

# 初始化資料庫
init_db()

# 載入真實球員數據
def load_players_data():
    """從 CSV 檔案載入球員數據"""
    players = []
    csv_path = os.path.join('data', 'nba_traditional_stats_2025_26.csv')

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 計算場均數據
                gp = float(row['GP']) if row['GP'] else 1

                player = {
                    'id': row['PLAYER_ID'],
                    'name': row['PLAYER_NAME'],
                    'nickname': row['NICKNAME'] if row['NICKNAME'] else row['PLAYER_NAME'],
                    'team': row['TEAM_ABBREVIATION'],
                    'age': row['AGE'],
                    'gp': int(float(row['GP'])) if row['GP'] else 0,
                    'min': round(float(row['MIN']) / gp, 1) if row['MIN'] else 0,
                    'ppg': round(float(row['PTS']) / gp, 1) if row['PTS'] else 0,
                    'apg': round(float(row['AST']) / gp, 1) if row['AST'] else 0,
                    'rpg': round(float(row['REB']) / gp, 1) if row['REB'] else 0,
                    'fg_pct': round(float(row['FG_PCT']) * 100, 1) if row['FG_PCT'] else 0,
                    'three_pct': round(float(row['FG3_PCT']) * 100, 1) if row['FG3_PCT'] else 0,
                    'ft_pct': round(float(row['FT_PCT']) * 100, 1) if row['FT_PCT'] else 0,
                    'stl': round(float(row['STL']) / gp, 1) if row['STL'] else 0,
                    'blk': round(float(row['BLK']) / gp, 1) if row['BLK'] else 0,
                    'tov': round(float(row['TOV']) / gp, 1) if row['TOV'] else 0,
                    'pf': round(float(row['PF']) / gp, 1) if row['PF'] else 0,
                    'plus_minus': round(float(row['PLUS_MINUS']) / gp, 1) if row['PLUS_MINUS'] else 0,
                    # 原始總數據
                    'total_pts': int(float(row['PTS'])) if row['PTS'] else 0,
                    'total_ast': int(float(row['AST'])) if row['AST'] else 0,
                    'total_reb': int(float(row['REB'])) if row['REB'] else 0,
                    'fgm': round(float(row['FGM']) / gp, 1) if row['FGM'] else 0,
                    'fga': round(float(row['FGA']) / gp, 1) if row['FGA'] else 0,
                    'fg3m': round(float(row['FG3M']) / gp, 1) if row['FG3M'] else 0,
                    'fg3a': round(float(row['FG3A']) / gp, 1) if row['FG3A'] else 0,
                    'ftm': round(float(row['FTM']) / gp, 1) if row['FTM'] else 0,
                    'fta': round(float(row['FTA']) / gp, 1) if row['FTA'] else 0,
                    'oreb': round(float(row['OREB']) / gp, 1) if row['OREB'] else 0,
                    'dreb': round(float(row['DREB']) / gp, 1) if row['DREB'] else 0,
                    'avatar': 'https://via.placeholder.com/80'
                }
                players.append(player)
    except Exception as e:
        print(f"載入球員數據失敗: {e}")
        return []

    # 按得分排序
    players.sort(key=lambda x: x['ppg'], reverse=True)

    # 獲取所有球隊列表
    teams = sorted(list(set(p['team'] for p in players)))

    return players, teams

def load_multi_year_data(player_id):
    """載入球員多年數據用於趨勢分析"""
    years_data = {}
    csv_files = {
        '2021-22': 'nba_traditional_stats_2021_22.csv',
        '2022-23': 'nba_traditional_stats_2022_23.csv',
        '2023-24': 'nba_traditional_stats_2023_24.csv',
        '2024-25': 'nba_traditional_stats_2024_25.csv',
        '2025-26': 'nba_traditional_stats_2025_26.csv'
    }

    for year, filename in csv_files.items():
        csv_path = os.path.join('data', filename)
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if str(row['PLAYER_ID']) == str(player_id):
                        gp = float(row['GP']) if row['GP'] else 1
                        years_data[year] = {
                            'ppg': round(float(row['PTS']) / gp, 1) if row['PTS'] else 0,
                            'apg': round(float(row['AST']) / gp, 1) if row['AST'] else 0,
                            'rpg': round(float(row['REB']) / gp, 1) if row['REB'] else 0,
                            'fg_pct': round(float(row['FG_PCT']) * 100, 1) if row['FG_PCT'] else 0,
                            'three_pct': round(float(row['FG3_PCT']) * 100, 1) if row['FG3_PCT'] else 0,
                            'ft_pct': round(float(row['FT_PCT']) * 100, 1) if row['FT_PCT'] else 0,
                            'stl': round(float(row['STL']) / gp, 1) if row['STL'] else 0,
                            'blk': round(float(row['BLK']) / gp, 1) if row['BLK'] else 0,
                            'gp': int(float(row['GP'])) if row['GP'] else 0,
                            'min': round(float(row['MIN']) / gp, 1) if row['MIN'] else 0,
                        }
                        break
        except Exception as e:
            print(f"載入 {year} 數據失敗: {e}")
            continue

    return years_data

# 載入球員數據
PLAYERS_DATA, TEAMS_LIST = load_players_data()

# 模擬比賽數據
GAMES_DATA = {
    'live': [
        {
            'id': 1,
            'home_team': '洛杉磯湖人',
            'away_team': '金州勇士',
            'home_score': 108,
            'away_score': 105,
            'quarter': 'Q4',
            'time': '2:34',
            'status': 'live',
            'quarter_scores': {
                'home': [28, 26, 27, 27],
                'away': [25, 28, 24, 28]
            }
        },
        {
            'id': 2,
            'home_team': '波士頓塞爾提克',
            'away_team': '邁阿密熱火',
            'home_score': 95,
            'away_score': 89,
            'quarter': 'Q3',
            'time': '8:12',
            'status': 'live',
            'quarter_scores': {
                'home': [24, 28, 23, 0],
                'away': [22, 25, 22, 0]
            }
        }
    ],
    'upcoming': [
        {
            'id': 3,
            'home_team': '布魯克林籃網',
            'away_team': '芝加哥公牛',
            'start_time': '19:30',
            'status': 'upcoming'
        },
        {
            'id': 4,
            'home_team': '鳳凰城太陽',
            'away_team': '達拉斯獨行俠',
            'start_time': '20:00',
            'status': 'upcoming'
        }
    ],
    'finished': [
        {
            'id': 5,
            'home_team': '洛杉磯快艇',
            'away_team': '丹佛金塊',
            'home_score': 112,
            'away_score': 118,
            'status': 'finished',
            'time_ago': '2小時前'
        },
        {
            'id': 6,
            'home_team': '密爾瓦基公鹿',
            'away_team': '費城76人',
            'home_score': 128,
            'away_score': 119,
            'status': 'finished',
            'time_ago': '3小時前'
        }
    ]
}

# 統計數據
STATISTICS_DATA = {
    'overview': {
        'ppg': 28.5,
        'ppg_change': 2.3,
        'fg_pct': 45.8,
        'fg_pct_change': 1.5,
        'apg': 7.2,
        'apg_change': -0.5,
        'rpg': 9.1,
        'rpg_change': 0.8
    },
    'shooting': {
        'two_pt': 52.3,
        'three_pt': 38.6,
        'ft': 87.5,
        'efg': 56.8,
        'ts': 60.2
    },
    'advanced': {
        'ortg': 118.5,
        'usg': 29.8,
        'ast_pct': 32.1,
        'tov_pct': 12.3,
        'drtg': 108.2,
        'drb_pct': 75.6,
        'stl_pct': 2.1,
        'blk_pct': 1.8,
        'per': 24.7,
        'ws': 8.3,
        'plus_minus': 8.5,
        'net_rtg': 10.3
    }
}

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

# ========== 用戶認證路由 ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登入頁面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('登入成功!', 'success')
            return redirect(url_for('index'))
        else:
            flash('用戶名或密碼錯誤', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """註冊頁面"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 驗證
        if password != confirm_password:
            flash('兩次密碼輸入不一致', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('密碼長度至少6個字符', 'error')
            return render_template('register.html')

        # 檢查用戶是否已存在
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        existing_user = c.fetchone()

        if existing_user:
            flash('用戶名或郵箱已被使用', 'error')
            conn.close()
            return render_template('register.html')

        # 創建新用戶
        hashed_password = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                 (username, email, hashed_password))
        conn.commit()
        conn.close()

        flash('註冊成功!請登入', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    flash('已成功登出', 'success')
    return redirect(url_for('index'))

# ========== 原有路由 ==========

@app.route('/player_analysis')
def player_analysis():
    """球員分析頁面"""
    return render_template('player_analysis.html', players=PLAYERS_DATA, teams=TEAMS_LIST)

@app.route('/player/<player_id>')
def player_detail(player_id):
    """球員詳細分析頁面"""
    player = next((p for p in PLAYERS_DATA if str(p['id']) == str(player_id)), None)
    if player:
        # 準備雷達圖數據(歸一化到0-100)
        max_stats = {
            'ppg': 35,  # 假設最高得分35
            'apg': 12,  # 假設最高助攻12
            'rpg': 15,  # 假設最高籃板15
            'stl': 2.5, # 假設最高抄截2.5
            'blk': 3    # 假設最高阻攻3
        }

        radar_stats = [
            min(round((player['ppg'] / max_stats['ppg']) * 100, 1), 100),
            min(round((player['apg'] / max_stats['apg']) * 100, 1), 100),
            min(round((player['rpg'] / max_stats['rpg']) * 100, 1), 100),
            min(round((player['stl'] / max_stats['stl']) * 100, 1), 100),
            min(round((player['blk'] / max_stats['blk']) * 100, 1), 100)
        ]

        # 載入多年數據
        years_data = load_multi_year_data(player_id)

        return render_template('player_detail.html',
                             player=player,
                             radar_stats=radar_stats,
                             years_data=years_data)
    return render_template('index.html'), 404

@app.route('/live_scores')
def live_scores():
    """賽事比分頁面"""
    return render_template('live_scores.html')

@app.route('/statistics')
def statistics():
    """數據分析頁面"""
    return render_template('statistics.html')

@app.route('/save_exercise', methods=['POST'])
def save_exercise():
    """保存運動數據到歷史記錄"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    data = request.get_json()

    try:
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO exercise_history
            (user_id, exercise_type, duration, weight, height, age, gender,
             heart_rate, temperature, calories, met, heart_rate_zone, efficiency_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            data.get('exercise_type'),
            data.get('duration'),
            data.get('weight'),
            data.get('height'),
            data.get('age'),
            data.get('gender'),
            data.get('heart_rate'),
            data.get('temperature'),
            data.get('calories'),
            data.get('met'),
            data.get('heart_rate_zone'),
            data.get('efficiency_score')
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '數據已保存到歷史記錄'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失敗: {str(e)}'}), 500

@app.route('/history')
def history():
    """查看歷史記錄頁面"""
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('data/users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT * FROM exercise_history
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    records = c.fetchall()
    conn.close()

    # 轉換為字典列表
    history_data = []
    for record in records:
        history_data.append({
            'id': record['id'],
            'exercise_type': record['exercise_type'],
            'duration': record['duration'],
            'weight': record['weight'],
            'height': record['height'],
            'age': record['age'],
            'gender': record['gender'],
            'heart_rate': record['heart_rate'],
            'temperature': record['temperature'],
            'calories': record['calories'],
            'met': record['met'],
            'heart_rate_zone': record['heart_rate_zone'],
            'efficiency_score': record['efficiency_score'],
            'created_at': record['created_at']
        })

    return render_template('history.html', history=history_data)

@app.route('/delete_history/<int:record_id>', methods=['POST'])
def delete_history(record_id):
    """刪除歷史記錄"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    try:
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        c.execute('DELETE FROM exercise_history WHERE id = ? AND user_id = ?',
                 (record_id, session['user_id']))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '記錄已刪除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'刪除失敗: {str(e)}'}), 500

# API 路由
@app.route('/api/players')
def api_players():
    """獲取球員列表"""
    return jsonify({
        'success': True,
        'data': PLAYERS_DATA
    })

@app.route('/api/player/<int:player_id>')
def api_player(player_id):
    """獲取單個球員詳情"""
    player = next((p for p in PLAYERS_DATA if p['id'] == player_id), None)
    if player:
        return jsonify({
            'success': True,
            'data': player
        })
    return jsonify({
        'success': False,
        'message': '球員不存在'
    }), 404

@app.route('/api/games')
def api_games():
    """獲取所有比賽"""
    return jsonify({
        'success': True,
        'data': GAMES_DATA
    })

@app.route('/api/games/live')
def api_games_live():
    """獲取進行中的比賽"""
    # 模擬即時更新比分
    live_games = GAMES_DATA['live'].copy()
    for game in live_games:
        # 隨機更新比分
        if random.random() > 0.7:
            game['home_score'] += random.choice([0, 2, 3])
        if random.random() > 0.7:
            game['away_score'] += random.choice([0, 2, 3])

    return jsonify({
        'success': True,
        'data': live_games
    })

@app.route('/api/statistics')
def api_statistics():
    """獲取統計數據"""
    return jsonify({
        'success': True,
        'data': STATISTICS_DATA
    })

@app.route('/api/statistics/trend')
def api_statistics_trend():
    """獲取數據趨勢"""
    # 生成模擬的趨勢數據
    weeks = ['第1週', '第2週', '第3週', '第4週', '第5週', '第6週']
    trend_data = {
        'labels': weeks,
        'datasets': [
            {
                'label': '哈登 PPG',
                'data': [22.5, 24.1, 23.8, 25.2, 24.8, 26.1]
            },
            {
                'label': '東契奇 PPG',
                'data': [30.2, 31.5, 32.1, 33.0, 32.4, 34.2]
            }
        ]
    }
    return jsonify({
        'success': True,
        'data': trend_data
    })

@app.route('/api/player/<int:player_id>/games')
def api_player_games(player_id):
    """獲取球員最近比賽數據"""
    # 生成模擬數據
    games = []
    for i in range(10):
        games.append({
            'game_number': i + 1,
            'score': random.randint(20, 40),
            'assists': random.randint(3, 12),
            'rebounds': random.randint(4, 14),
            'fg_pct': round(random.uniform(35, 60), 1)
        })

    return jsonify({
        'success': True,
        'data': games
    })

@app.template_filter('format_datetime')
def format_datetime(value):
    """格式化日期時間"""
    if isinstance(value, str):
        return value
    return value.strftime('%Y-%m-%d %H:%M')

@app.errorhandler(404)
def not_found(error):
    """404 錯誤處理"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 錯誤處理"""
    return render_template('index.html'), 500

if __name__ == '__main__':
    # 初始化資料庫
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
