"""
Notes:
    1. Get a list with app id
    2. For every app get store-data
    3. Filter DLC and other apps that are of no interest
    4. Save result continuously so that if a CI-job that is canceled can continue
    5. Respect rate limits with a delay when repeatedly fetching apps
    6. Maybe dont fetch if already have data, alternatively --force
"""

import os
import json
import sys
import time
import requests

CONFIG_FILE = "env/.cfg"
ENCODING = "utf-8"

DEFAULT_DATASET_FILE = "games_dataset.json"

STEAM_APP_LIST_URL = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

REQUEST_TIMEOUT = 15
REQUEST_DELAY = 1
MAX_RESULTS = 5


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


def load_json(filename) -> dict:
    if not os.path.exists(filename):
        return {}

    with open(filename, "r", encoding=ENCODING) as file:
        return json.load(file)


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

    # TODO: Feature to have a specific applist file to search for

    last_appid = 0
    steam_api_key = get_steam_api_key()
    params = {
        "key": steam_api_key,
        "max_results": MAX_RESULTS,
        "last_appid": last_appid
    }

    response = requests.get(
        url=STEAM_APP_LIST_URL,
        params=params,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    apps = data.get("response", {}).get("apps", [])

    Log("INFO", f"Steam returned {len(apps)} applications.")

    return apps


def get_app_details(appid):
    response = requests.get(
        STEAM_APP_DETAILS_URL,
        params={
            "appids": appid,
            "l": "english"
        },
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    app_data = data.get(str(appid))

    if not app_data:
        return None

    if not app_data.get("success"):
        return None

    return app_data.get("data")


if __name__ == "__main__":
    Log("INFO", "Starting GamesScraper.py")

    steam_api_key = get_steam_api_key()

    if not steam_api_key:
        Log("ERROR", "Steam API Key is invalid.")
        sys.exit(1)

    dataset = load_json(DEFAULT_DATASET_FILE)

    if not dataset:
        Log(
            "INFO",
            f"No data found in '{DEFAULT_DATASET_FILE}'. "
            "Starting with an empty dataset."
        )
        dataset = {}
    else:
        Log(
            "INFO",
            f"Loaded dataset from '{DEFAULT_DATASET_FILE}' "
            f"with {len(dataset)} entries."
        )

    start_time = time.time()

    # Begin scraper
    try:
        apps = get_app_list()
    except requests.RequestException as error:
        Log("ERROR", f"Failed to fetch Steam app list: {error}")
        sys.exit(1)

    Log("INFO", f"Found {len(apps)} Steam applications")

    for index, app in enumerate(apps, start=1):
        appid = str(app["appid"])
        name = app.get("name", "")

        # Already collected
        if appid in dataset:
            continue

        Log(
            "INFO",
            f"[{index}/{len(apps)}] Fetching "
            f"{name} ({appid})"
        )

        try:
            details = get_app_details(appid)

            if not details:
                continue

            # Only keep actual games
            if details.get("type") != "game":
                continue

            dataset[appid] = details

            # Save continuously so CI interruptions don't lose everything
            save_json(dataset, DEFAULT_DATASET_FILE)

        except requests.RequestException as error:
            Log(
                "ERROR",
                f"Failed to fetch app {appid}: {error}"
            )

        except Exception as error:
            Log(
                "ERROR",
                f"Unexpected error for app {appid}: {error}"
            )

        time.sleep(REQUEST_DELAY)

    end_time = time.time()
    duration = end_time - start_time

    Log(
        "INFO",
        f"Data fetching completed in {duration:.2f} seconds."
    )

    save_json(dataset, DEFAULT_DATASET_FILE)

    Log(
        "INFO",
        f"Dataset saved to '{DEFAULT_DATASET_FILE}' "
        f"with {len(dataset)} entries."
    )
