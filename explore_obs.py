import os
import requests
import json

API_KEY = "CWA-BAAEAF7F-E786-4219-A518-EA08F4201EFB"

requests.packages.urllib3.disable_warnings()
url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={API_KEY}&format=JSON&limit=5"
response = requests.get(url, verify=False)
print("Status:", response.status_code)
if response.status_code == 200:
    data = response.json()
    with open("cwa_obs_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to cwa_obs_response.json")
    # show top-level structure
    records = data.get('records', {})
    print("Records keys:", list(records.keys()))
    stations = records.get('Station', records.get('station', []))
    if stations:
        print("Number of stations:", len(stations))
        print("First station keys:", list(stations[0].keys()))
        print("First station:", json.dumps(stations[0], ensure_ascii=False, indent=2))
else:
    print("Error:", response.text[:500])
