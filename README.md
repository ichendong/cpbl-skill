# CPBL Skill - 中華職棒資訊查詢 ⚾

查詢中華職棒 CPBL 即時比分 已完賽結果 賽程 戰績 球員數據 新聞與歷史資料

## v1.4.3 重點

- **Box Score 詳細數據**：已結束比賽現在會顯示完整投手與打者成績
  - 投手：局數(IP) 被安打(H) 自責分(ER) 三振(K) 四壞(BB) 被全壘打(HR) 中繼成功(H) 救援成功(SV) 最快球速
  - 打者：打數(AB) 安打(H) 打點(RBI) 全壘打(HR) 得分(R) 盜壘(SB) MVP標記
- **比賽狀態修正**：`getlive` 的 `GameStatus=3` 現在會正確覆蓋 `PresentStatus=2`，比賽不再卡在「比賽中」
- **比賽時長格式**：`032300` → `3h23m` 人類可讀格式
- **救援投手支援**：勝投/敗投/救援成功 全部顯示
- **中繼點/救援點**：投手摘要加入中繼成功(H) 與救援成功(SV) 標記
- **PR #3 合併**：N+1 query 優化、TTL 快取、CSRF token 純 HTTP 優先、平行 detail fetch

## v1.4.2 重點

- **戰績排名修復**：`cpbl_standings.py` 現在可正確解析官方 `/standings/seasonaction` 回傳的四張表
  - 球隊對戰戰績
  - 團隊投球成績
  - 團隊打擊成績
  - 團隊守備成績
- **二軍代碼修正**：二軍查詢改用 `D` 避免沿用錯誤代碼
- **文件同步更新**：清掉舊的「只有表頭 沒資料」描述 避免誤導
- **主流程 smoke test 全過**：standings live schedule games stats 都已重新驗證

## v1.4.0 重點

- **即時局數顯示**：`cpbl_live.py` 現在能正確顯示比賽進行中的「第N局上/下半」
  - 改用 `/box/getlive` 的 `CurtGameDetailJson` + `LiveLogJson` 取得精確局數
  - 舊方案 `/box/gamedata` 無法取得局數（回傳 HTML 空頁）
  - 注意：`GameDetailJson` 回的是第一場的資料而非當前進行中場次，必須用 `CurtGameDetailJson`
- **延賽自動偵測**：API 標記已結束但 0:0 無勝敗投 → 自動判為延賽 🌧️
- **API 延遲修正**：`PresentStatus=1`(未開打) 但已有非零比分 → 修正為比賽中
- 移除 `cpbl_news.py`（功能已被 `web_search` 取代，維護成本不值得）
- 移除 `lxml` 依賴 其餘腳本盡量維持輕量
- CPBL 官網前端正確框架為 **Vue.js**（非 Angular）

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
- 近期新聞 直接用 `web_search` 查 CPBL 官網新聞頁
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
# 近期新聞請用 web_search 搜尋 CPBL 官網
```

## 授權

僅供學習與個人使用 請遵守 CPBL 官網與資料來源的使用條款
