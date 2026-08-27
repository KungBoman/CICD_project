"""
"""

import os
import json
import sys
import time
import datetime
import requests

CONFIG_FILE = "env/.cfg"
ENCODING = "utf-8"

DATASET_FILE = "games_dataset.json"

# Documentation: https://github-wiki-see.page/m/Revadike/InternalSteamWebAPI/wiki/Get-App-Details?utm_source=chatgpt.com
STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0


def Log(type, msg):
    print(f"[{type}] {msg}")


def print_progress(current, total, name="", width=40):
    progress = current / total
    filled = int(width * progress)

    bar = "█" * filled + "░" * (width - filled)

    print(
        f"\r{datetime.datetime.now().strftime('%H:%M:%S')} "
        f"{bar} "
        f"{current}/{total} "
        f"({progress * 100:6.2f}%) "
        f"{name[:50]}",
        end="",
        flush=True
    )


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


def get_app_details(appid, country="SE", language="english", filters=None):
    params = {
        "appids": appid,
        "cc": country,
        "l": language
    }

    if filters:
        params["filters"] = filters

    response = requests.get(
        STEAM_APP_DETAILS_URL,
        params=params,
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


def extract_game_data(details):
    return {
        "appid": details.get("steam_appid"),
        "name": details.get("name"),
        "is_free": details.get("is_free"),
        "price": details.get("price_overview", {}).get("final") / 100,
        "currency": details.get("price_overview", {}).get("currency"),
        "about_the_game": details.get("about_the_game"),
        "windows": details.get("platforms", {}).get("windows"),
        "mac": details.get("platforms", {}).get("mac"),
        "linux": details.get("platforms", {}).get("linux"),
        "metacritic_score": details.get("metacritic", {}).get("score"),
        "metacritic_url": details.get("metacritic", {}).get("url"),
    }


if __name__ == "__main__":
    Log("INFO", "Starting GamesScraper.py")

    dataset = load_json(DATASET_FILE)

    if not dataset:
        Log(
            "INFO",
            f"No data found in '{DATASET_FILE}'. "
            "Starting with an empty dataset."
        )
        dataset = {}
    else:
        Log(
            "INFO",
            f"Loaded dataset from '{DATASET_FILE}' "
            f"with {len(dataset)} entries."
        )

    start_time = time.time()

    applist = load_json("applist.json")

    Log("INFO", f"Found {len(applist)} Steam applications.")

    skip_already_collected = False

    # Begin scraper
    Log("INFO", "Fetching details... (CTRL+C to exit)")
    for index, app in enumerate(applist, start=1):
        appid = str(app["appid"])
        name = app.get("name", "")

        if skip_already_collected and appid in dataset:
            continue

        print_progress(
            index,
            len(applist),
            f"{name} ({appid})"
        )

        try:
            details = get_app_details(appid)

            if not details:
                continue

            # Only keep actual games
            if details.get("type") != "game":
                continue

            game = extract_game_data(details)

            dataset[appid] = game

            # Save continuously so CI interruptions don't lose everything
            save_json(dataset, DATASET_FILE)

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

    save_json(dataset, DATASET_FILE)

    Log(
        "INFO",
        f"Dataset saved to '{DATASET_FILE}' "
        f"with {len(dataset)} entries."
    )
