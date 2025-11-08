from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import random
import csv
import os

app = Flask(__name__)

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
    app.run(debug=True, host='0.0.0.0', port=5000)
