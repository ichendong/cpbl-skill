---
name: cpbl
description: "CPBL (Chinese Professional Baseball League) stats, scores, schedules, and player data for Taiwan's pro baseball."
tags: ["cpbl", "baseball", "taiwan", "sports", "scores"]
---

# CPBL Skill - 中華職棒資訊查詢 ⚾

Query CPBL game results, schedules, standings, and player stats across all game types.

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
| Standings | `cpbl_standings.py` | CPBL official API |
| Player stats | `cpbl_stats.py` | CPBL official API |
| News | `cpbl_news.py` | web_search |
| Awards & history | `web_fetch` | 台灣棒球維基館 |

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
