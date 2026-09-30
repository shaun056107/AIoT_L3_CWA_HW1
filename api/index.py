"""
api/index.py
Flask backend for the Taiwan Real-Time Weather Dashboard.
Runs as a Vercel Python Serverless Function.
"""

import os
import json
import math
import urllib.request
import ssl
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="../templates")

API_KEY = os.getenv("CWA_API_KEY", "CWA-BAAEAF7F-E786-4219-A518-EA08F4201EFB")

COUNTY_COORDS = {
    "臺北市": [25.033, 121.565],
    "新北市": [25.012, 121.463],
    "桃園市": [24.994, 121.301],
    "臺中市": [24.148, 120.674],
    "臺南市": [23.000, 120.227],
    "高雄市": [22.627, 120.301],
    "基隆市": [25.128, 121.739],
    "新竹縣": [24.820, 121.032],
    "新竹市": [24.814, 120.967],
    "苗栗縣": [24.568, 120.823],
    "彰化縣": [24.052, 120.539],
    "南投縣": [23.903, 120.690],
    "雲林縣": [23.709, 120.431],
    "嘉義縣": [23.452, 120.255],
    "嘉義市": [23.480, 120.449],
    "屏東縣": [22.673, 120.485],
    "宜蘭縣": [24.732, 121.762],
    "花蓮縣": [23.987, 121.602],
    "臺東縣": [22.758, 121.144],
    "澎湖縣": [23.571, 119.579],
    "金門縣": [24.433, 118.323],
    "連江縣": [26.151, 119.933],
}

DIR_LABELS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]


def wind_deg_to_label(deg):
    if deg is None or (isinstance(deg, float) and math.isnan(deg)):
        return "—"
    return DIR_LABELS[int((deg + 11.25) / 22.5) % 16]


def parse_val(v):
    try:
        val = float(v)
        return None if val < -90 else val
    except Exception:
        return None


def fetch_stations():
    url = (
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
        f"?Authorization={API_KEY}&format=JSON"
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("records", {}).get("Station", [])


def aggregate_by_county(stations):
    buckets = {}
    obs_time = None

    for s in stations:
        try:
            county = s.get("GeoInfo", {}).get("CountyName")
            if not county:
                continue

            if obs_time is None:
                obs_time = s.get("ObsTime", {}).get("DateTime", "")

            weath = s.get("WeatherElement", {})
            temp = parse_val(weath.get("AirTemperature"))
            hum = parse_val(weath.get("RelativeHumidity"))
            wind_speed = parse_val(weath.get("WindSpeed"))
            pressure = parse_val(weath.get("AirPressure"))
            uv = parse_val(weath.get("UVIndex"))
            wind_dir = parse_val(weath.get("WindDirection"))

            now_p = weath.get("Now", {})
            if isinstance(now_p, dict) and "Precipitation" in now_p:
                precip = parse_val(now_p.get("Precipitation")) or 0.0
            else:
                precip = parse_val(weath.get("Precipitation")) or 0.0

            sid = s.get("StationId", "")

            if county not in buckets:
                buckets[county] = {
                    "County": county,
                    "stations": [],
                    "temps": [],
                    "hums": [],
                    "winds": [],
                    "pressures": [],
                    "uvs": [],
                    "precips": [],
                    "wind_dirs": [],
                }

            b = buckets[county]
            b["stations"].append(sid)
            if temp is not None:
                b["temps"].append(temp)
            if hum is not None:
                b["hums"].append(hum)
            if wind_speed is not None:
                b["winds"].append(wind_speed)
            if pressure is not None:
                b["pressures"].append(pressure)
            if uv is not None:
                b["uvs"].append(uv)
            b["precips"].append(precip)
            if wind_dir is not None:
                b["wind_dirs"].append(wind_dir)

        except Exception:
            continue

    def safe_avg(lst):
        return round(sum(lst) / len(lst), 1) if lst else None

    result = []
    for county, b in buckets.items():
        temps = b["temps"]
        avg_wind_dir = safe_avg(b["wind_dirs"])
        entry = {
            "County": county,
            "Stations": len(b["stations"]),
            "AvgTemp": safe_avg(temps),
            "MaxTemp": round(max(temps), 1) if temps else None,
            "MinTemp": round(min(temps), 1) if temps else None,
            "AvgHumidity": safe_avg(b["hums"]),
            "AvgWindSpeed": safe_avg(b["winds"]),
            "AvgPressure": safe_avg(b["pressures"]),
            "AvgUV": safe_avg(b["uvs"]),
            "TotalRain": round(sum(b["precips"]), 1),
            "AvgWindDir": avg_wind_dir,
            "WindDirLabel": wind_deg_to_label(avg_wind_dir),
            "Lat": COUNTY_COORDS.get(county, [None, None])[0],
            "Lon": COUNTY_COORDS.get(county, [None, None])[1],
        }
        result.append(entry)

    result.sort(key=lambda x: x["County"])
    return result, (obs_time[:16] if obs_time else "N/A")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def weather():
    try:
        stations = fetch_stations()
        counties, obs_time = aggregate_by_county(stations)
        return jsonify({"obs_time": obs_time, "counties": counties})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Vercel entry point
handler = app
