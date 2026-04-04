#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "scrapling[ai]",
# #     "lxml",
# ]
# ///
"""
CPBL 即時比分查詢
使用官方隱藏 API: /schedule/getgamedatas + /box/gamedata
顯示今日/指定日期賽事狀態（未開打 / 比賽中 / 已結束）及當前局數與比分
"""

import argparse
import json
import sys
from datetime import datetime, date, timezone, timedelta
from pathlib import Path
from typing import Optional

# 引入共用模組
sys.path.insert(0, str(Path(__file__).parent))
from _cpbl_api import post_api, post_api_html, KIND_NAMES, resolve_team_cli, validate_date, get_api

TZ_TW = timezone(timedelta(hours=8))

# PresentStatus 對照表（從 CPBL Angular 模板推斷）
PRESENT_STATUS_MAP = {
    '1': '未開打',
    '2': '比賽中',
    '3': '已結束',
    '4': '延賽',
    '5': '保留',
    '6': '取消',
    '7': '比賽暫停',
    '8': '比賽中',  # 進入延長
}

STATUS_EMOJI = {
    '未開打': '⏳',
    '比賽中': '🔴',
    '已結束': '✅',
    '延賽': '🌧️',
    '保留': '📌',
    '取消': '❌',
    '比賽暫停': '⏸️',
}


def _get_status(raw_status: str) -> str:
    """將 PresentStatus 代碼轉成人類可讀狀態"""
    return PRESENT_STATUS_MAP.get(str(raw_status).strip(), '未知')


def _get_today_tw() -> str:
    """取得台灣時區今天日期 YYYY-MM-DD"""
    return datetime.now(TZ_TW).strftime('%Y-%m-%d')


def fetch_games_for_date(target_date: str, kind: str = 'A') -> list[dict]:
    """
    從 /schedule/getgamedatas 取得指定日期的所有賽事
    
    Returns: 原始 game dict 列表
    """
    year = target_date[:4]
    result = post_api('/schedule/getgamedatas', {
        'calendar': f'{year}/01/01',
        'location': '',
        'kindCode': kind
    })
    
    if not result.get('Success'):
        raise ValueError(f'API 回應失敗: {result}')
    
    raw_games = json.loads(result.get('GameDatas', '[]'))
    
    # 過濾指定日期
    return [g for g in raw_games if g.get('GameDate', '')[:10] == target_date]


def fetch_live_inning(year: str, kind: str, game_sno: str) -> Optional[dict]:
    """
    從 /box/getlive 的 LiveLogJson + CurtGameDetailJson 取得即時局數
    
    策略：
    1. 從 CurtGameDetailJson 取 GameStatus 和分數
    2. 從 ScoreboardJson 取最大局數
    3. 從 LiveLogJson 取最後一筆的 InningSeq + VisitingHomeType（最準確）
    
    Returns: dict with inning info or None
        {'inning': int, 'half': str, 'display': str, 'scores': dict}
    """
    try:
        result = post_api('/box/getlive', {
            'year': year,
            'kindCode': kind,
            'gameSno': game_sno,
        })
        
        if not result.get('Success'):
            return None
        
        # CurtGameDetailJson 是當前比賽的詳細資料
        curt_raw = result.get('CurtGameDetailJson')
        if not curt_raw:
            return None
        
        curt = json.loads(curt_raw)
        game_status = curt.get('GameStatus')
        
        # 只有比賽中 (2) 或已結束 (3) 才有局數
        if game_status not in (2, 3):
            return None
        
        away_score = curt.get('VisitingScore', 0) or 0
        home_score = curt.get('HomeScore', 0) or 0
        
        # 從 ScoreboardJson 取局數
        sb_raw = result.get('ScoreboardJson')
        max_inning = 0
        if sb_raw:
            scoreboards = json.loads(sb_raw)
            for sb in scoreboards:
                seq = sb.get('InningSeq')
                if seq and isinstance(seq, (int, float)):
                    max_inning = max(max_inning, int(seq))
        
        # 從 LiveLogJson 取精確的上下半
        log_raw = result.get('LiveLogJson')
        half = None
        last_inning = 0
        if log_raw:
            logs = json.loads(log_raw)
            if logs:
                last = logs[-1]
                last_inning = int(last.get('InningSeq', 0))
                half_type = last.get('VisitingHomeType')
                half = '上' if str(half_type) == '1' else '下'
                # 用 live log 的局數（更準確）
                max_inning = max(max_inning, last_inning)
        
        if max_inning == 0:
            return None
        
        if not half:
            half = '下'  # 預設下半
        
        if game_status == 3:
            display = '結束'
        else:
            display = f'第{max_inning}局{half}半'
        
        return {
            'inning': max_inning,
            'half': half,
            'display': display,
            'away_score': away_score,
            'home_score': home_score,
        }
        
    except Exception as e:
        print(f'⚠️ getlive 局數查詢失敗: {e}', file=sys.stderr)
        return None


