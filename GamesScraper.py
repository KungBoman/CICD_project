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
    Log("INFO", "Fetching Steam applications list...")

    apps = []
    # TODO: Feature to have a specific applist file to search for

    # Get applist from Steam
    Log("INFO", "Get applist from Steam")
    steam_apps = []
    last_appid = 0
    steam_api_key = get_steam_api_key()

    params = {
        "key": steam_api_key,
        "max_results": 50000,
        "last_appid": last_appid
    }

    # Do request
    response = requests.get(
        url=STEAM_APP_LIST_URL,
        params=params,
        timeout=REQUEST_TIMEOUT)
    if response:
        data = response.json()
        if "response" in data and "apps" in data["response"]:
            batch = [str(x["appid"]) for x in data["response"]["apps"]]
            steam_apps.extend(batch)
        else:
            Log("ERROR", "Steam API")

    Log("INFO", f"Number of apps: {len(steam_apps)}")
    return steam_apps


if __name__ == "__main__":
    Log("INFO", "Starting GamesScraper.py")

    steam_api_key = get_steam_api_key()

    if not steam_api_key:
        Log("ERROR", "Steam API Key is invalid.")
        sys.exit(1)

    dataset = load_json(DEFAULT_DATASET_FILE)

    if not dataset:
        Log("INFO", f"No data found in '{DEFAULT_DATASET_FILE}'. Starting with an empty dataset.")
        dataset = {}
    else:
        Log("INFO", f"Loaded dataset from '{DEFAULT_DATASET_FILE}' with {len(dataset)} entries.")

    start_time = time.time()

    # Begin scraper
    try:
        apps = get_app_list()
    except requests.RequestException as error:
        Log("ERROR", f"Failed to fetch Steam app list: {error}")
        sys.exit(1)

    Log("INFO", f"Found {len(apps)} Steam applications")

    end_time = time.time()
    duration = end_time - start_time

    Log("INFO", f"Data fetching completed in {duration:.2f} seconds.")

    save_json(dataset, DEFAULT_DATASET_FILE)

    Log("INFO", f"Dataset saved to '{DEFAULT_DATASET_FILE}' with {len(dataset)} entries.")
