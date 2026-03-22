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
CPBL API 共用模組
負責 CSRF token 取得、快取與 API 呼叫
"""

import json
import re
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any

# 快取檔案路徑（依據 TASK-001 要求）
TOKEN_CACHE_FILE = Path('/tmp/cpbl_csrf_token.txt')


class CPBLAPI:
    """CPBL 官方隱藏 API 封裝"""
    
    BASE_URL = 'https://cpbl.com.tw'
    
    def __init__(self):
        self.csrf_token: Optional[str] = None
        self.token_expire: Optional[datetime] = None
        self._load_token_cache()
    
    def _load_token_cache(self):
        """載入快取的 CSRF token"""
        if TOKEN_CACHE_FILE.exists():
            try:
                with open(TOKEN_CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    self.csrf_token = data.get('token')
                    expire_str = data.get('expire')
                    if expire_str:
                        self.token_expire = datetime.fromisoformat(expire_str)
            except:
                pass
    
    def _save_token_cache(self):
        """儲存 CSRF token 到快取"""
        data = {
            'token': self.csrf_token,
            'expire': self.token_expire.isoformat() if self.token_expire else None
        }
        with open(TOKEN_CACHE_FILE, 'w') as f:
            json.dump(data, f)
    
    def _is_token_valid(self) -> bool:
        """檢查 token 是否有效"""
        if not self.csrf_token or not self.token_expire:
            return False
        return datetime.now() < self.token_expire
    
    def fetch_csrf_token(self, force_refresh: bool = False) -> str:
        """
        取得 CSRF token
        
        Args:
            force_refresh: 強制重新取得（忽略快取）
        
        Returns:
            CSRF token 字串
        """
        # 檢查快取
        if not force_refresh and self._is_token_valid():
            return self.csrf_token
        
        # 使用 scrapling DynamicFetcher 取得頁面
        from scrapling.fetchers import DynamicFetcher
        from bs4 import BeautifulSoup
        
        # 從 schedule 頁面取得 token
        url = f'{self.BASE_URL}/schedule?KindCode=A'
        page = DynamicFetcher.fetch(url, wait=5, headless=True)
        soup = BeautifulSoup(page.body, 'lxml')
        html = str(soup)
        
        # 用正則找出 token
        matches = re.findall(r"RequestVerificationToken['\"]?\s*[:=]\s*['\"]([^'\"]{20,})", html)
        
        if not matches:
            raise ValueError('無法從頁面取得 CSRF token')
        
        self.csrf_token = matches[0]
        # Token 有效期設為 1 小時
        self.token_expire = datetime.now() + timedelta(hours=1)
        self._save_token_cache()
        
        return self.csrf_token
    
    def post_api(self, endpoint: str, data: dict) -> dict:
        """
        發送 POST 請求到 CPBL API
        
        Args:
            endpoint: API 路徑（如 /schedule/getgamedatas）
            data: POST 資料
        
        Returns:
            JSON 回應
        """
        # 確保有 token
        if not self._is_token_valid():
            self.fetch_csrf_token()
        
        url = f'{self.BASE_URL}{endpoint}'
        
        # 準備 headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'RequestVerificationToken': self.csrf_token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 編碼 POST 資料
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        
        # 發送請求
        req = urllib.request.Request(url, data=post_data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
        except urllib.error.HTTPError as e:
            # 如果 403/401，可能是 token 過期，重試一次
            if e.code in (401, 403):
                self.fetch_csrf_token(force_refresh=True)
                headers['RequestVerificationToken'] = self.csrf_token
                req = urllib.request.Request(url, data=post_data, headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=30) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return result
            raise


# 提供全域實例
_api_instance: Optional[CPBLAPI] = None

def get_api() -> CPBLAPI:
    """取得 CPBL API 實例（singleton）"""
    global _api_instance
    if _api_instance is None:
        _api_instance = CPBLAPI()
    return _api_instance


def get_csrf_token(force_refresh: bool = False) -> str:
    """取得 CSRF token（便捷函式）"""
    return get_api().fetch_csrf_token(force_refresh)


def post_api(endpoint: str, data: dict) -> dict:
    """發送 POST 請求（便捷函式）"""
    return get_api().post_api(endpoint, data)


if __name__ == '__main__':
    # 測試
    api = CPBLAPI()
    
    print('測試 CSRF token 取得...')
    token = api.fetch_csrf_token()
    print(f'Token: {token[:20]}...')
    print(f'快取位置: {TOKEN_CACHE_FILE}')
    
    print('\n測試 post_api()...')
    result = api.post_api('/schedule/getgamedatas', {
        'calendar': '2025/01/01',
        'location': '',
        'kindCode': 'A'
    })
    
    if result.get('Success'):
        games = json.loads(result.get('GameDatas', '[]'))
        print(f'✅ 取得 {len(games)} 場 2025 年比賽')
    else:
        print('❌ API 呼叫失敗')
