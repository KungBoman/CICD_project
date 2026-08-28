"""
build a dataset
"""

import common_util as cu

import time
import datetime
import requests
import argparse


STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
"""
Documentation:
https://github-wiki-see.page/m/Revadike/InternalSteamWebAPI/wiki/
Get-App-Details?utm_source=chatgpt.com
"""

REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0

DEFAULT_DATASET_FILE = "games_dataset.json"
DEFAULT_COUNTRY_CODE = "se"
DEFAULT_LANGUAGE = "en"
DEFAULT_SKIP_EXISTING = True


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
    game_data = {}

    game_data["appid"] = details.get("steam_appid")
    game_data["name"] = details.get("name")

    is_free = details.get("is_free")
    game_data["is_free"] = is_free

    price_overview = details.get("price_overview", {})

    if is_free:
        game_data["price"] = 0.0
        game_data["currency"] = None
    else:
        game_data["price"] = (
            price_overview.get("final", 0) / 100
            if price_overview
            else 0.0
        )
        game_data["currency"] = price_overview.get("currency")

    game_data["about_the_game"] = details.get("about_the_game")

    platforms = details.get("platforms", {})
    game_data["windows"] = platforms.get("windows")
    game_data["mac"] = platforms.get("mac")
    game_data["linux"] = platforms.get("linux")

    metacritic = details.get("metacritic", {})
    game_data["metacritic_score"] = metacritic.get("score")
    game_data["metacritic_url"] = metacritic.get("url")

    return game_data


def load_dataset(file=DEFAULT_DATASET_FILE):
    dataset = cu.load_json(file)

    if not dataset:
        cu.log(
            "INFO",
            f"No data found in '{file}'. "
            "Starting with an empty dataset."
        )
        dataset = {}
    else:
        cu.log(
            "INFO",
            f"Loaded dataset from '{file}' "
            f"with {len(dataset)} entries."
        )

    return dataset


def load_app_list(max_apps=None):
    app_list = cu.load_json("app_list.json")

    if max_apps is not None:
        app_list = app_list[:max_apps]
        cu.log(
            "INFO",
            f"Limiting app_list to {len(app_list)} apps for this run."
        )

    return app_list


def process_app(app, dataset, country=DEFAULT_COUNTRY_CODE, language=DEFAULT_LANGUAGE):
    appid = str(app["appid"])
    name = app.get("name", "")

    try:
        details = get_app_details(
            appid,
            country,
            language
        )

        if not details:
            return

        if details.get("type") != "game":
            return

        game = extract_game_data(details)

        dataset[appid] = game

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


def build_dataset(app_list, dataset, country=DEFAULT_COUNTRY_CODE, language=DEFAULT_LANGUAGE, skip_existing=DEFAULT_SKIP_EXISTING):
    total = len(app_list)

    cu.log(
        "INFO",
        f"Fetching details for {total} applications... "
        "(CTRL+C to exit)"
    )

    for index, app in enumerate(app_list, start=1):
        appid = str(app["appid"])
        name = app.get("name", "")

        print_progress(
            index - 1,
            total,
            f"{name} ({appid})"
        )

        if skip_existing and appid in dataset:
            continue

        process_app(
            app,
            dataset,
            country,
            language
        )

        cu.save_json(dataset, DEFAULT_DATASET_FILE)

        time.sleep(REQUEST_DELAY)

    print_progress(total, total, "")
    print()


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
        help="Country code"
    )

    parser.add_argument(
        "-l", "--language", type=str, default=DEFAULT_LANGUAGE,
        help="Language code"
    )

    parser.add_argument(
        "-si", "--skip-existing", type=str, default=DEFAULT_SKIP_EXISTING,
        help=""
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    cu.log("INFO", "Starting GamesScraper.py")

    dataset = load_dataset()

    start_time = time.time()

    app_list = load_app_list(args.max_apps)

    build_dataset(
        app_list,
        dataset,
        args.country,
        args.language,
        args.skip_existing
    )

    duration = time.time() - start_time

    cu.log(
        "INFO",
        f"Data fetching completed in {duration:.2f} seconds."
    )

    cu.save_json(dataset, DEFAULT_DATASET_FILE)

    cu.log(
        "INFO",
        f"Dataset saved to '{DEFAULT_DATASET_FILE}' "
        f"with {len(dataset)} entries."
    )


if __name__ == "__main__":
    main()
