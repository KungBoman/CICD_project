"""
example output
[
    {
        "appid": 10,
        "name": "Counter-Strike"
    },
    {
        "appid": 20,
        "name": "Team Fortress Classic"
    },
    {
        "appid": 30,
        "name": "Day of Defeat"
    }
]
"""

import os
import json
import sys
import time
import requests

CONFIG_FILE = "env/.cfg"
ENCODING = "utf-8"

APP_LIST_FILE = "applist.json"

STEAM_APP_LIST_URL = "https://api.steampowered.com/IStoreService/GetAppList/v1/"

REQUEST_TIMEOUT = 15
MAX_RESULTS = 50000


def Log(type, msg):
    print(f"[{type}] {msg}")


def get_steam_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding=ENCODING) as file:
            for line in file:
                line = line.strip()

                if line.startswith("STEAM_API_KEY="):
                    return line.split("=", 1)[1]

    Log("ERROR", f"Configuration file '{CONFIG_FILE}' not found.")
    sys.exit(1)


def save_json(data, filename):
    with open(filename, "w", encoding=ENCODING) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_app_list():
    Log("INFO", "Fetching Steam application list...")

    steam_api_key = get_steam_api_key()
    apps = []
    last_appid = 0

    while True:
        params = {
            "key": steam_api_key,
            "max_results": MAX_RESULTS,
            "last_appid": last_appid
        }

        response = requests.get(
            STEAM_APP_LIST_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()
        response_data = data.get("response", {})

        page = response_data.get("apps", [])

        if not page:
            break

        for app in page:
            apps.append({
                "appid": app["appid"],
                "name": app.get("name", "")
            })

        Log(
            "INFO",
            f"Fetched {len(page)} apps "
            f"(total: {len(apps)})..."
        )

        last_appid = response_data.get("last_appid")

        if not last_appid:
            break

    return apps


if __name__ == "__main__":
    Log("INFO", "Starting fetch_app_list.py")

    start_time = time.time()

    try:
        apps = get_app_list()

    except requests.RequestException as error:
        Log("ERROR", f"Failed to fetch Steam app list: {error}")
        sys.exit(1)

    end_time = time.time()
    duration = end_time - start_time

    Log("INFO", f"Fetched {len(apps)} applications in {duration:.2f} seconds..")

    save_json(apps, APP_LIST_FILE)

    Log(
        "INFO",
        f"App list saved to '{APP_LIST_FILE}' "
        f"with {len(apps)} entries."
    )
