from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# 模擬球員數據
PLAYERS_DATA = [
    {
        'id': 1,
        'name': '詹姆斯 · 哈登',
        'name_en': 'James Harden',
        'team': '費城76人',
        'team_en': '76ers',
        'position': '得分後衛',
        'number': '13',
        'avatar': 'https://via.placeholder.com/80',
        'ppg': 24.8,
        'apg': 10.2,
        'rpg': 6.5,
        'fg_pct': 44.1,
        'three_pct': 38.5
    },
    {
        'id': 2,
        'name': '盧卡 · 東契奇',
        'name_en': 'Luka Doncic',
        'team': '達拉斯獨行俠',
        'team_en': 'Mavericks',
        'position': '控球後衛',
        'number': '77',
        'avatar': 'https://via.placeholder.com/80',
        'ppg': 32.4,
        'apg': 8.6,
        'rpg': 8.0,
        'fg_pct': 49.6,
        'three_pct': 37.8
    },
    {
        'id': 3,
        'name': '吉安尼斯 · 安戴托昆波',
        'name_en': 'Giannis Antetokounmpo',
        'team': '密爾瓦基公鹿',
        'team_en': 'Bucks',
        'position': '大前鋒',
        'number': '34',
        'avatar': 'https://via.placeholder.com/80',
        'ppg': 31.1,
        'apg': 5.7,
        'rpg': 11.8,
        'fg_pct': 55.3,
        'three_pct': 27.5
    },
    {
        'id': 4,
        'name': '凱文 · 杜蘭特',
        'name_en': 'Kevin Durant',
        'team': '鳳凰城太陽',
        'team_en': 'Suns',
        'position': '小前鋒',
        'number': '35',
        'avatar': 'https://via.placeholder.com/80',
        'ppg': 29.1,
        'apg': 5.0,
        'rpg': 6.7,
        'fg_pct': 56.0,
        'three_pct': 39.7
    }
]

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
    return render_template('player_analysis.html', players=PLAYERS_DATA)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    """球員詳細分析頁面"""
    player = next((p for p in PLAYERS_DATA if p['id'] == player_id), None)
    if player:
        # 準備最近10場得分數據
        recent_games = [
            player['ppg'] - 5,
            player['ppg'] + 3,
            player['ppg'] - 2,
            player['ppg'] + 7,
            player['ppg'],
            player['ppg'] + 4,
            player['ppg'] - 3,
            player['ppg'] + 6,
            player['ppg'] + 1,
            player['ppg']
        ]

        # 準備雷達圖數據
        radar_stats = [
            round(player['ppg'] * 2.5, 1),
            round(player['apg'] * 8, 1),
            round(player['rpg'] * 7, 1),
            65,
            55
        ]

        return render_template('player_detail.html',
                             player=player,
                             recent_games=recent_games,
                             radar_stats=radar_stats)
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
