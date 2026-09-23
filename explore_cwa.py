import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CWA_API_KEY = os.getenv("CWA_API_KEY")
if not CWA_API_KEY:
    print("API KEY IS MISSING")
    exit(1)

# try F-C0032-005 for 1-week forecast as requested
url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={CWA_API_KEY}&format=JSON"

requests.packages.urllib3.disable_warnings()
response = requests.get(url, verify=False)
if response.status_code == 200:
    data = response.json()
    with open("cwa_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved response to cwa_response.json")
    # print some basic info
    if "records" in data and "location" in data["records"]:
        print("Success! Number of locations:", len(data["records"]["location"]))
        # look for weather elements in the first location
        loc0 = data["records"]["location"][0]
        print("Location 0:", loc0["locationName"])
        for we in loc0["weatherElement"]:
            print("  Element:", we["elementName"])
else:
    print("Error HTTP:", response.status_code)
    print(response.text)
