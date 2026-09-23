# AIoT_L3_CWA_HW1 - Taiwan Real-Time Weather Dashboard

從中央氣象署自動氣象站即時觀測資料，建立互動式天氣監測儀表板，使用 **CWA API × JSON × Python × SQLite × Streamlit × Plotly × Folium**。

> AI 創新微課程：Taiwan Weather Dashboard  
> 從即時觀測資料到互動式天氣監測儀表板

---

## 📌 專案簡介

本專案透過中央氣象署（CWA）開放資料平台的 **`O-A0003-001`** 資料集（全台自動氣象站即時觀測），完成：

1. 即時 API 資料取得（Real-time Observation API）
2. JSON 資料解析與清理
3. 多欄位測站資料結構化處理
4. SQLite 資料庫儲存（`ObservationStations` 資料表）
5. Streamlit Web App 建立
6. KPI 摘要卡片（總站數、平均氣溫、最高/最低溫站）
7. 互動式地圖（依氣溫著色的測站標記）
8. 多種 Plotly 圖表（溫度直方圖、溫溼度散佈圖、風玫瑰圖、UV 指數圖、縣市箱型圖）
9. 完整觀測資料表格

最終建立一個可互動的 **Taiwan Real-Time Weather Dashboard**。

---

## 🎯 學習目標

完成本專案後，可以掌握：

- Python 基礎資料處理與錯誤處理
- REST API 使用方式（即時觀測 vs 天氣預報）
- JSON 巢狀結構解析
- CWA Open Data API（O-A0003-001）
- Pandas 資料分析與清理（包含異常值處理）
- SQLite 資料庫設計與操作
- SQL 查詢
- Streamlit Web App 與自訂 CSS 主題
- Plotly 互動式圖表（直方圖、散佈圖、極座標圖、箱型圖）
- Folium 地圖視覺化（依數值著色的圓形標記）
- Git / GitHub 專案管理
- 將資料分析流程整合成完整應用程式

---

## 🏗️ 系統架構

```text
┌─────────────────────┐
│  Central Weather    │
│  Administration     │
│  O-A0003-001        │
│  (AWS Real-time)    │
└──────────┬──────────┘
           │
           │ HTTP GET (JSON)
           ▼
┌─────────────────────┐
│    data_pipeline.py │
│  requests + pandas  │
│  Parse / Clean AWS  │
│  observation data   │
└──────────┬──────────┘
           │
           │ to_sql()
           ▼
┌─────────────────────┐
│       SQLite        │
│  ObservationStations│
│  (20+ fields/station│
└──────────┬──────────┘
           │
           │ SQL Query
           ▼
┌─────────────────────┐
│     app.py          │
│  Streamlit + Plotly │
│  + Folium Dashboard │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  KPI Cards          │
│  Station Detail     │
│  Temp-colored Map   │
│  Charts & Tables    │
└─────────────────────┘
```

---

## 📂 專案結構

```
AIoT_L3_CWA_HW1/
├── .env                    # CWA API Key (不上傳 GitHub)
├── .gitignore
├── requirements.txt        # Python 依賴套件
├── data_pipeline.py        # 資料擷取與儲存腳本
├── app.py                  # Streamlit 儀表板主程式
├── data.db                 # SQLite 資料庫 (執行後產生)
└── README.md
```

---

## 🗄️ 資料庫結構 (ObservationStations)

| 欄位 | 說明 |
|------|------|
| `StationId` | 測站編號 |
| `StationName` | 測站名稱 |
| `ObsTime` | 觀測時間 |
| `County` | 縣市 |
| `Town` | 鄉鎮 |
| `Latitude` / `Longitude` | WGS84 緯度 / 經度 |
| `Altitude` | 海拔高度 (m) |
| `AirTemperature` | 氣溫 (°C) |
| `RelativeHumidity` | 相對濕度 (%) |
| `WindSpeed` | 風速 (m/s) |
| `WindDirection` | 風向 (度) |
| `AirPressure` | 氣壓 (hPa) |
| `Precipitation` | 降水量 (mm) |
| `UVIndex` | 紫外線指數 |
| `GustSpeed` | 最大陣風 (m/s) |
| `SunshineDuration` | 日照時數 (hr) |
| `DailyHighTemp` | 當日最高氣溫 |
| `DailyLowTemp` | 當日最低氣溫 |
| `Weather` | 天氣現象描述 |

---

## 🚀 如何執行

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 設定 API Key
在 `.env` 檔案中加入：
```
CWA_API_KEY=your_key_here
```

### 3. 執行資料擷取
```bash
python data_pipeline.py
```

### 4. 啟動儀表板
```bash
python -m streamlit run app.py
```

---

## 📊 儀表板功能

| 功能 | 說明 |
|------|------|
| **KPI 卡片** | 測站數、平均氣溫、最高/最低溫站、平均濕度、降雨站數 |
| **測站詳情面板** | 選擇測站後顯示所有即時觀測值 |
| **即時觀測地圖** | Folium 地圖，依氣溫著色（藍=涼→紅=熱） |
| **溫度分佈直方圖** | 各測站氣溫分佈 |
| **溫溼度散佈圖** | 氣溫 vs 相對濕度的相關性分析 |
| **風玫瑰圖** | 各風向的平均風速分佈（極座標圖） |
| **UV 指數圖** | 各縣市平均紫外線指數比較 |
| **縣市氣溫箱型圖** | 各縣市氣溫分佈與極端值 |
| **完整資料表** | 可依欄位排序的所有測站觀測資料 |
