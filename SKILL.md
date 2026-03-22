---
description: 查詢中華職棒 CPBL 比賽結果、賽程、戰績、球員數據（打擊率、防禦率等）。支援所有賽事類型（例行賽/熱身賽/明星賽/季後賽等）、球隊過濾。關鍵字：中華職棒、CPBL、棒球、賽程、戰績、球員數據、打擊、投球、比分。
---

# CPBL Skill V5 - 中華職棒資訊查詢 ⚾🏆

使用 **CPBL 官方隱藏 API** 取得資料，快速穩定！

## 技術架構

- **主要資料來源**: CPBL 官方隱藏 API（POST 請求 + CSRF token）
- **次要資料來源**: 台灣棒球維基館 (`https://twbsball.dils.tku.edu.tw/`)
  - 適用於官方 API 無法查詢的資料：年度 MVP、年度獎項、歷史紀錄、球員生涯資料等
  - 使用 `web_fetch` 抓取頁面後解析
  - 搜尋 URL 格式：`https://twbsball.dils.tku.edu.tw/wiki/index.php?title=關鍵字`
  - 常用頁面：
    - 年度 MVP：`中華職棒年度最有價值球員`
    - 年度新人王：`中華職棒年度新人王`
    - 球員查詢：球員姓名（含括號年份）
- **快取機制**: CSRF token 快取 1 小時，避免重複取得
- **備用方案**: standings 目前無 API，提供官網連結

## 功能狀態

| 功能 | 腳本 | 狀態 | 資料來源 |
|------|------|------|----------|
| 比賽結果 | cpbl_games.py | ✅ 可用 | 官方 API `/schedule/getgamedatas` |
| 賽程查詢 | cpbl_schedule.py | ✅ 可用 | 官方 API `/schedule/getgamedatas` |
| 戰績排名 | cpbl_standings.py | ⚠️ 受限 | API `/standings/seasonaction` 只返回表頭 |
| 球員數據 | cpbl_stats.py | ✅ 可用 | 官方 API `/stats/recordall` |
| 年度獎項 | web_fetch | ✅ 可用 | 台灣棒球維基館 |
| 新聞查詢 | cpbl_news.py | ⚠️ 備用 | web_search |

## 賽事類型 (kindCode)

| 代碼 | 名稱 |
|------|------|
| A | 一軍例行賽（預設） |
| B | 一軍明星賽 |
| C | 一軍總冠軍賽 |
| D | 二軍例行賽 |
| E | 一軍季後挑戰賽 |
| F | 二軍總冠軍賽 |
| G | 一軍熱身賽 |
| H | 未來之星邀請賽 |
| X | 國際交流賽 |

## 快速開始

### 查詢比賽結果

```bash
# 查詢 2025 年所有比賽（前 10 場）
uv run scripts/cpbl_games.py --year 2025 --limit 10

# 查詢特定日期
uv run scripts/cpbl_games.py --date 2025-03-29

# 查詢特定球隊
uv run scripts/cpbl_games.py --team 中信 --year 2025

# 查詢二軍比賽
uv run scripts/cpbl_games.py --year 2025 --kind W

# 查詢一軍熱身賽
uv run scripts/cpbl_games.py --kind G --year 2026 --limit 5

# 文字格式輸出
uv run scripts/cpbl_games.py --year 2025 --limit 5 --output text
```

### 查詢賽程

```bash
# 查詢今年所有未來賽程
uv run scripts/cpbl_schedule.py

# 查詢特定日期
uv run scripts/cpbl_schedule.py --date 2025-03-29

# 查詢整月（包含已完成）
uv run scripts/cpbl_schedule.py --month 2025-03 --all

# 查詢特定球隊
uv run scripts/cpbl_schedule.py --team 樂天

# 查詢二軍賽程
uv run scripts/cpbl_schedule.py --kind W
```

### 查詢戰績

```bash
# 查詢今年一軍戰績
uv run scripts/cpbl_standings.py

# 查詢二軍戰績
uv run scripts/cpbl_standings.py --kind W
```

**注意**: 戰績 API 目前無法取得，請直接前往官網查詢。

### 查詢球員數據

```bash
# 查詢 2025 年打擊排行榜（前 10 名）
uv run scripts/cpbl_stats.py --year 2025 --category batting --top 10

# 查詢投手數據
uv run scripts/cpbl_stats.py --year 2025 --category pitching --top 5

# 查詢特定球隊球員
uv run scripts/cpbl_stats.py --team 中信 --category batting

# 查詢二軍數據
uv run scripts/cpbl_stats.py --kind W --category batting
```

**輸出範例**:
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

### 查詢新聞

```bash
# 搜尋 CPBL 新聞
uv run scripts/cpbl_news.py --keyword 中信兄弟
```

**注意**: 新聞查詢需要使用 Sonic 的 web_search 功能。

## 腳本說明

### cpbl_games.py — 比賽結果查詢

**參數**:
- `--year, -y`: 年份（預設今年）
- `--date, -d`: 特定日期 (YYYY-MM-DD)
- `--team, -t`: 球隊名過濾（部分匹配）
- `--kind, -k`: 賽事類型代碼（預設 A）。A=一軍例行賽 B=明星賽 C=總冠軍 D=二軍例行賽 E=季後挑戰賽 F=二軍總冠軍 G=一軍熱身賽 H=未來之星 X=國際交流賽
- `--limit, -l`: 限制筆數
- `--output, -o`: json/text（預設 json）

**輸出格式**:
```json
[
  {
    "date": "2025-03-29",
    "time": "17:05",
    "away_team": "統一7-ELEVEn獅",
    "home_team": "中信兄弟",
    "away_score": 8,
    "home_score": 0,
    "venue": "大巨蛋",
    "status": "completed",
    "winning_pitcher": "布雷克",
    "losing_pitcher": "*德保拉",
    "mvp": "布雷克"
  }
]
```

