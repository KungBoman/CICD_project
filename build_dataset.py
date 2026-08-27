"""
build a dataset
"""

import common_util as cu

import time
import datetime
import requests
import argparse

ENCODING = "utf-8"
DATASET_FILE = "games_dataset.json"

# Documentation: https://github-wiki-see.page/m/Revadike/InternalSteamWebAPI/wiki/
# Get-App-Details?utm_source=chatgpt.com
STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0

DEFAULT_COUNTRY_CODE = "se"
DEFAULT_LANGUAGE = "en"


def print_progress(current, total, name="", width=20):
    progress = current / total
    filled = int(width * progress)

    bar = "█" * filled + "░" * (width - filled)

    print(
        f"\r\033[K"  # erase line
        f"\r{datetime.datetime.now().strftime('%H:%M:%S')} "
        f"{bar} "
        f"{current}/{total} "
        f"({progress * 100:6.2f}%) "
        f"{name[:50]}",
        end="",
        flush=True
    )


def get_app_details(appid, country=DEFAULT_COUNTRY_CODE, language=DEFAULT_LANGUAGE, filters=None):
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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch Steam application list."
    )

    parser.add_argument(
        "-ma", "--max-apps", type=int, default=None,
        help="Maximum number of apps to fetch. "
             "If omitted, fetch all apps."
    )

    parser.add_argument(
        "-c", "--country", type=str, default=DEFAULT_COUNTRY_CODE,
        help="-Country code"
    )

    parser.add_argument(
        "-l", "--language", type=str, default=DEFAULT_LANGUAGE,
        help="Language code"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    cu.log("INFO", "Starting GamesScraper.py")

    dataset = cu.load_json(DATASET_FILE)

    if not dataset:
        cu.log(
            "INFO",
            f"No data found in '{DATASET_FILE}'. "
            "Starting with an empty dataset."
        )
        dataset = {}
    else:
        cu.log(
            "INFO",
            f"Loaded dataset from '{DATASET_FILE}' "
            f"with {len(dataset)} entries."
        )

    start_time = time.time()

    raw_app_list = cu.load_json("app_list.json")

    if args.max_apps is not None:
        app_list = raw_app_list[:args.max_apps]
        cu.log(
            "INFO",
            f"Limiting app_list to {len(app_list)} apps "
            f"for this run."
        )
    else:
        app_list = raw_app_list

    skip_already_collected = False

    # Begin scraper
    cu.log(
        "INFO",
        f"Fetching details for {len(app_list)} applications... "
        "(CTRL+C to exit)"
    )
    for index, app in enumerate(app_list, start=1):
        appid = str(app["appid"])
        name = app.get("name", "")

        if skip_already_collected and appid in dataset:
            continue

        print_progress(
            index - 1,
            len(app_list),
            f"{name} ({appid})"
        )

        try:
            details = get_app_details(appid, args.country, args.language)

            if not details:
                continue

            # Only keep actual games
            if details.get("type") != "game":
                continue

            game = extract_game_data(details)

            dataset[appid] = game

            # Save continuously so CI interruptions don't lose everything
            cu.save_json(dataset, DATASET_FILE)

        except requests.RequestException as error:
            cu.log(
                "ERROR",
                f"Failed to fetch app {appid}: {error}"
            )

        except Exception as error:
            cu.log(
                "ERROR",
                f"Unexpected error for app {appid}: {error}"
            )

        time.sleep(REQUEST_DELAY)

    end_time = time.time()
    duration = end_time - start_time

    print_progress(
        index,
        len(app_list),
        ""
    )
    print()  # new line
    cu.log(
        "INFO",
        f"Data fetching completed in {duration:.2f} seconds."
    )

    cu.save_json(dataset, DATASET_FILE)

    cu.log(
        "INFO",
        f"Dataset saved to '{DATASET_FILE}' "
        f"with {len(dataset)} entries."
    )
