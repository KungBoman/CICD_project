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

APPLIST_FILE = "applist.json"

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


def get_app_list(steam_api_key):
    Log("INFO", "Fetching Steam application list...")

    applist = []
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

        response_apps = response_data.get("apps", [])

        if not response_apps:
            break

        for app in response_apps:
            applist.append({
                "appid": app["appid"],
                "name": app.get("name", "")
            })

        have_more_results = response_data.get("have_more_results")
        last_appid = response_data.get("last_appid")

        Log(
            "INFO",
            f"Fetched {len(response_apps)} apps "
            f"(total: {len(applist)})" +
            ("..." if have_more_results else "")
        )

        if not have_more_results:
            break

    return applist


if __name__ == "__main__":
    Log("INFO", "Starting fetch_app_list.py")

    steam_api_key = get_steam_api_key()

    if not steam_api_key:
        Log("ERROR", "Steam API Key is invalid.")
        sys.exit(1)

    start_time = time.time()

    try:
        applist = get_app_list(steam_api_key)

    except requests.RequestException as error:
        Log("ERROR", f"Failed to fetch Steam app list: {error}")
        sys.exit(1)

    end_time = time.time()
    duration = end_time - start_time

    Log("INFO", f"Fetched {len(applist)} applications in {duration:.2f} seconds.")

    save_json(applist, APPLIST_FILE)

    Log(
        "INFO",
        f"App list saved to '{APPLIST_FILE}' "
        f"with {len(applist)} entries."
    )
