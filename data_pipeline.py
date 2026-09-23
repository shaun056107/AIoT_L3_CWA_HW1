"""
data_pipeline.py
Fetches real-time weather station observations from CWA (O-A0003-001)
and stores them in a local SQLite database (data.db).

API: O-A0003-001 - Automatic weather station (AWS) observations
"""

import os
import sqlite3
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('CWA_API_KEY')

API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"


def fetch_observations() -> list[dict]:
    """
    Fetch all real-time station observations from CWA API.
    Returns a list of flattened dictionaries ready for DataFrame creation.
    """
    requests.packages.urllib3.disable_warnings()
    params = {
        "Authorization": API_KEY,
        "format": "JSON",
    }
    print("Fetching data from CWA API (O-A0003-001)...")
    response = requests.get(API_URL, params=params, verify=False)

    if response.status_code != 200:
        print(f"API Error {response.status_code}: {response.text[:300]}")
        return []

    data = response.json()
    stations = data.get('records', {}).get('Station', [])
    print(f"  -> Received {len(stations)} stations.")

    records = []
    for stn in stations:
        geo = stn.get('GeoInfo', {})
        we = stn.get('WeatherElement', {})
        daily = we.get('DailyExtreme', {})
        gust = we.get('GustInfo', {})

        # Extract WGS84 latitude/longitude
        lat, lon = None, None
        for coord in geo.get('Coordinates', []):
            if coord.get('CoordinateName') == 'WGS84':
                lat = float(coord.get('StationLatitude', 0) or 0)
                lon = float(coord.get('StationLongitude', 0) or 0)
                break

        def safe_float(val):
            """Safely convert to float, return None if invalid."""
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
            'Weather':           we.get('Weather', ''),
            'AirTemperature':    safe_float(we.get('AirTemperature')),
            'RelativeHumidity':  safe_float(we.get('RelativeHumidity')),
            'WindSpeed':         safe_float(we.get('WindSpeed')),
            'WindDirection':     safe_float(we.get('WindDirection')),
            'AirPressure':       safe_float(we.get('AirPressure')),
            'Precipitation':     safe_float(we.get('Now', {}).get('Precipitation')),
            'UVIndex':           safe_float(we.get('UVIndex')),
            'GustSpeed':         safe_float(gust.get('PeakGustSpeed')),
            'SunshineDuration':  safe_float(we.get('SunshineDuration')),
            'DailyHighTemp':     safe_float(
                daily.get('DailyHigh', {}).get('TemperatureInfo', {}).get('AirTemperature')
            ),
            'DailyHighTime':     daily.get('DailyHigh', {}).get('TemperatureInfo', {})
                                      .get('Occurred_at', {}).get('DateTime', ''),
            'DailyLowTemp':      safe_float(
                daily.get('DailyLow', {}).get('TemperatureInfo', {}).get('AirTemperature')
            ),
            'DailyLowTime':      daily.get('DailyLow', {}).get('TemperatureInfo', {})
                                      .get('Occurred_at', {}).get('DateTime', ''),
        })

    return records


def save_to_sqlite(records: list[dict]) -> None:
    """Persist the observation records to data.db (ObservationStations table)."""
    df = pd.DataFrame(records)
    conn = sqlite3.connect('data.db')
    df.to_sql('ObservationStations', conn, if_exists='replace', index=False)
    conn.close()
    print(f"  -> Saved {len(df)} records to data.db (ObservationStations).")


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: CWA_API_KEY not found in .env")
        exit(1)

    records = fetch_observations()
    if records:
        save_to_sqlite(records)
        df = pd.DataFrame(records)
        print("\nSample data:")
        print(df[['StationName', 'County', 'AirTemperature', 'RelativeHumidity',
                   'WindSpeed', 'AirPressure', 'UVIndex']].head(10).to_string())
        print(f"\nTotal valid stations: {len(df)}")
        print(f"Temperature range: {df['AirTemperature'].min():.1f}°C – {df['AirTemperature'].max():.1f}°C")
    else:
        print("No data received.")