def build_live_summary(games_raw: list[dict], date_str: str) -> list[dict]:
    """
    將原始 game 資料轉換成即時比分摘要
    
    Args:
        games_raw: getgamedatas API 回傳的原始 game list
        date_str: 查詢日期
    
    Returns:
        格式化的比賽摘要列表
    """
    result = []
    
    for g in games_raw:
        # 狀態判斷
        present_status = str(g.get('PresentStatus', '')).strip()
        is_play_ball = g.get('IsPlayBall') == 'Y'
        has_result = bool(g.get('GameResult'))
        
        away_score = g.get('VisitingScore')
        home_score = g.get('HomeScore')
        has_score = away_score is not None and home_score is not None
        
        # 決定狀態
        if present_status and present_status != '0':
            status = _get_status(present_status)
        elif is_play_ball or has_result:
            status = '已結束'
        elif has_score and (int(away_score or 0) > 0 or int(home_score or 0) > 0):
            status = '已結束'
        else:
            # 用時間判斷：若比賽時間已過但沒有比分，可能延賽或未更新
            game_time = g.get('GameDateTimeS', '')
            if game_time:
                try:
                    game_dt = datetime.fromisoformat(game_time)
                    now_tw = datetime.now(TZ_TW)
                    if now_tw > game_dt:
                        status = '比賽中'  # 時間到了但 API 還沒更新
                    else:
                        status = '未開打'
                except:
                    status = '未開打'
            else:
                status = '未開打'
        
        # API 延遲修正：PS=1(未開打) 但已有非零比分 → 實為比賽中
        if status == '未開打' and has_score:
            away_s = int(away_score or 0)
            home_s = int(home_score or 0)
            if away_s > 0 or home_s > 0:
                status = '比賽中'

        # 延賽推測：API 標已結束但 0:0 且無勝敗投 → 實為延賽
        if status == '已結束':
            away_s = int(away_score or 0)
            home_s = int(home_score or 0)
            no_pitchers = not g.get('WinningPitcherName') and not g.get('LoserPitcherName')
            if away_s == 0 and home_s == 0 and no_pitchers:
                status = '延賽'
        
        # 比賽時間
        game_time_str = ''
        if g.get('PreExeDate'):
            try:
                dt = datetime.fromisoformat(g['PreExeDate'])
                game_time_str = dt.strftime('%H:%M')
            except:
                game_time_str = ''
        
        # 比賽時長
        duration = g.get('GameDuringTime', '')
        
        # 基本資訊
        entry = {
            'game_sno': g.get('GameSno'),
            'date': date_str,
            'time': game_time_str,
            'away_team': g.get('VisitingTeamName'),
            'home_team': g.get('HomeTeamName'),
            'venue': g.get('FieldAbbe'),
            'status': status,
            'status_emoji': STATUS_EMOJI.get(status, '❓'),
        }
        
        # 比分
        if has_score and (int(away_score or 0) > 0 or int(home_score or 0) > 0 or status in ('已結束', '比賽中')):
            entry['away_score'] = int(away_score or 0)
            entry['home_score'] = int(home_score or 0)
            entry['score_display'] = f'{away_score}:{home_score}'
        
        # 比賽中顯示局數
        if status == '比賽中':
            year = g.get('Year', date_str[:4])
            kind_code = g.get('KindCode', 'A')
            sno = g.get('GameSno', '')
            if sno:
                inning_info = fetch_live_inning(year, kind_code, sno)
                if inning_info:
                    entry['inning'] = inning_info
                    entry['inning_display'] = inning_info['display']
            if duration:
                entry['duration'] = duration
        
        # 已結束顯示勝敗投手
        if status == '已結束':
            if g.get('WinningPitcherName'):
                entry['winning_pitcher'] = g.get('WinningPitcherName')
            if g.get('LoserPitcherName'):
                entry['losing_pitcher'] = g.get('LoserPitcherName')
            if g.get('MvpName'):
                entry['mvp'] = g.get('MvpName')
            if duration:
                entry['duration'] = duration
        
        # 延賽/取消原因
        if status in ('延賽', '保留', '取消'):
            if g.get('GameResult'):
                entry['reason'] = g.get('GameResult')
        
        # box score 連結
        year = g.get('Year', date_str[:4])
        kind_code = g.get('KindCode', 'A')
        sno = g.get('GameSno', '')
        if sno:
            entry['box_url'] = f'https://cpbl.com.tw/box/index?year={year}&kindCode={kind_code}&gameSno={sno}'
            entry['live_url'] = f'https://cpbl.com.tw/box/live?year={year}&kindCode={kind_code}&gameSno={sno}'
        
        result.append(entry)
    
    return result


def query_live(
    date_filter: Optional[str] = None,
    team: Optional[str] = None,
    kind: str = 'A',
) -> list[dict]:
    """
    查詢即時比分（主要入口）
    
    Args:
        date_filter: 日期 (YYYY-MM-DD)，預設今天
        team: 球隊過濾
        kind: 賽事類型
    
    Returns:
        比賽摘要列表
    """
    target_date = date_filter or _get_today_tw()
    
    games_raw = fetch_games_for_date(target_date, kind)
    
    if team:
        games_raw = [
            g for g in games_raw
            if team in (g.get('VisitingTeamName', '') or '')
            or team in (g.get('HomeTeamName', '') or '')
        ]
    
    return build_live_summary(games_raw, target_date)


