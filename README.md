# CPBL Skill - 中華職棒資訊查詢 ⚾

查詢中華職棒 CPBL 即時比分 已完賽結果 賽程 戰績 球員數據 新聞與歷史資料

## 功能

- 即時比分 `scripts/cpbl_live.py`
- 已完賽結果 `scripts/cpbl_games.py`
- 賽程查詢 `scripts/cpbl_schedule.py`
- 戰績排名 `scripts/cpbl_standings.py`
- 球員與排行榜數據 `scripts/cpbl_stats.py`
- 近期新聞 直接用 `web_search` 查 CPBL 官網新聞頁
- 歷史獎項與紀錄 Scrapling StealthyFetcher 查台灣棒球維基館（可繞過 Anubis 防爬）

## 資料來源

| 來源 | 用途 | 備註 |
|------|------|------|
| CPBL 官方站隱藏 API | 即時比分 比賽結果 賽程 戰績 球員數據 | 直接可用 |
| 台灣棒球維基館 | 年度獎項 歷史紀錄 球員生涯資料 | 需 Scrapling StealthyFetcher 繞過 Anubis |

## 快速開始

```bash
uv run scripts/cpbl_live.py --output text
uv run scripts/cpbl_games.py --date 2026-04-01 --output text
uv run scripts/cpbl_schedule.py --month 2026-04 --all
uv run scripts/cpbl_standings.py
uv run scripts/cpbl_stats.py --year 2025 --category batting --top 10
# 近期新聞請用 web_search 搜尋 CPBL 官網
```

### 查詢台灣棒球維基館（需 Scrapling StealthyFetcher）

**安裝（首次使用前）：**
```bash
# 1. 建立 venv 並安裝依賴（如果 .venv 不存在）
cd skills/cpbl && uv venv && uv pip install -e .
# 2. 安裝 stealth browser（Scrapling StealthyFetcher 需要）
.venv/bin/scrapling install --force
```

```python
# 在 CPBL skill venv 中執行
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    "https://twbsball.dils.tku.edu.tw/wiki/index.php?title=中華職棒年度最有價值球員",
    headless=True,
    wait=10000,  # 等 Anubis PoW 挑戰完成
)
text = page.css("#mw-content-text")[0].get_all_text()
print(text)
```

多頁面查詢用 `StealthySession` 複用 browser：
```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True) as session:
    page1 = session.fetch("https://twbsball.dils.tku.edu.tw/wiki/index.php?title=中華職棒年度最有價值球員")
    text1 = page1.css("#mw-content-text")[0].get_all_text()
```

## 授權

僅供學習與個人使用 請遵守 CPBL 官網與資料來源的使用條款
