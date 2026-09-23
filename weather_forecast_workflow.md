# AI 創新微課程: Taiwan Real-Time Weather Dashboard Workflow

**副標題:** 從即時氣象觀測資料到互動式天氣監測儀表板 (From real-time AWS observations to an interactive weather monitoring dashboard)
**技術棧 (Tech Stack):** CWA API × JSON × Python × SQLite × Streamlit × Plotly × Folium

---

## 開發流程 (Development Workflow)

### 第一階段：課程準備與資料取得 (Phase 1: Preparation & Data Acquisition)
*   **1. 課程介紹**
    *   課程目標
    *   學習地圖
    *   專案成果展示
*   **2. 台灣的天氣與生活**
    *   氣象的關聯性
    *   天氣對日常生活的影響
    *   資訊取得管道
    *   常見氣象專有名詞
*   **3. 中央氣象署 CWA**
    *   認識 Open Data 平台
    *   註冊帳號
    *   取得 API Key
    *   選擇資料集 → **O-A0003-001（自動氣象站即時觀測）**
*   **4. API 資料取得**
    *   使用 `requests` 模組取得 JSON 資料
    *   了解即時觀測 vs 天氣預報資料的差異
*   **5. JSON 資料結構解析**
    *   巢狀 JSON 解析
    *   找出各測站觀測欄位（氣溫、濕度、風速、氣壓等）

### 第二階段：資料處理與資料庫建立 (Phase 2: Data Processing & Database)
*   **6. 擷取各測站觀測資料**
    *   資料分析與處理
    *   解析巢狀 JSON（GeoInfo、WeatherElement、DailyExtreme）
    *   擷取 20+ 觀測欄位
    *   處理異常值（-99 代表無效資料）
    *   轉換成結構化資料（Pandas DataFrame）
*   **7. 資料處理與預覽**
    *   使用 Pandas 讀取與整理資料
    *   資料型別轉換（safe_float 函數）
*   **8. 建立 SQLite 資料庫**
    *   儲存觀測資料
    *   建立資料庫 (data.db)
    *   建立資料表 (ObservationStations)
    *   寫入觀測資料
*   **9. 資料庫設計**
    *   設計 `ObservationStations` 表格結構 (Schema)
    *   20+ 欄位：位置座標、氣溫、濕度、風速風向、氣壓、UV、降水等
*   **10. 查詢資料驗證**
    *   使用 SQL 檢查與驗證寫入的資料

### 第三階段：互動式網頁應用程式開發 (Phase 3: Web App Development)
*   **11. Streamlit 入門**
    *   快速建立 Web App
    *   安裝環境
    *   自訂 CSS 主題（Dark Premium UI）
*   **12. 從資料庫讀取資料**
    *   在 Streamlit 中使用 SQL 查詢 SQLite 資料
    *   使用 `@st.cache_data` 快取資料
*   **13. KPI 摘要卡片**
    *   顯示總站數、平均氣溫、最高/最低溫站、濕度、降雨站數
*   **14. 測站詳情面板**
    *   側邊欄下拉選單選擇測站
    *   顯示所有即時觀測值
*   **15. 顯示資料表格**
    *   完整觀測資料表格（可排序）

### 第四階段：進階視覺化 (Phase 4: Advanced Visualization)
*   **16. 即時觀測地圖**
    *   Folium CircleMarker 依氣溫著色（藍→紅漸層）
    *   測站 Popup 顯示詳細資料
    *   CartoDB Dark Matter 底圖
*   **17. Plotly 圖表**
    *   溫度分佈直方圖
    *   溫度 vs 濕度散佈圖（色彩編碼）
    *   風玫瑰圖（極座標）
    *   縣市 UV 指數長條圖
    *   縣市氣溫箱型圖
*   **18. 整合 Web App 介面**
    *   完整互動式天氣監測儀表板

### 第五階段：進階功能與部署 (Phase 5: Advanced Features & Deployment)
*   **19. 排版與美化**
    *   Google Fonts (Inter)
    *   Dark Premium UI CSS
    *   響應式欄位布局
*   **20. 程式碼重構與優化**
    *   更好的程式設計
    *   程式碼模組化（fetch_observations、save_to_sqlite）
    *   處理極端值（異常值 -99）
    *   處理防呆與錯誤提示
    *   良好的 Docstring 與註解
*   **21. 專案上傳至 GitHub**
    *   版本管理與備份
    *   建立 Repository
    *   連結 Git/GitHub
    *   Commit & Push

### 第六階段：總結與展望 (Phase 6: Conclusion & Next Steps)
*   **22. 延伸應用與專案**
    *   從即時觀測到更多應用
    *   天氣警報 Line Bot
    *   農業 / 防災應用
    *   排班/物流路線規劃
    *   結合 AI 做異常偵測
*   **23. 總結與重點整理**
    *   你學到了什麼？
    *   回顧: API 資料取得, JSON 資料分析, SQLite 資料庫, Streamlit Web App, Plotly 圖表, Folium 地圖, AI + Coding 開發流程
*   **24. 下一步：繼續探索**
    *   AI × Data = Real World 的無限可能