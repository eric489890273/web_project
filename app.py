from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import csv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # 請在生產環境中更改此密鑰

# PostgreSQL 資料庫連接字串 (從環境變數讀取)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_JU0MEseP6fZC@ep-square-dust-a1cmt258-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require')

def get_db_connection():
    """取得資料庫連接"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# 資料庫初始化
def init_db():
    """初始化資料庫"""
    conn = get_db_connection()
    c = conn.cursor()

    # 用戶表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 運動數據歷史記錄表
    c.execute('''
        CREATE TABLE IF NOT EXISTS exercise_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            exercise_type VARCHAR(50) NOT NULL,
            duration INTEGER NOT NULL,
            weight REAL,
            height REAL,
            age INTEGER,
            gender VARCHAR(10),
            heart_rate INTEGER,
            temperature REAL,
            calories REAL,
            met REAL,
            heart_rate_zone VARCHAR(50),
            efficiency_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 籃球數據歷史記錄表
    c.execute('''
        CREATE TABLE IF NOT EXISTS basketball_history (
            id SERIAL PRIMARY KEY,
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

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = %s', (username,))
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
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        existing_user = c.fetchone()

        if existing_user:
            flash('用戶名或郵箱已被使用', 'error')
            conn.close()
            return render_template('register.html')

        # 創建新用戶
        hashed_password = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
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

@app.route('/player_compare')
def player_compare():
    """球員比較頁面"""
    return render_template('player_compare.html', players=PLAYERS_DATA, teams=TEAMS_LIST)

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

def fetch_nba_games(date_str):
    """抓取指定日期的 NBA 比賽資料"""
    try:
        url = f"https://www.nba.com/games?date={date_str}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # 從 HTML 中提取 __NEXT_DATA__ JSON
        import json
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', response.text)
        if not match:
            print(f"找不到 __NEXT_DATA__ for {date_str}")
            return []

        # 解析 JSON
        data = json.loads(match.group(1))

        # 取得遊戲資料: props.pageProps.gameCardFeed.modules
        game_feed = data.get('props', {}).get('pageProps', {}).get('gameCardFeed', {})
        modules = game_feed.get('modules', [])

        if not modules:
            print(f"找不到 modules for {date_str}")
            return []

        games = []

        # 第一個 module 包含 cards
        for module in modules:
            cards = module.get('cards', [])

            for card in cards:
                card_data = card.get('cardData', {})

                # 確認有隊伍資料
                if 'awayTeam' not in card_data or 'homeTeam' not in card_data:
                    continue

                game_id = card_data.get('gameId', '')
                game_status = card_data.get('gameStatus', 1)  # 1=未開始, 2=進行中, 3=已結束
                status_text = card_data.get('gameStatusText', '')

                # 判斷比賽狀態
                if game_status == 3:
                    status = 'finished'
                elif game_status == 2:
                    status = 'live'
                else:
                    status = 'upcoming'

                # 取得節數和時間
                period = card_data.get('period', '')
                game_clock = card_data.get('gameClock', '')

                # 客隊資料
                away_team = card_data['awayTeam']
                away_code = away_team.get('teamTricode', '')
                away_score = away_team.get('score', '')

                # 主隊資料
                home_team = card_data['homeTeam']
                home_code = home_team.get('teamTricode', '')
                home_score = home_team.get('score', '')

                # 取得隊伍資訊 (中文名稱和 logo)
                away_info = get_team_info(away_code)
                home_info = get_team_info(home_code)

                game = {
                    'id': game_id,
                    'awayTeam': away_info,
                    'homeTeam': home_info,
                    'status': status
                }

                # 根據狀態加入對應資訊
                if status == 'finished':
                    game['awayScore'] = away_score
                    game['homeScore'] = home_score
                    game['timeAgo'] = f"{random.randint(1, 8)} 小時前"
                elif status == 'live':
                    game['awayScore'] = away_score
                    game['homeScore'] = home_score
                    game['quarter'] = f"Q{period}" if period else 'Q4'
                    game['time'] = game_clock if game_clock else '00:00'
                else:  # upcoming
                    game['startTime'] = status_text if status_text else '19:30'
                    game['countdown'] = f"{random.randint(1, 12)} 小時後"

                games.append(game)

        print(f"成功抓取 {len(games)} 場比賽 for {date_str}")
        return games

    except Exception as e:
        print(f"Error fetching NBA games for {date_str}: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_box_score(game_id, away_code, home_code):
    """抓取比賽 box-score 詳細資料

    Args:
        game_id: 比賽 ID
        away_code: 客隊代碼
        home_code: 主隊代碼

    Returns:
        dict: 包含球員統計和隊伍統計的資料
    """
    try:
        url = f"https://www.nba.com/game/{away_code.lower()}-vs-{home_code.lower()}-{game_id}/box-score"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # 從 HTML 中提取 __NEXT_DATA__ JSON
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', response.text)
        if not match:
            print(f"找不到 __NEXT_DATA__ for box-score {game_id}")
            return None

        # 解析 JSON
        data = json.loads(match.group(1))

        # 取得比賽資料
        props = data.get('props', {}).get('pageProps', {})
        game = props.get('game', {})

        if not game:
            print(f"找不到 game data for {game_id}")
            return None

        # 提取需要的資料
        away_team = game.get('awayTeam', {})
        home_team = game.get('homeTeam', {})

        # 球員統計
        away_players = away_team.get('players', [])
        home_players = home_team.get('players', [])

        # 隊伍統計
        away_stats = away_team.get('statistics', {})
        home_stats = home_team.get('statistics', {})

        # 比分細節 (各節比分) - 從各隊的 periods 取得
        away_periods = away_team.get('periods', [])
        home_periods = home_team.get('periods', [])

        # 合併各節比分
        periods = []
        for i in range(max(len(away_periods), len(home_periods))):
            period_data = {
                'period': i + 1,
                'awayScore': away_periods[i].get('score', 0) if i < len(away_periods) else 0,
                'homeScore': home_periods[i].get('score', 0) if i < len(home_periods) else 0
            }
            periods.append(period_data)

        result = {
            'gameId': game_id,
            'awayTeam': {
                'name': get_team_info(away_team.get('teamTricode', '')).get('name'),
                'code': away_team.get('teamTricode', ''),
                'score': away_team.get('score', 0),
                'players': [{
                    'name': f"{p.get('firstName', '')} {p.get('familyName', '')}".strip(),
                    'nameI': p.get('nameI', ''),
                    'position': p.get('position', ''),
                    'jerseyNum': p.get('jerseyNum', ''),
                    'statistics': p.get('statistics', {}),
                    'hasPlayed': p.get('statistics', {}).get('minutes', '') != ''
                } for p in away_players],
                'statistics': away_stats
            },
            'homeTeam': {
                'name': get_team_info(home_team.get('teamTricode', '')).get('name'),
                'code': home_team.get('teamTricode', ''),
                'score': home_team.get('score', 0),
                'players': [{
                    'name': f"{p.get('firstName', '')} {p.get('familyName', '')}".strip(),
                    'nameI': p.get('nameI', ''),
                    'position': p.get('position', ''),
                    'jerseyNum': p.get('jerseyNum', ''),
                    'statistics': p.get('statistics', {}),
                    'hasPlayed': p.get('statistics', {}).get('minutes', '') != ''
                } for p in home_players],
                'statistics': home_stats
            },
            'periods': periods
        }

        return result

    except Exception as e:
        print(f"Error fetching box-score for {game_id}: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_team_info(team_code):
    """根據球隊代碼獲取球隊資訊"""
    team_map = {
        'LAL': {'name': '洛杉磯湖人', 'short': 'LAL', 'logo': 'https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg'},
        'GSW': {'name': '金州勇士', 'short': 'GSW', 'logo': 'https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg'},
        'BOS': {'name': '波士頓塞爾提克', 'short': 'BOS', 'logo': 'https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg'},
        'MIA': {'name': '邁阿密熱火', 'short': 'MIA', 'logo': 'https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg'},
        'PHX': {'name': '鳳凰城太陽', 'short': 'PHX', 'logo': 'https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg'},
        'POR': {'name': '波特蘭拓荒者', 'short': 'POR', 'logo': 'https://cdn.nba.com/logos/nba/1610612757/primary/L/logo.svg'},
        'BKN': {'name': '布魯克林籃網', 'short': 'BKN', 'logo': 'https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg'},
        'DEN': {'name': '丹佛金塊', 'short': 'DEN', 'logo': 'https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg'},
        'ATL': {'name': '亞特蘭大老鷹', 'short': 'ATL', 'logo': 'https://cdn.nba.com/logos/nba/1610612737/primary/L/logo.svg'},
        'DET': {'name': '底特律活塞', 'short': 'DET', 'logo': 'https://cdn.nba.com/logos/nba/1610612765/primary/L/logo.svg'},
        'MEM': {'name': '曼菲斯灰熊', 'short': 'MEM', 'logo': 'https://cdn.nba.com/logos/nba/1610612763/primary/L/logo.svg'},
        'SAS': {'name': '聖安東尼奧馬刺', 'short': 'SAS', 'logo': 'https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg'},
        'UTA': {'name': '猶他爵士', 'short': 'UTA', 'logo': 'https://cdn.nba.com/logos/nba/1610612762/primary/L/logo.svg'},
        'ORL': {'name': '奧蘭多魔術', 'short': 'ORL', 'logo': 'https://cdn.nba.com/logos/nba/1610612753/primary/L/logo.svg'},
        'CHI': {'name': '芝加哥公牛', 'short': 'CHI', 'logo': 'https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg'},
        'CLE': {'name': '克里夫蘭騎士', 'short': 'CLE', 'logo': 'https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg'},
        'DAL': {'name': '達拉斯獨行俠', 'short': 'DAL', 'logo': 'https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg'},
        'HOU': {'name': '休士頓火箭', 'short': 'HOU', 'logo': 'https://cdn.nba.com/logos/nba/1610612745/primary/L/logo.svg'},
        'IND': {'name': '印第安納溜馬', 'short': 'IND', 'logo': 'https://cdn.nba.com/logos/nba/1610612754/primary/L/logo.svg'},
        'LAC': {'name': '洛杉磯快艇', 'short': 'LAC', 'logo': 'https://cdn.nba.com/logos/nba/1610612746/primary/L/logo.svg'},
        'MIL': {'name': '密爾瓦基公鹿', 'short': 'MIL', 'logo': 'https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg'},
        'MIN': {'name': '明尼蘇達灰狼', 'short': 'MIN', 'logo': 'https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg'},
        'NOP': {'name': '紐奧良鵜鶘', 'short': 'NOP', 'logo': 'https://cdn.nba.com/logos/nba/1610612740/primary/L/logo.svg'},
        'NYK': {'name': '紐約尼克', 'short': 'NYK', 'logo': 'https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg'},
        'OKC': {'name': '奧克拉荷馬雷霆', 'short': 'OKC', 'logo': 'https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg'},
        'PHI': {'name': '費城76人', 'short': 'PHI', 'logo': 'https://cdn.nba.com/logos/nba/1610612755/primary/L/logo.svg'},
        'SAC': {'name': '沙加緬度國王', 'short': 'SAC', 'logo': 'https://cdn.nba.com/logos/nba/1610612758/primary/L/logo.svg'},
        'TOR': {'name': '多倫多暴龍', 'short': 'TOR', 'logo': 'https://cdn.nba.com/logos/nba/1610612761/primary/L/logo.svg'},
        'WAS': {'name': '華盛頓巫師', 'short': 'WAS', 'logo': 'https://cdn.nba.com/logos/nba/1610612764/primary/L/logo.svg'},
        'CHA': {'name': '夏洛特黃蜂', 'short': 'CHA', 'logo': 'https://cdn.nba.com/logos/nba/1610612766/primary/L/logo.svg'},
    }

    return team_map.get(team_code, {
        'name': team_code,
        'short': team_code,
        'logo': 'https://via.placeholder.com/60'
    })

@app.route('/live_scores')
def live_scores():
    """賽事比分頁面"""
    return render_template('live_scores.html')

@app.route('/api/nba_games')
def api_nba_games():
    """API: 獲取指定日期範圍的 NBA 比賽資料"""
    try:
        # 獲取參數中的日期,預設為昨天
        base_date_str = request.args.get('base_date')
        if base_date_str:
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
        else:
            base_date = datetime.now() - timedelta(days=1)

        # 生成前後兩天的日期 (總共5天)
        dates = []
        games_by_date = {}

        for i in range(-2, 3):
            date = base_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            dates.append({
                'date': date_str,
                'display': date.strftime('%m/%d'),
                'weekday': ['週一', '週二', '週三', '週四', '週五', '週六', '週日'][date.weekday()],
                'is_base': i == 0
            })

            # 抓取該日期的比賽資料
            games_by_date[date_str] = fetch_nba_games(date_str)

        return jsonify({
            'success': True,
            'dates': dates,
            'games': games_by_date
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/box_score')
def api_box_score():
    """API: 獲取比賽 box-score 詳細資料"""
    try:
        game_id = request.args.get('game_id')
        away_code = request.args.get('away_code')
        home_code = request.args.get('home_code')

        if not game_id or not away_code or not home_code:
            return jsonify({
                'success': False,
                'error': '缺少必要參數'
            }), 400

        box_score = fetch_box_score(game_id, away_code, home_code)

        if box_score:
            return jsonify({
                'success': True,
                'data': box_score
            })
        else:
            return jsonify({
                'success': False,
                'error': '無法獲取比賽資料'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_mock_games(dates):
    """生成模擬比賽資料 (實際使用時應替換為真實 API)"""
    teams = [
        {'name': '洛杉磯湖人', 'short': 'LAL', 'logo': 'https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg'},
        {'name': '金州勇士', 'short': 'GSW', 'logo': 'https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg'},
        {'name': '波士頓塞爾提克', 'short': 'BOS', 'logo': 'https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg'},
        {'name': '邁阿密熱火', 'short': 'MIA', 'logo': 'https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg'},
        {'name': '鳳凰城太陽', 'short': 'PHX', 'logo': 'https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg'},
        {'name': '波特蘭拓荒者', 'short': 'POR', 'logo': 'https://cdn.nba.com/logos/nba/1610612757/primary/L/logo.svg'},
        {'name': '布魯克林籃網', 'short': 'BKN', 'logo': 'https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg'},
        {'name': '丹佛金塊', 'short': 'DEN', 'logo': 'https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg'},
    ]

    games = {}
    statuses = ['live', 'finished', 'upcoming']

    for date_info in dates:
        date = date_info['date']
        games[date] = []

        # 每天生成 2-4 場比賽
        num_games = random.randint(2, 4)
        for i in range(num_games):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])

            # 根據日期決定比賽狀態
            if date_info['is_base']:
                status = random.choice(['live', 'finished'])
            elif dates.index(date_info) < 2:
                status = 'finished'
            else:
                status = 'upcoming'

            game = {
                'id': f"{date}_{i}",
                'status': status,
                'homeTeam': home_team,
                'awayTeam': away_team
            }

            if status == 'live':
                game['quarter'] = random.choice(['Q1', 'Q2', 'Q3', 'Q4'])
                game['time'] = f"{random.randint(0, 11):02d}:{random.randint(0, 59):02d}"
                game['homeScore'] = random.randint(80, 120)
                game['awayScore'] = random.randint(80, 120)
            elif status == 'finished':
                game['homeScore'] = random.randint(90, 130)
                game['awayScore'] = random.randint(90, 130)
                game['timeAgo'] = f"{random.randint(1, 5)} 小時前"
            else:
                game['startTime'] = f"{random.randint(18, 21)}:{random.choice(['00', '30'])}"
                game['countdown'] = f"{random.randint(1, 8)} 小時後"

            games[date].append(game)

    return games

@app.route('/statistics')
def statistics():
    """數據分析頁面"""
    return render_template('statistics.html')

@app.route('/basketball_stats')
def basketball_stats():
    """籃球數據分析頁面"""
    return render_template('basketball_stats.html')

@app.route('/save_exercise', methods=['POST'])
def save_exercise():
    """保存運動數據到歷史記錄"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    data = request.get_json()

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO exercise_history
            (user_id, exercise_type, duration, weight, height, age, gender,
             heart_rate, temperature, calories, met, heart_rate_zone, efficiency_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

@app.route('/save_basketball', methods=['POST'])
def save_basketball():
    """保存籃球數據到歷史記錄"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    data = request.get_json()

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO basketball_history
            (user_id, play_time, fga, fgm, fg_pct, three_pa, three_pm, three_pct,
             fta, ftm, ft_pct, rebounds, assists, steals, blocks, turnovers, points,
             true_shooting_pct, assist_ratio, turnover_ratio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            session['user_id'],
            data.get('play_time'),
            data.get('fga'),
            data.get('fgm'),
            data.get('fg_pct'),
            data.get('three_pa'),
            data.get('three_pm'),
            data.get('three_pct'),
            data.get('fta'),
            data.get('ftm'),
            data.get('ft_pct'),
            data.get('rebounds'),
            data.get('assists'),
            data.get('steals'),
            data.get('blocks'),
            data.get('turnovers'),
            data.get('points'),
            data.get('true_shooting_pct'),
            data.get('assist_ratio'),
            data.get('turnover_ratio')
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '籃球數據已保存到歷史記錄'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失敗: {str(e)}'}), 500

@app.route('/history')
def history():
    """查看歷史記錄頁面"""
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute('''
        SELECT * FROM exercise_history
        WHERE user_id = %s
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

@app.route('/basketball_history')
def basketball_history():
    """查看籃球數據歷史記錄頁面"""
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor(cursor_factory=RealDictCursor)
    c.execute('''
        SELECT * FROM basketball_history
        WHERE user_id = %s
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    records = c.fetchall()
    conn.close()

    # 轉換為字典列表並計算 PER
    history_data = []
    total_games = len(records)

    for record in records:
        # 計算 PER: [(得分+助攻+籃板+抄截+阻攻)-(投籃出手數-投籃命中數)-(罰球出手數-罰球命中數)-失誤數]/總出場場次
        per = 0
        if total_games > 0:
            per = (
                (record['points'] + record['assists'] + record['rebounds'] +
                 record['steals'] + record['blocks']) -
                (record['fga'] - record['fgm']) -
                (record['fta'] - record['ftm']) -
                record['turnovers']
            ) / total_games

        history_data.append({
            'id': record['id'],
            'play_time': record['play_time'],
            'fga': record['fga'],
            'fgm': record['fgm'],
            'fg_pct': record['fg_pct'],
            'three_pa': record['three_pa'],
            'three_pm': record['three_pm'],
            'three_pct': record['three_pct'],
            'fta': record['fta'],
            'ftm': record['ftm'],
            'ft_pct': record['ft_pct'],
            'rebounds': record['rebounds'],
            'assists': record['assists'],
            'steals': record['steals'],
            'blocks': record['blocks'],
            'turnovers': record['turnovers'],
            'points': record['points'],
            'per': per,
            'true_shooting_pct': record['true_shooting_pct'],
            'assist_ratio': record['assist_ratio'],
            'turnover_ratio': record['turnover_ratio'],
            'created_at': record['created_at']
        })

    return render_template('basketball_history.html', history=history_data, total_games=total_games)

@app.route('/delete_history/<int:record_id>', methods=['POST'])
def delete_history(record_id):
    """刪除歷史記錄"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM exercise_history WHERE id = %s AND user_id = %s',
                 (record_id, session['user_id']))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '記錄已刪除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'刪除失敗: {str(e)}'}), 500

@app.route('/delete_basketball_history/<int:record_id>', methods=['POST'])
def delete_basketball_history(record_id):
    """刪除籃球歷史記錄"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '請先登入'}), 401

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM basketball_history WHERE id = %s AND user_id = %s',
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

# Vercel serverless function entry point
app = app
