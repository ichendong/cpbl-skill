# Progress Log

Started: 2026-03-20 20:19

## TASK-001 ✅ 完成 (2026-03-20 20:38)

**修復 _cpbl_api.py 共用模組**

修改內容：
- 快取路徑改為 `/tmp/cpbl_csrf_token.txt`（符合任務要求）
- 加上公開的 `post_api()` 方法到 CPBLAPI 類別
- 加上便捷函式 `get_csrf_token()` 和 `post_api()` 供外部使用
- Token 有效期 1 小時，自動重試機制處理 401/403

實測結果：
- Token 取得成功：aYJcM3WDH7_1uzX5hrcn...
- API 呼叫成功：取得 393 場 2025 年比賽
- 快取位置：/tmp/cpbl_csrf_token.txt

學習：
- scrapling DynamicFetcher 能成功繞過 CPBL 的反爬蟲
- Token 從頁面 JS 用 regex `RequestVerificationToken['\"]?\s*[:=]\s*['\"]([^'\"]{20,})` 提取

## TASK-002 ✅ 完成 (2026-03-20 20:39)

**重寫 cpbl_games.py 比賽結果查詢**

修改內容：
- 使用 `post_api()` 呼叫 /schedule/getgamedatas
- 支援 --year, --date, --team, --kind, --limit 參數
- 輸出 JSON 格式包含 date, away_team, home_team, away_score, home_score, venue, winning_pitcher, losing_pitcher, mvp
- 過濾條件：日期、球隊名稱部分匹配

實測結果：
- `uv run cpbl_games.py --year 2025 --limit 3` ✅
- `uv run cpbl_games.py --team 樂天 --year 2025 --limit 3` ✅
- `uv run cpbl_games.py --help` ✅

輸出範例：
```json
[
  {
    "date": "2025-10-06",
    "away_team": "樂天桃猿",
    "home_team": "統一7-ELEVEn獅",
    "away_score": 5,
    "home_score": 4,
    "venue": "澄清湖",
    "winning_pitcher": "賴胤豪",
    "losing_pitcher": "*姚杰宏",
    "mvp": "曾家輝"
  }
]
```

學習：
- API 回傳的 GameDatas 是 JSON 字串，需要再 parse
- 2025 年共 393 場比賽

## TASK-003 ✅ 完成 (2026-03-20 20:40)

**重寫 cpbl_schedule.py 賽程查詢**

修改內容：
- 使用 `post_api()` 呼叫 /schedule/getgamedatas
- 預設只顯示未完成的比賽（有 --all 可以顯示全部）
- 支援 --year, --month, --date, --team, --kind, --limit 參數
- 輸出含星期幾、時間、場地

實測結果：
- `uv run cpbl_schedule.py --year 2025 --month 2025-03 --limit 3 --all` ✅
- `uv run cpbl_schedule.py --help` ✅

輸出範例：
```json
[
  {
    "date": "2025-03-29",
    "weekday": "六",
    "time": "17:05",
    "away_team": "統一7-ELEVEn獅",
    "home_team": "中信兄弟",
    "venue": "大巨蛋",
    "away_score": 8,
    "home_score": 0
  }
]
```

學習：
- 預設過濾掉已完成的比賽，避免賽程表太長
- 星期幱用中文字元顯示

## TASK-004 ✅ 完成 (2026-03-20 20:46)

**偵查戰績 API endpoint**

發現：
- `/standings/seasonaction` - 戰績 API（返回 HTML 片段，不是 JSON）
- 回傳包含 4 個表格：球隊對戰戰績、團隊投球成績、團隊打擊成績、團隊守備成績
- 需用 BeautifulSoup 解析 HTML

實測：
- POST /standings/seasonaction (year=2025) ✅
- 回傳 5272 bytes HTML 片段

學習：
- CPBL 頁面反爬蟲很強，DynamicFetcher 會被擋（顯示 "Oops" 頁面）
- 但直接 POST API 反而能成功（需要正確的 CSRF token）
- API 回傳的是 HTML 而非 JSON，需特別處理

## TASK-005 ✅ 完成 (2026-03-20 20:47)

**偵查球員數據 API endpoint**

發現：
- `/stats/toplistaction` - 球員數據 API（返回 HTML 片段）
- 回傳包含 TopFiveList，顯示各項數據排行榜
- 參數：year, kindCode

