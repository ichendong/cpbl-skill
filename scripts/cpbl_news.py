#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
CPBL 新聞查詢
使用 web_search（Brave）搜尋
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from typing import Optional

def search_cpbl_news(
    keyword: str,
    limit: int = 10
) -> list[dict]:
    """
    搜尋 CPBL 相關新聞
    
    Args:
        keyword: 搜尋關鍵字
        limit: 筆數限制
    
    Returns:
        新聞列表
    """
    # 使用 web_search tool（需要從外部傳入）
    # 這裡用備用方案：直接回傳提示訊息
    return []


def main():
    parser = argparse.ArgumentParser(
        description='CPBL 新聞查詢',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  # 搜尋中信兄弟相關新聞
  uv run cpbl_news.py --keyword 中信兄弟
  
  # 搜尋樂天桃猿新聞（限制 5 筆）
  uv run cpbl_news.py --keyword 樂天桃猿 --limit 5
  
  # 搜尋比賽結果
  uv run cpbl_news.py --keyword "CPBL 戰報"

備註:
  此腳本需要配合 OpenClaw web_search tool 使用。
  請讓 Sonic 代為執行搜尋。
        '''
    )
    
    parser.add_argument('--keyword', '-k', type=str, required=True,
                        help='搜尋關鍵字')
    parser.add_argument('--limit', '-l', type=int, default=10,
                        help='筆數限制（預設 10）')
    parser.add_argument('--output', '-o', type=str, default='json',
                        choices=['json', 'text'],
                        help='輸出格式（預設 json）')
    
    args = parser.parse_args()
    
    # 回傳提示訊息
    result = {
        'keyword': args.keyword,
        'limit': args.limit,
        'message': '請使用 Sonic 的 web_search 功能搜尋新聞',
        'suggestion': f'搜尋關鍵字: "CPBL {args.keyword}"'
    }
    
    if args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"關鍵字: {args.keyword}")
        print(f"限制: {args.limit} 筆")
        print(f"\n{result['message']}")
        print(f"建議: {result['suggestion']}")


if __name__ == '__main__':
    main()
