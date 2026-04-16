---
name: cpbl
description: Query CPBL 中華職棒 scores schedules live games standings player stats news and Taiwan baseball history for Taiwan users Use when the user asks about CPBL 戰績 賽程 即時比分 球員數據 排行榜 新聞 年度獎項 二軍 熱身賽 總冠軍賽 or historical CPBL facts
---

# CPBL

Use the bundled scripts for official-site data first.
Use `web_search` for recent news.
Use `web_fetch` on 台灣棒球維基館 for awards history or facts the official site does not expose.

## Primary workflow

1. Pick the narrowest script that matches the request.
2. Prefer text output for user-facing answers and JSON output for chaining or debugging.
3. If the official source cannot provide the requested historical fact, fetch 台灣棒球維基館.
4. If a result looks empty or partial, check `references/api-endpoints.md` before assuming the data does not exist.

## Script map

- `scripts/cpbl_live.py`  即時比分 今日賽況 指定日期賽況
- `scripts/cpbl_games.py`  已完賽結果 歷史比賽
- `scripts/cpbl_schedule.py`  賽程
- `scripts/cpbl_standings.py`  戰績 排名
- `scripts/cpbl_stats.py`  球員與排行榜數據

## Common commands

```bash
uv run skills/cpbl/scripts/cpbl_live.py --output text
uv run skills/cpbl/scripts/cpbl_live.py --date 2026-04-01 --team 兄弟
uv run skills/cpbl/scripts/cpbl_games.py --year 2025 --limit 10
uv run skills/cpbl/scripts/cpbl_schedule.py --month 2026-04 --all
uv run skills/cpbl/scripts/cpbl_standings.py
uv run skills/cpbl/scripts/cpbl_stats.py --year 2025 --category batting --top 10
```

## Game type codes

- `A` 一軍例行賽 預設
- `B` 一軍明星賽
- `C` 一軍總冠軍賽
- `D` 二軍例行賽
- `E` 一軍季後挑戰賽
- `F` 二軍總冠軍賽
- `G` 一軍熱身賽
- `H` 未來之星邀請賽
- `X` 國際交流賽

## Live score notes

- Live data is polled from the official source and is not push-based.
- API data may lag by a few minutes.
- When `PresentStatus` shows "比賽中" but `/box/getlive` returns `GameStatus=3`, the script corrects the status to "已結束" automatically.
- Finished games now include detailed Box Score: pitcher lines (IP/H/ER/K/BB/HR/H/SV/speed) and key batter lines (AB/H/RBI/HR/R/SB).
- Game duration is displayed in `Xh Xm` format (e.g. 3h23m).
- Monday often has no games unless adjusted by holidays or makeup scheduling.

## Schedule cache

If a request is about schedule, check `memory/cpbl_schedule_YYYY.md` first.
Refresh the cache when the file is missing, stale, or the requested range extends beyond the cached range.

Recommended refresh command

```bash
uv run skills/cpbl/scripts/cpbl_schedule.py --month YYYY-MM --all
```

## Postponement info

To check today's postponement announcements, fetch the official news page:
```
https://cpbl.com.tw/news
```
Look for the latest "延賽公告" entry. The live script now auto-detects postponed games (0:0 + no winning/losing pitcher).

## History and awards

Use 台灣棒球維基館 for MVP 新人王 歷史紀錄 球員生涯資料 or older facts that the official site does not return.
Search URL format

```text
https://twbsball.dils.tku.edu.tw/wiki/index.php?title=關鍵字
```

Common pages

- `中華職棒年度最有價值球員`
- `中華職棒年度新人王`
- `球員姓名`

## References

Read these only when needed

- `references/api-endpoints.md`  official-site endpoint behavior and quirks
- `references/summary.md`  project background and current limitations
- `references/test-report.md`  prior investigation details

## Known limits

- Some official endpoints return HTML fragments instead of JSON.
- Some standings and schedule flows are brittle because the site relies on AJAX plus CSRF.
- If a script returns partial data, do not invent missing values. State the limit and fall back to another source when possible.
