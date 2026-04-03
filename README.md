# CPBL Skill - 中華職棒資訊查詢 ⚾

查詢中華職棒 CPBL 即時比分 已完賽結果 賽程 戰績 球員數據 新聞與歷史資料

## v1.3.2 重點

- 移除與 CPBL 功能無關的 `scripts/ralph/` 自治開發框架
- 清掉 bundle 內的 Autonomous Coder 痕跡 降低審查時的 suspicious 風險
- 保留原本所有 CPBL 查詢腳本與文件結構 不影響 skill 主功能

## v1.3.1 重點

- 新增 `cpbl_live.py` 支援今日或指定日期即時比分
- `cpbl_games.py` 補上賽後全壘打 中繼點 救援點 觀眾人數
- 新增 `box_url` 與 `live_url` 方便追詳細戰況
- 改善完賽判斷 避開官方 `PresentStatus` 不可靠的坑
- 精簡 `SKILL.md` 結構 改成更清楚的腳本導向說明

## 功能

- 即時比分 `scripts/cpbl_live.py`
- 已完賽結果 `scripts/cpbl_games.py`
- 賽程查詢 `scripts/cpbl_schedule.py`
- 戰績排名 `scripts/cpbl_standings.py`
- 球員與排行榜數據 `scripts/cpbl_stats.py`
- 近期新聞 `scripts/cpbl_news.py`
- 歷史獎項與紀錄 以台灣棒球維基館補強

## 資料來源

| 來源 | 用途 |
|------|------|
| CPBL 官方站隱藏 API | 即時比分 比賽結果 賽程 戰績 球員數據 |
| 台灣棒球維基館 | 年度獎項 歷史紀錄 球員生涯資料 |

## 快速開始

```bash
uv run scripts/cpbl_live.py --output text
uv run scripts/cpbl_games.py --date 2026-04-01 --output text
uv run scripts/cpbl_schedule.py --month 2026-04 --all
uv run scripts/cpbl_standings.py
uv run scripts/cpbl_stats.py --year 2025 --category batting --top 10
uv run scripts/cpbl_news.py --keyword 中信兄弟
```

## 授權

僅供學習與個人使用 請遵守 CPBL 官網與資料來源的使用條款
