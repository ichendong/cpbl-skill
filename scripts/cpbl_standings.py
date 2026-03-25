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
CPBL 戰績排名查詢
使用官方 API: /standings/seasonaction
注意：此 API 只返回表頭結構，不包含資料
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

# 引入共用模組
sys.path.insert(0, str(Path(__file__).parent))
from _cpbl_api import post_api_html


def query_standings(
    year: Optional[int] = None,
    kind: str = 'A'
) -> dict:
    """
    查詢球隊戰績

    Args:
        year: 年份（預設今年）
        kind: A=一軍, W=二軍

    Returns:
        戰績資料（目前 API 只返回表頭，無法取得資料）
    """
    if year is None:
        year = datetime.now().year

    try:
        html = post_api_html('/standings/seasonaction', {
            'year': str(year),
            'kindCode': kind
        })

        # 檢查 HTML 中是否有資料行
        has_data = '<td' in html

        if not has_data:
            return {
                'year': year,
                'kind': kind,
                'source': 'api_limited',
                'message': '戰績 API 只返回表頭結構，無法取得資料',
                'note': 'CPBL 官網的反爬蟲機制導致無法取得完整資料',
                'url': f'https://cpbl.com.tw/standings?KindCode={kind}',
                'data': [],
                'tables': [
                    '球隊對戰戰績',
                    '團隊投球成績',
                    '團隊打擊成績',
                    '團隊守備成績'
                ]
            }

        # 如果有資料，解析 HTML（目前不會進入這個分支）
        return {
            'year': year,
            'kind': kind,
            'source': 'api',
            'data': []  # 需要實作 HTML 解析
        }

    except Exception as e:
        return {
            'year': year,
            'kind': kind,
            'source': 'error',
            'error': str(e),
            'message': '無法取得戰績資料',
            'url': f'https://cpbl.com.tw/standings?KindCode={kind}',
            'data': []
        }


def main():
    parser = argparse.ArgumentParser(
        description='CPBL 戰績排名查詢',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  # 查詢今年一軍戰績
  uv run cpbl_standings.py

  # 查詢 2025 年戰績
  uv run cpbl_standings.py --year 2025

  # 查詢二軍戰績
  uv run cpbl_standings.py --kind W

備註:
  由於 CPBL 官網的反爬蟲機制，戰績 API 目前無法取得完整資料。
  請直接前往官網查詢: https://cpbl.com.tw/standings

  已確認的 API endpoint: /standings/seasonaction
  此 API 只返回表頭結構，不包含資料。
        '''
    )

    parser.add_argument('--year', '-y', type=int, help='年份（預設今年）')
    parser.add_argument('--kind', '-k', type=str, default='A', choices=['A', 'W'],
                        help='A=一軍, W=二軍（預設 A）')
    parser.add_argument('--output', '-o', type=str, default='json', choices=['json', 'text'],
                        help='輸出格式（預設 json）')

    args = parser.parse_args()

    try:
        standings = query_standings(year=args.year, kind=args.kind)

        if args.output == 'json':
            print(json.dumps(standings, ensure_ascii=False, indent=2))
        else:
            print(f"年份: {standings['year']}")
            print(f"軍種: {'一軍' if standings['kind'] == 'A' else '二軍'}")
            print(f"\n{standings['message']}")
            if standings.get('tables'):
                print(f"\n可用表格: {', '.join(standings['tables'])}")
            print(f"\n官網連結: {standings['url']}")

    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
