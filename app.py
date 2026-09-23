"""
app.py
Taiwan City-Level Real-Time Weather Dashboard
Powered by CWA O-A0003-001 (aggregated to county level)
"""

import os
import math
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('CWA_API_KEY')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="台灣即時天氣",
    page_icon="🌤️",
    layout="wide",
)

# ── CSS: clean sky-blue light theme ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f0f7ff;
}

/* gradient page header */
.page-header {
    background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 50%, #7dd3fc 100%);
    border-radius: 18px;
    padding: 28px 36px;
    margin-bottom: 20px;
    color: white;
}
.page-header h1 { color: white !important; margin:0; font-size: 2rem; font-weight: 700; }
.page-header p  { color: rgba(255,255,255,0.85); margin: 6px 0 0 0; font-size:0.92rem; }

/* KPI cards */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(14,165,233,0.10);
    border-top: 4px solid #38bdf8;
    height: 100%;
}
.kpi-icon  { font-size: 1.6rem; margin-bottom: 6px; }
.kpi-value { color: #0f172a; font-size: 1.7rem; font-weight: 700; line-height: 1.1; margin:4px 0; }
.kpi-label { color: #64748b; font-size: 0.75rem; font-weight: 600;
             letter-spacing:.04em; text-transform: uppercase; }
.kpi-sub   { color: #94a3b8; font-size: 0.72rem; margin-top: 4px; }

/* City weather cards */
.city-card {
    background: white;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 2px 12px rgba(14,165,233,0.10);
    margin-bottom: 10px;
    border-left: 5px solid #38bdf8;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.city-name  { font-size: 1.05rem; font-weight: 700; color: #0f172a; }
.city-temp  { font-size: 1.9rem; font-weight: 700; color: #0ea5e9; }
.city-meta  { font-size: 0.78rem; color: #64748b; }
.hot   { border-left-color: #f97316; }
.cold  { border-left-color: #6366f1; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #e0f2fe;
    border-right: 1px solid #bae6fd;
}
section[data-testid="stSidebar"] .stSelectbox label { color: #0369a1 !important; font-weight:600; }

/* Section headings */
h2, h3 { color: #0ea5e9 !important; font-weight: 700 !important; }

/* Chart background */
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    if not API_KEY:
        st.error("⚠️ 未設定 CWA_API_KEY，請確認 Vercel 環境變數或 .env 檔案。")
        st.stop()
        
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={API_KEY}&format=JSON"
    requests.packages.urllib3.disable_warnings()
    
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        st.error(f"⚠️ 無法連接氣象署 API: {e}")
        st.stop()

    stations = data.get('records', {}).get('Station', [])
    records = []
    
    for stn in stations:
        geo = stn.get('GeoInfo', {})
        we = stn.get('WeatherElement', {})
        
        # 尋找 WGS84 座標
        lat, lon = None, None
        for coord in geo.get('Coordinates', []):
            if coord.get('CoordinateName') == 'WGS84':
                lat = float(coord.get('StationLatitude', 0) or 0)
                lon = float(coord.get('StationLongitude', 0) or 0)
                break

        def safe_float(val):
            try:
                v = float(val)
                return None if v == -99.0 or v == -99 else v
            except (TypeError, ValueError):
                return None

        records.append({
            'StationId':         stn.get('StationId', ''),
            'StationName':       stn.get('StationName', ''),
            'ObsTime':           stn.get('ObsTime', {}).get('DateTime', ''),
            'County':            geo.get('CountyName', ''),
            'Town':              geo.get('TownName', ''),
            'Latitude':          lat,
            'Longitude':         lon,
            'Altitude':          safe_float(geo.get('StationAltitude')),
            'AirTemperature':    safe_float(we.get('AirTemperature')),
            'RelativeHumidity':  safe_float(we.get('RelativeHumidity')),
            'WindSpeed':         safe_float(we.get('WindSpeed')),
            'WindDirection':     safe_float(we.get('WindDirection')),
            'AirPressure':       safe_float(we.get('AirPressure')),
            'Precipitation':     safe_float(we.get('Now', {}).get('Precipitation')),
            'UVIndex':           safe_float(we.get('UVIndex')),
        })
        
    return pd.DataFrame(records)


def wind_deg_to_label(deg) -> str:
    if deg is None or (isinstance(deg, float) and math.isnan(deg)):
        return "—"
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[int((deg + 11.25) / 22.5) % 16]


COUNTY_COORDS = {
    '臺北市':[25.033,'121.565'], '新北市':[25.012,121.463], '桃園市':[24.994,121.301],
    '臺中市':[24.148,120.674], '臺南市':[23.000,120.227], '高雄市':[22.627,120.301],
    '基隆市':[25.128,121.739], '新竹縣':[24.820,121.032], '新竹市':[24.814,120.967],
    '苗栗縣':[24.568,120.823], '彰化縣':[24.052,120.539], '南投縣':[23.903,120.690],
    '雲林縣':[23.709,120.431], '嘉義縣':[23.452,120.255], '嘉義市':[23.480,120.449],
    '屏東縣':[22.673,120.485], '宜蘭縣':[24.732,121.762], '花蓮縣':[23.987,121.602],
    '臺東縣':[22.758,121.144], '澎湖縣':[23.571,119.579], '金門縣':[24.433,118.323],
    '連江縣':[26.151,119.933],
}


# ── Load & aggregate ───────────────────────────────────────────────────────────
try:
    raw = load_data()
except Exception as e:
    st.error(f"⚠️ 資料載入失敗: {e}")
    st.stop()

raw = raw.dropna(subset=['County'])

city_df = raw.groupby('County', as_index=False).agg(
    Stations=('StationId','count'),
    AvgTemp=('AirTemperature','mean'),
    MaxTemp=('AirTemperature','max'),
    MinTemp=('AirTemperature','min'),
    AvgHumidity=('RelativeHumidity','mean'),
    AvgWindSpeed=('WindSpeed','mean'),
    AvgPressure=('AirPressure','mean'),
    AvgUV=('UVIndex','mean'),
    TotalRain=('Precipitation','sum'),
    AvgWindDir=('WindDirection','mean'),
).round(1)


# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🌤️ 台灣即時天氣")
st.sidebar.markdown("---")

obs_time = raw['ObsTime'].iloc[0][:16] if len(raw) else "N/A"
st.sidebar.caption(f"🕐 觀測時間：{obs_time}")
st.sidebar.caption(f"📡 資料來源：CWA O-A0003-001")

st.sidebar.markdown("---")
counties_list = sorted(city_df['County'].tolist())
selected_county = st.sidebar.selectbox("🔍 選擇縣市", ["全台灣"] + counties_list)

if selected_county != "全台灣":
    focus_df = city_df[city_df['County'] == selected_county]
else:
    focus_df = city_df


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
  <h1>🌤️ 台灣即時天氣儀表板</h1>
  <p>即時天氣觀測 · {selected_county} · {obs_time} · 資料來源：中央氣象署 Open Data</p>
</div>
""", unsafe_allow_html=True)


# ── KPI row ───────────────────────────────────────────────────────────────────
valid_temp = focus_df['AvgTemp'].dropna()
avg_tw  = valid_temp.mean()
hot_row = city_df.loc[city_df['MaxTemp'].idxmax()] if not city_df['MaxTemp'].dropna().empty else None
cold_row= city_df.loc[city_df['MinTemp'].idxmin()] if not city_df['MinTemp'].dropna().empty else None
avg_hum = focus_df['AvgHumidity'].dropna().mean()
avg_uv  = focus_df['AvgUV'].dropna().mean()
rain_cnt= (focus_df['TotalRain'].fillna(0) > 0).sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)

def kpi(col, icon, value, label, sub=""):
    col.markdown(f"""<div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {"<div class='kpi-sub'>"+sub+"</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

kpi(k1, "🏙️", len(focus_df), "縣市數量", f"共 {len(city_df)} 個縣市")
kpi(k2, "🌡️", f"{avg_tw:.1f}°C", "平均氣溫", selected_county)
kpi(k3, "🔴", f"{hot_row['MaxTemp']:.1f}°C" if hot_row is not None else "—", "最高氣溫", hot_row['County'] if hot_row is not None else "")
kpi(k4, "🔵", f"{cold_row['MinTemp']:.1f}°C" if cold_row is not None else "—", "最低氣溫", cold_row['County'] if cold_row is not None else "")
kpi(k5, "💧", f"{avg_hum:.0f}%", "平均濕度", "相對濕度")
kpi(k6, "☔", f"{rain_cnt}", "有雨縣市", "有降水紀錄")

st.markdown("<br>", unsafe_allow_html=True)


# ── Map (full width) ─────────────────────────────────────────────────────────
st.markdown("### 🗺️ 台灣天氣地圖")

m = folium.Map(
    location=[23.7, 121.0],
    zoom_start=7,
    tiles="OpenStreetMap",
)

temp_vals = city_df['AvgTemp'].dropna()
t_min, t_max = temp_vals.min(), temp_vals.max()

for _, row in city_df.iterrows():
    if row['County'] not in COUNTY_COORDS:
        continue
    lat, lon = COUNTY_COORDS[row['County']]

    # blue → orange color scale
    if pd.notna(row['AvgTemp']) and t_max > t_min:
        ratio = (row['AvgTemp'] - t_min) / (t_max - t_min)
        r = int(30  + ratio * 225)
        g = int(144 - ratio * 80)
        b = int(255 - ratio * 230)
        color = f"#{r:02x}{g:02x}{b:02x}"
    else:
        color = "#94a3b8"

    is_selected = (selected_county == row['County'])
    popup_html = (
        f"<b style='font-size:14px'>{row['County']}</b><br>"
        f"🌡 平均氣溫：<b>{row['AvgTemp']:.1f}°C</b> "
        f"（最高 {row['MaxTemp']:.1f} / 最低 {row['MinTemp']:.1f}）<br>"
        f"💧 相對濕度：{row['AvgHumidity']:.0f}%<br>"
        f"🌬 風速：{row['AvgWindSpeed']:.1f} m/s {wind_deg_to_label(row['AvgWindDir'])}<br>"
        f"☀️ 紫外線：{row['AvgUV']:.0f} &nbsp; ☔ 降水：{row['TotalRain']:.1f}mm"
    )
    folium.CircleMarker(
        location=[lat, lon],
        radius=18 if is_selected else 14,
        color='white',
        weight=2 if is_selected else 1,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"{row['County']}: {row['AvgTemp']:.1f}°C",
    ).add_to(m)

    folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(
            html=f"<div style='font-size:10px;font-weight:700;color:white;"
                 f"text-align:center;line-height:1;margin-top:4px;text-shadow:0 0 3px #000'>"
                 f"{row['AvgTemp']:.0f}°</div>",
            icon_size=(36, 20),
            icon_anchor=(18, 10),
        ),
    ).add_to(m)

st_folium(m, width=None, height=480)


# ── City Cards – 3-column CSS grid ────────────────────────────────────────────
st.markdown("### 🏙️ 各縣市天氣一覽")
sorted_cities = focus_df.sort_values('AvgTemp', ascending=False)
max_t = sorted_cities['AvgTemp'].max()
min_t = sorted_cities['AvgTemp'].min()

cards_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">'
for _, row in sorted_cities.iterrows():
    extra_cls = "hot" if row['AvgTemp'] == max_t else ("cold" if row['AvgTemp'] == min_t else "")
    rain_txt = f"☔ 降水 {row['TotalRain']:.1f}mm" if row['TotalRain'] > 0 else "無降水"
    wind_lbl = wind_deg_to_label(row['AvgWindDir'])
    cards_html += f"""<div class="city-card {extra_cls}">
      <div class="city-name">{row['County']}</div>
      <div class="city-temp">{row['AvgTemp']:.1f}°C</div>
      <div class="city-meta">
        💧 {row['AvgHumidity']:.0f}% &nbsp;·&nbsp; 🌬️ {row['AvgWindSpeed']:.1f} m/s {wind_lbl}
        &nbsp;·&nbsp; {rain_txt} &nbsp;·&nbsp; UV {row['AvgUV']:.0f}
      </div>
    </div>"""
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)


st.markdown("---")


# ── Charts ────────────────────────────────────────────────────────────────────
st.markdown("### 📊 氣象數據分析")

PLOTLY_LAYOUT = dict(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_color='#334155',
    font_family='Inter',
)

ca1, ca2 = st.columns(2)

with ca1:
    bar_df = focus_df.sort_values('AvgTemp', ascending=True)
    fig_bar = px.bar(
        bar_df, x='AvgTemp', y='County', orientation='h',
        color='AvgTemp', color_continuous_scale='RdYlBu_r',
        title="各縣市平均氣溫（°C）",
        labels={'AvgTemp': '平均氣溫（°C）', 'County': ''},
        template='plotly_white',
    )
    fig_bar.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                          title_font_size=14)
    st.plotly_chart(fig_bar, use_container_width=True)

with ca2:
    scatter_df = focus_df.dropna(subset=['AvgTemp','AvgHumidity'])
    fig_sc = px.scatter(
        scatter_df, x='AvgTemp', y='AvgHumidity',
        size='Stations', color='AvgTemp',
        color_continuous_scale='RdYlBu_r',
        hover_name='County',
        hover_data={'AvgWindSpeed': True, 'AvgUV': True, 'Stations': True},
        title="氣溫與相對濕度關係",
        labels={'AvgTemp': '平均氣溫（°C）', 'AvgHumidity': '平均濕度（%）'},
        template='plotly_white',
    )
    fig_sc.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, title_font_size=14)
    st.plotly_chart(fig_sc, use_container_width=True)


ca3, ca4 = st.columns(2)

with ca3:
    wind_df = focus_df.dropna(subset=['AvgWindDir','AvgWindSpeed']).copy()
    wind_df['WindDirLabel'] = wind_df['AvgWindDir'].apply(wind_deg_to_label)
    dir_order = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
                 "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    wind_agg = wind_df.groupby('WindDirLabel')['AvgWindSpeed'].mean().reset_index()
    wind_agg['order'] = wind_agg['WindDirLabel'].apply(
        lambda d: dir_order.index(d) if d in dir_order else 99)
    wind_agg = wind_agg.sort_values('order')

    fig_wind = go.Figure(go.Barpolar(
        r=wind_agg['AvgWindSpeed'],
        theta=wind_agg['WindDirLabel'],
        marker_color=wind_agg['AvgWindSpeed'],
        marker_colorscale='Blues',
        opacity=0.85,
    ))
    fig_wind.update_layout(
        title="風玫瑰圖（各風向平均風速）",
        title_font_size=14,
        paper_bgcolor='white',
        polar=dict(bgcolor='#f8fafc',
                   angularaxis=dict(tickfont_size=10),
                   radialaxis=dict(tickfont_size=9)),
        font=dict(family='Inter', color='#334155'),
    )
    st.plotly_chart(fig_wind, use_container_width=True)

with ca4:
    uv_df = focus_df.dropna(subset=['AvgUV']).sort_values('AvgUV', ascending=False)
    fig_uv = px.bar(
        uv_df, x='County', y='AvgUV',
        color='AvgUV', color_continuous_scale='YlOrRd',
        title="各縣市平均紫外線指數",
        labels={'County': '', 'AvgUV': '紫外線指數'},
        template='plotly_white',
    )
    fig_uv.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False,
                          xaxis_tickangle=-35, title_font_size=14)
    st.plotly_chart(fig_uv, use_container_width=True)


# ── Summary table ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 各縣市數據總覽")

display = focus_df[['County','AvgTemp','MaxTemp','MinTemp','AvgHumidity',
                     'AvgWindSpeed','AvgPressure','AvgUV','TotalRain','Stations']].copy()
display.columns = ['縣市','平均氣溫°C','最高°C','最低°C','濕度%',
                   '風速m/s','氣壓hPa','紫外線','降水mm','測站數']
st.dataframe(
    display.sort_values('平均氣溫°C', ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=420,
)

st.markdown("---")
st.caption("資料來源：中央氣象署 Open Data · O-A0003-001 · 自動氣象站即時觀測 · 以縣市彙整")