def format_text(games: list[dict]) -> str:
    """格式化成文字輸出"""
    if not games:
        return '今天沒有 CPBL 賽事 🏟️'
    
    lines = []
    
    # 統計狀態
    live_count = sum(1 for g in games if g['status'] == '比賽中')
    finished_count = sum(1 for g in games if g['status'] == '已結束')
    upcoming_count = sum(1 for g in games if g['status'] == '未開打')
    postpone_count = sum(1 for g in games if g['status'] == '延賽')
    other_count = len(games) - live_count - finished_count - upcoming_count - postpone_count
    
    header_parts = []
    if live_count:
        header_parts.append(f'🔴 進行中 {live_count}')
    if finished_count:
        header_parts.append(f'✅ 已結束 {finished_count}')
    if postpone_count:
        header_parts.append(f'🌧️ 延賽 {postpone_count}')
    if upcoming_count:
        header_parts.append(f'⏳ 未開打 {upcoming_count}')
    if other_count:
        header_parts.append(f'📢 其他 {other_count}')
    
    lines.append(f'⚾ CPBL 即時比分 | {games[0]["date"]}')
    lines.append(' | '.join(header_parts))
    lines.append('─' * 50)
    
    for g in games:
        emoji = g['status_emoji']
        status = g['status']
        
        # 基本行
        if g.get('score_display'):
            line = f'{emoji} {g["away_team"]} {g["score_display"]} {g["home_team"]}'
        else:
            line = f'{emoji} {g["away_team"]} vs {g["home_team"]}'
        
        # 時間或場次
        parts = []
        if g.get('time'):
            parts.append(g['time'])
        if g.get('game_sno'):
            parts.append(f'#{g["game_sno"]}')
        if parts:
            line += f'  ({", ".join(parts)})'
        
        lines.append(line)
        
        # 場館
        if g.get('venue'):
            lines.append(f'   📍 {g["venue"]}')
        
        # 比賽中：顯示局數 + 時長
        if status == '比賽中':
            live_parts = []
            if g.get('inning_display'):
                live_parts.append(f'⚾ {g["inning_display"]}')
            if g.get('duration'):
                live_parts.append(f'⏱️ {g["duration"]}')
            if live_parts:
                lines.append(f'   {" | ".join(live_parts)}')
        
        # 已結束：勝敗投
        if status == '已結束':
            details = []
            if g.get('winning_pitcher'):
                details.append(f'勝: {g["winning_pitcher"]}')
            if g.get('losing_pitcher'):
                details.append(f'敗: {g["losing_pitcher"]}')
            if g.get('mvp'):
                details.append(f'MVP: {g["mvp"]}')
            if g.get('duration'):
                details.append(f'⏱️ {g["duration"]}')
            if details:
                lines.append(f'   {" | ".join(details)}')
        
        # 異常狀態
        if status in ('延賽', '保留', '取消', '比賽暫停'):
            if g.get('reason'):
                lines.append(f'   📢 {g["reason"]}')
        
        lines.append('')
    
    return '\n'.join(lines).strip()


def main():
    parser = argparse.ArgumentParser(
        description='CPBL 即時比分查詢',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  # 查今天即時比分
  uv run cpbl_live.py
  
  # 查特定日期
  uv run cpbl_live.py --date 2026-04-01
  
  # 查特定球隊
  uv run cpbl_live.py --team 兄弟
  
  # 純文字格式
  uv run cpbl_live.py --output text
        '''
    )
    
    parser.add_argument('--date', '-d', type=str, help='日期 (YYYY-MM-DD)，預設今天')
    parser.add_argument('--team', '-t', type=str, help='球隊過濾（支援簡稱如：兄弟、獅、悍將）')
    parser.add_argument('--kind', '-k', type=str, default='A',
                        choices=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'X'],
                        help='賽事類型（預設 A）')
    parser.add_argument('--output', '-o', type=str, default='json', choices=['json', 'text'],
                        help='輸出格式（預設 json）')
    
    args = parser.parse_args()
    
    # 球隊模糊匹配
    team = resolve_team_cli(args.team)
    
    # 驗證日期
    target_date = args.date
    if target_date:
        validate_date(target_date)
    else:
        target_date = _get_today_tw()
    
    kind_name = KIND_NAMES.get(args.kind, '未知')
    print(f'✅ 查詢日期：{target_date} ({kind_name})', file=sys.stderr)
    
    try:
        games = query_live(
            date_filter=target_date,
            team=team,
            kind=args.kind,
        )
        
        if not games:
            print(f'⚠️ {target_date} 沒有賽事', file=sys.stderr)
        
        if args.output == 'json':
            print(json.dumps(games, ensure_ascii=False, indent=2))
        else:
            print(format_text(games))
    
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