實測：
- POST /stats/toplistaction (year=2025, kindCode=A) ✅
- 回傳 3616 bytes HTML 片段

學習：
- 多數 endpoint 返回完整 HTML 頁面（可能是錯誤頁面）
- 只有 /stats/toplistaction 返回有意義的資料片段
- 一樣需用 BeautifulSoup 解析

## TASK-006 ✅ 完成（有 API 限制）(2026-03-20 20:52)

**實作 cpbl_standings.py 戰績排名**

實作結果：
- 找到 API endpoint: `/standings/seasonaction`
- 但 API 只返回表頭結構（5272 bytes HTML），無資料行（<td>）
- scrapling dynamic mode 也被 CPBL 反爬蟲擋截（顯示 "Oops" 頁面）
- 誠實回報 API 限制，不提供假資料

實測：
- `uv run cpbl_standings.py --year 2025` ✅（返回 api_limited 狀態）
- `uv run cpbl_standings.py --help` ✅

輸出範例：
```json
{
  "year": 2025,
  "kind": "A",
  "source": "api_limited",
  "message": "戰績 API 只返回表頭結構，無法取得資料",
  "note": "CPBL 官網的反爬蟲機制導致無法取得完整資料",
  "url": "https://cpbl.com.tw/standings?KindCode=A",
  "data": []
}
```

學習：
- CPBL 反爬蟲非常嚴格，DynamicFetcher 無法繞過
- API endpoint 存在但資料不完整
- 誠實回報限制比假裝有資料更重要

## TASK-007 ✅ 完成 (2026-03-20 20:55)

**實作 cpbl_stats.py 球員數據**

實作結果：
- 找到可用 API: `/stats/recordall`（需要 year 參數）
- 成功解析 HTML 表格（82304 bytes，495 個 <td>）
- 支援打擊/投球排行榜、球隊過濾、筆數限制

實測：
- `uv run cpbl_stats.py --year 2025 --category batting --top 5` ✅
- `uv run cpbl_stats.py --help` ✅

輸出範例：
```json
[
  {
    "rank": 1,
    "player": "台鋼雄鷹吳念庭",
    "avg": "0.328",
    "games": "88",
    "hits": "109",
    "hr": "2",
    "rbi": "50"
  }
]
```

學習：
- /stats/toplistaction 只返回框架，/stats/recordall 才有資料
- year 參數是關鍵，沒有 year 會返回空表格

## TASK-008, TASK-009, TASK-010 ✅ 完成 (2026-03-20 20:58)

**更新 SKILL.md、frontmatter、清理檔案**

完成項目：
- 更新 SKILL.md 功能狀態表、API 文檔、已知限制
- 加上 YAML frontmatter description（包含觸發關鍵字）
- 刪除 V2 殘留的 README.md

## 最終驗證 (2026-03-20 21:00)

執行最終驗證指令：

```bash
# 測試 1: cpbl_games.py
uv run cpbl_games.py --year 2025 --limit 3
# ✅ 成功返回 3 場比賽資料（2025-10-06, 2025-10-05, 2025-10-05）

# 測試 2: cpbl_schedule.py
uv run cpbl_schedule.py --year 2025 --month 2025-03 --limit 3
# ✅ 返回空陣列（因為預設只顯示未來賽程，需加 --all）

# 測試 3: cpbl_standings.py
uv run cpbl_standings.py --year 2025
# ⚠️ 返回 api_limited 狀態（API 只返回表頭）

# 測試 4: cpbl_stats.py
uv run cpbl_stats.py --year 2025 --category batting --top 5
# ✅ 成功返回前 5 名打擊排行榜
```

## 完成統計

- ✅ 完成任務：10/10 (100%)
- ✅ 可用功能：3/4 (比賽結果、賽程、球員數據)
- ⚠️ 受限功能：1/4 (戰績 API 只返回表頭)

## Codebase Patterns

- CPBL 官網隱藏 API: POST `/schedule/getgamedatas`, `/stats/recordall`
- CSRF token 從頁面 JS 用 regex 提取
- 腳本用 uv inline script metadata 管理依賴
- 不用 requests，用 urllib.request
- 繁體中文輸出和註解
