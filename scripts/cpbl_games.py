#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "scrapling[ai]",
#     "beautifulsoup4",
#     "lxml",
# ]
# ///
"""
CPBL 比賽結果查詢
使用官方隱藏 API: /schedule/getgamedatas
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 引入共用模組
sys.path.insert(0, str(Path(__file__).parent))
from _cpbl_api import post_api, KIND_NAMES, resolve_team


def query_games(
    year: Optional[int] = None,
    month: Optional[str] = None,
    date: Optional[str] = None,
    team: Optional[str] = None,
    kind: str = 'A',
    limit: Optional[int] = None
) -> list[dict]:
    """
    查詢比賽結果
    
    Args:
        year: 年份（預設今年）
        date: 特定日期 (YYYY-MM-DD)
        team: 球隊名過濾（部分匹配）
        kind: 賽事類型代碼（預設 A）
        limit: 限制筆數
    
    Returns:
        比賽列表
    """
    if year is None:
        year = datetime.now().year
    
    # 呼叫 API（用該年 1/1 取得整年資料）
    result = post_api('/schedule/getgamedatas', {
        'calendar': f'{year}/01/01',
        'location': '',
        'kindCode': kind
    })
    
    if not result.get('Success'):
        raise ValueError(f'API 回應失敗: {result}')
    
    # GameDatas 是 JSON 字串，需要再解析
    raw_games = json.loads(result.get('GameDatas', '[]'))
    
    # 過濾與轉換資料
    games = []
    for g in raw_games:
        game_date_str = g.get('GameDate', '')[:10]
        
        # 日期過濾
        if date and game_date_str != date:
            continue
        
        # 月份過濾
        if month and not game_date_str.startswith(month):
            continue
        
        # 球隊過濾（用正式名稱匹配）
        if team:
            away = g.get('VisitingTeamName', '')
            home = g.get('HomeTeamName', '')
            if team not in away and team not in home:
                continue
        
        # 只顯示已經打完的比賽（有比分）
        away_score = g.get('VisitingScore')
        home_score = g.get('HomeScore')
        has_score = away_score is not None and home_score is not None
        
        # 轉換成統一格式
        game_data = {
            'date': g.get('GameDate', '')[:10],
            'away_team': g.get('VisitingTeamName'),
            'home_team': g.get('HomeTeamName'),
            'away_score': away_score if has_score else None,
            'home_score': home_score if has_score else None,
            'venue': g.get('FieldAbbe'),
        }
        
        # 如果有勝敗投手資訊，也加入
        if has_score:
            if g.get('WinningPitcherName'):
                game_data['winning_pitcher'] = g.get('WinningPitcherName')
            if g.get('LoserPitcherName'):
                game_data['losing_pitcher'] = g.get('LoserPitcherName')
            if g.get('MvpName'):
                game_data['mvp'] = g.get('MvpName')
        
        games.append(game_data)
    
    # 排序（最新在前）
    games.sort(key=lambda x: x['date'], reverse=True)
    
    # 限制筆數
    if limit:
        games = games[:limit]
    
    return games


def main():
    parser = argparse.ArgumentParser(
        description='CPBL 比賽結果查詢',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  # 查詢 2025 年所有比賽（前 10 場）
  uv run cpbl_games.py --year 2025 --limit 10
  
  # 查詢特定日期
  uv run cpbl_games.py --date 2025-03-29
  
  # 查詢特定球隊
  uv run cpbl_games.py --team 中信 --year 2025
  
  # 查詢二軍比賽
  uv run cpbl_games.py --year 2025 --kind W
        '''
    )
    
    parser.add_argument('--year', '-y', type=int, help='年份（預設今年）')
    parser.add_argument('--month', '-M', type=str, help='月份過濾 (YYYY-MM)')
    parser.add_argument('--date', '-d', type=str, help='特定日期 (YYYY-MM-DD)')
    parser.add_argument('--team', '-t', type=str, help='球隊名過濾（支援簡稱如：兄弟、獅、悍將）')
    parser.add_argument('--kind', '-k', type=str, default='A',
                        choices=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'X'],
                        help='賽事類型（預設 A）。A=一軍例行賽 B=明星賽 C=總冠軍 D=二軍例行賽 E=季後挑戰賽 F=二軍總冠軍 G=一軍熱身賽 H=未來之星 X=國際交流賽')
    parser.add_argument('--limit', '-l', type=int, help='限制筆數')
    parser.add_argument('--output', '-o', type=str, default='json', choices=['json', 'text'],
                        help='輸出格式（預設 json）')
    
    args = parser.parse_args()
    
    # 球隊名稱模糊匹配
    team_input = args.team
    team = None
    if team_input:
        team = resolve_team(team_input)
        if team:
            if team != team_input:
                print(f'✅ 「{team_input}」→「{team}」', file=sys.stderr)
        else:
            print(f'⚠️ 找不到球隊「{team_input}」', file=sys.stderr)
    
    # 驗證 month 格式
    if args.month and not (len(args.month) == 7 and args.month[4] == '-'):
        print(f'⚠️ --month 格式應為 YYYY-MM，例如 2025-03', file=sys.stderr)
        sys.exit(1)
    
    # 顯示賽事類型
    kind_name = KIND_NAMES.get(args.kind, '未知')
    print(f'✅ 賽事類型：{kind_name} ({args.kind})', file=sys.stderr)
    
    try:
        games = query_games(
            year=args.year,
            month=args.month,
            date=args.date,
            team=team,
            kind=args.kind,
            limit=args.limit
        )
        
        # 空結果預警
        if not games:
            query_year = args.year if args.year else datetime.now().year
            if query_year > datetime.now().year:
                print(f'⚠️ 該年份球季尚未開始', file=sys.stderr)
            else:
                print(f'⚠️ 目前沒有符合條件的賽事資料', file=sys.stderr)
        
        if args.output == 'json':
            print(json.dumps(games, ensure_ascii=False, indent=2))
        else:
            # 文字格式
            if not games:
                print('沒有找到比賽資料')
                return
            
            print(f"找到 {len(games)} 場比賽:\n")
            for g in games:
                if g.get('away_score') is not None:
                    score = f"{g['away_score']}:{g['home_score']}"
                    print(f"[{g['date']}] {g['away_team']} {score} {g['home_team']} @ {g['venue']}")
                    if g.get('winning_pitcher'):
                        print(f"  勝: {g['winning_pitcher']} 敗: {g.get('losing_pitcher', '')}")
                else:
                    print(f"[{g['date']}] {g['away_team']} vs {g['home_team']} @ {g['venue']}")
    
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
