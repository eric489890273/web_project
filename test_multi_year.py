"""測試多年數據載入功能"""
import csv
import os

def test_multi_year_data():
    """測試載入多年數據"""
    csv_files = {
        '2021-22': 'nba_traditional_stats_2021_22.csv',
        '2022-23': 'nba_traditional_stats_2022_23.csv',
        '2023-24': 'nba_traditional_stats_2023_24.csv',
        '2024-25': 'nba_traditional_stats_2024_25.csv',
        '2025-26': 'nba_traditional_stats_2025_26.csv'
    }

    print("=== 測試多年數據載入 ===\n")

    # 測試每個檔案
    for year, filename in csv_files.items():
        csv_path = os.path.join('data', filename)
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                print(f"✅ {year}: {len(rows)} 位球員")
        except Exception as e:
            print(f"❌ {year}: 載入失敗 - {e}")

    # 測試特定球員的多年數據 (LeBron James - ID: 2544)
    test_player_id = '2544'
    print(f"\n=== 測試球員 ID {test_player_id} 的多年數據 ===\n")

    years_data = {}
    for year, filename in csv_files.items():
        csv_path = os.path.join('data', filename)
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if str(row['PLAYER_ID']) == str(test_player_id):
                        gp = float(row['GP']) if row['GP'] else 1
                        years_data[year] = {
                            'name': row['PLAYER_NAME'],
                            'ppg': round(float(row['PTS']) / gp, 1) if row['PTS'] else 0,
                            'apg': round(float(row['AST']) / gp, 1) if row['AST'] else 0,
                            'rpg': round(float(row['REB']) / gp, 1) if row['REB'] else 0,
                            'gp': int(float(row['GP'])) if row['GP'] else 0,
                        }
                        break
        except Exception as e:
            print(f"載入 {year} 失敗: {e}")

    # 顯示結果
    if years_data:
        first_season = list(years_data.values())[0]
        print(f"球員: {first_season['name']}")
        print(f"找到 {len(years_data)} 個賽季的數據\n")

        print("賽季    | 場次 | 得分 | 助攻 | 籃板")
        print("-" * 45)
        for season in sorted(years_data.keys()):
            data = years_data[season]
            print(f"{season} | {data['gp']:4d} | {data['ppg']:4.1f} | {data['apg']:4.1f} | {data['rpg']:4.1f}")
    else:
        print(f"未找到球員 ID {test_player_id} 的數據")

if __name__ == '__main__':
    test_multi_year_data()
