---
name: cpbl
description: "CPBL (Chinese Professional Baseball League) stats, scores, schedules, player data, and live scores for Taiwan's pro baseball."
tags: ["cpbl", "baseball", "taiwan", "sports", "scores", "live"]
---

# CPBL Skill - 中華職棒資訊查詢 ⚾

Query CPBL game results, schedules, standings, player stats, and **live scores** across all game types.

## Data Sources

| Source | Description |
|--------|-------------|
| CPBL official API | Game results, schedule, standings, player stats |
| 台灣棒球維基館 | Historical data not available via API |

### Secondary Source: 台灣棒球維基館

For data that the official API cannot provide (annual MVP, awards, historical records, player career data), use `web_fetch` to scrape [台灣棒球維基館](https://twbsball.dils.tku.edu.tw/).

**Search URL format:** `https://twbsball.dils.tku.edu.tw/wiki/index.php?title=關鍵字`

Common pages:
- 年度 MVP: `中華職棒年度最有價值球員`
- 年度新人王: `中華職棒年度新人王`
- Player lookup: Player name (include birth year in parentheses)

## Features

| Feature | Script | Source |
|---------|--------|--------|
| Game results | `cpbl_games.py` | CPBL official API |
| Schedule | `cpbl_schedule.py` | CPBL official API |
| **Live scores** | **`cpbl_live.py`** | **CPBL official API** |
| Standings | `cpbl_standings.py` | CPBL official API |
| Player stats | `cpbl_stats.py` | CPBL official API |
| News | `cpbl_news.py` | web_search |
| Awards & history | `web_fetch` | 台灣棒球維基館 |

## 🔴 即時比分 (Live Scores)

查詢今日或指定日期的賽事狀態（未開打 / 比賽中 / 已結束）。

```bash
# 查今天即時比分
uv run scripts/cpbl_live.py

# 查特定日期
uv run scripts/cpbl_live.py --date 2026-04-01

# 文字格式（推薦給使用者）
uv run scripts/cpbl_live.py --output text

# 查特定球隊
uv run scripts/cpbl_live.py --team 兄弟

# 二軍
uv run scripts/cpbl_live.py --kind D
```

### 輸出欄位說明

| 欄位 | 說明 |
|------|------|
| `status` | `未開打` / `比賽中` / `已結束` / `延賽` / `保留` / `取消` / `比賽暫停` |
| `away_score` / `home_score` | 即時比分（比賽中會持續更新） |
| `duration` | 比賽時長（已開打才有） |
| `winning_pitcher` / `losing_pitcher` | 勝敗投手（已結束才有） |
| `mvp` | 單場 MVP（已結束才有） |
| `box_url` | 成績看板連結 |
| `live_url` | 文字轉播連結 |

### 即時比分限制
- **資料來源**：CPBL 官方 API `/schedule/getgamedatas`，非 WebSocket 推播
- **更新頻率**：每次呼叫 API 都會取得最新資料，但不會自動刷新
- **局數**：API 本身不回傳第幾局，需透過 `box_url` 或 `live_url` 查看詳細戰況
- **延遲**：官方 API 可能有數分鐘延遲
- **週一通常沒比賽**，除非連假

## Quick Start

All scripts use `uv run` for dependency management.

### Game Results

```bash
uv run scripts/cpbl_games.py --year 2025 --limit 10
uv run scripts/cpbl_games.py --date 2025-03-29
uv run scripts/cpbl_games.py --team 中信 --year 2025
uv run scripts/cpbl_games.py --kind G --year 2026 --limit 5  # 熱身賽
```

### Schedule

```bash
uv run scripts/cpbl_schedule.py
uv run scripts/cpbl_schedule.py --date 2025-03-29
uv run scripts/cpbl_schedule.py --team 樂天
uv run scripts/cpbl_schedule.py --month 2025-03 --all
```

### Standings

```bash
uv run scripts/cpbl_standings.py
uv run scripts/cpbl_standings.py --kind W  # 二軍
```

### Player Stats

```bash
uv run scripts/cpbl_stats.py --year 2025 --category batting --top 10
uv run scripts/cpbl_stats.py --year 2025 --category pitching --top 5
uv run scripts/cpbl_stats.py --team 中信 --category batting
```

### News

```bash
uv run scripts/cpbl_news.py --keyword 中信兄弟
```

## Game Type Codes

| Code | Type |
|------|------|
| A | 一軍例行賽 (default) |
| B | 一軍明星賽 |
| C | 一軍總冠軍賽 |
| D | 二軍例行賽 |
| E | 一軍季後挑戰賽 |
| F | 二軍總冠軍賽 |
| G | 一軍熱身賽 |
| H | 未來之星邀請賽 |
| X | 國際交流賽 |

## ⚠️ 查詢規則
- **查即時比分**優先使用 `cpbl_live.py`，它合併了已結束 + 進行中 + 未開打的賽事
- **CPBL 週一通常沒比賽**，除非連假。查賽程從週二開始查。
- 先確認已存在的賽程快取再查 API，避免重複呼叫。

## 賽程快取 (Schedule Cache)

已快取的賽程存在 `memory/cpbl_schedule_YYYY.md`。查賽程前先確認快取是否過期：
- 如果賽程檔日期小於等於今天的比賽日期 → 重新查一次覆蓋
- 如果快取還在有效範圍 → 直接從檔案讀，不用再呼叫 API

使用者問賽程時：
1. 先讀 `memory/cpbl_schedule_2026.md`（或其他年份）
2. 如果缺失或過期 → `uv run skills/cpbl/scripts/cpbl_schedule.py --month YYYY-MM --all` 取得全部資料
3. 更新快取檔案

## Dependencies

Auto-installed via `uv`:
- `scrapling[ai]` — CSRF token fetching
- `beautifulsoup4` — HTML parsing
- `lxml` — Fast parser

## Notes

- Data source: CPBL official website (cpbl.com.tw)
- CSRF token cached for 1 hour (`~/.cache/cpbl_api/`)
- Standings API currently limited (returns headers only)
- For learning and personal use only. Please follow CPBL terms of service.