### cpbl_schedule.py — 賽程查詢

**參數**:
- `--year, -y`: 年份（預設今年）
- `--month, -m`: 月份 (YYYY-MM)
- `--date, -d`: 特定日期 (YYYY-MM-DD)
- `--team, -t`: 球隊名過濾（部分匹配）
- `--kind, -k`: 賽事類型代碼（預設 A）。A=一軍例行賽 B=明星賽 C=總冠軍 D=二軍例行賽 E=季後挑戰賽 F=二軍總冠軍 G=一軍熱身賽 H=未來之星 X=國際交流賽
- `--limit, -l`: 限制筆數
- `--all, -a`: 包含已完成的比賽
- `--output, -o`: json/text（預設 json）

**輸出格式**:
```json
[
  {
    "date": "2025-03-29",
    "weekday": "六",
    "time": "17:05",
    "away_team": "統一7-ELEVEn獅",
    "home_team": "中信兄弟",
    "venue": "大巨蛋",
    "game_no": 1,
    "status": "scheduled"
  }
]
```

### cpbl_standings.py — 戰績排名

目前無法取得資料，提供官網連結。

### cpbl_stats.py — 球員數據

目前無法取得資料，提供官網連結。

### cpbl_news.py — 新聞查詢

需要使用 Sonic 的 web_search 功能。

## 技術細節

### 官方隱藏 API

**賽程/比賽 API**:
```
POST https://cpbl.com.tw/schedule/getgamedatas
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest
RequestVerificationToken: <CSRF token>

Body:
calendar=2025/01/01&location=&kindCode=A
```

**參數說明**:
- `calendar`: `YYYY/MM/DD`（用年份的 1/1 取得整年）
- `location`: 場地過濾（空字串 = 全部）
- `kindCode`: 賽事類型代碼（見上方對照表）

**回傳格式**:
```json
{
  "Success": true,
  "GameDatas": "<JSON string>"
}
```

**球員數據 API**:
```
POST https://cpbl.com.tw/stats/recordall
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest
RequestVerificationToken: <CSRF token>

Body:
year=2025&kindcode=A&position=01&sortby=01
```

**參數說明**:
- `year`: 年份（必填）
- `kindcode`: 賽事類型代碼（見上方對照表）
- `position`: `01`（打擊）/ `02`（投球）
- `sortby`: `01`（主要指標，如打擊率/防禦率）

**回傳**: HTML 表格（需用 BeautifulSoup 解析）

**戰績 API（受限）**:
```
POST https://cpbl.com.tw/standings/seasonaction
```

⚠️ 此 API 只返回表頭結構，不包含資料。

### CSRF Token 取得

使用 scrapling DynamicFetcher 從頁面取得 token，並快取 1 小時。

```python
from scrapling.fetchers import DynamicFetcher
from bs4 import BeautifulSoup
import re

page = DynamicFetcher.fetch('https://cpbl.com.tw/schedule?KindCode=A', wait=5, headless=True)
soup = BeautifulSoup(page.body, 'lxml')
text = str(soup)
matches = re.findall(r"RequestVerificationToken['\"]?\s*[:=]\s*['\"]([^'\"]{20,})", text)
token = matches[0]
```

## 依賴套件

所有腳本會自動透過 `uv` 安裝：
- `scrapling[ai]` - CSRF token 取得
- `beautifulsoup4` - HTML 解析
- `lxml` - 高效解析器

## 已知限制

1. **戰績排名**: API `/standings/seasonaction` 只返回表頭，無法取得資料。CPBL 官網反爬蟲機制嚴格，DynamicFetcher 也會被擋截。
2. **CSRF Token**: 首次取得較慢（需要跑 scrapling），之後會快取 1 小時
3. **2026 年資料**: 目前球季尚未開始，資料可能不完整

## 疑難排解

### 無法取得 CSRF Token

```bash
# 測試 scrapling 是否正常
uv run --with "scrapling[ai]" python3 -c "
from scrapling.fetchers import DynamicFetcher
page = DynamicFetcher.fetch('https://cpbl.com.tw/schedule', wait=5)
print(f'Status: {page.status}, Length: {len(page.body)}')
"
```

### 清除快取

```bash
# CSRF token 快取位置
rm -rf ~/.cache/cpbl_api/
```

## 更新日誌

### v5.0.0 (2026-03-20)
- ✅ 支援所有賽事類型：A/B/C/D/E/F/G/H/X（熱身賽、明星賽、總冠軍、國際交流賽等）
- ✅ `--kind` 參數擴充為 9 種賽事代碼
- ✅ stderr 顯示友善的中文賽事類型名稱
- 📝 SKILL.md 新增賽事類型對照表與熱身賽查詢範例

### v3.1.0 (2026-03-20)
- ✅ 球員數據查詢完成（API `/stats/recordall` + HTML 解析）
- ✅ 支援打擊/投球排行榜、球隊過濾、筆數限制
- 📝 更新 SKILL.md 文檔，記錄所有 API endpoint

### v3.0.0 (2026-03-20)
- 🎉 完全重寫，改用官方隱藏 API
- ✅ 比賽結果查詢（完整比分、勝敗投手、MVP）
- ✅ 賽程查詢（支援日期、月份、球隊過濾）
- ✅ CSRF token 快取機制（1 小時）
- ⚠️ 戰績 API 受限（只返回表頭）

## 授權

本 skill 僅供學習和個人使用。資料來源為 CPBL 官網，請遵守官方使用條款。
