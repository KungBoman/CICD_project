"""
build a dataset
"""

import common_util as cu

import time
import datetime
import requests
import argparse
from tqdm import tqdm


STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
"""
Documentation:
https://github-wiki-see.page/m/Revadike/InternalSteamWebAPI/wiki/
Get-App-Details?utm_source=chatgpt.com
"""

REQUEST_TIMEOUT = 15

DEFAULT_DATASET_INFILE = "games_dataset.json"
DEFAULT_DATASET_OUTFILE = "games_dataset.json"
DEFAULT_COUNTRY_CODE = "se"
DEFAULT_LANGUAGE = "en"
DEFAULT_FORCE_REWRITE = False
DEFAULT_REQUEST_DELAY = 0
DEFAULT_MAX_RETRIES = 4
DEFAULT_RETRY_DELAY = 10


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


def get_app_details(
    appid,
    country=DEFAULT_COUNTRY_CODE,
    language=DEFAULT_LANGUAGE,
    filters=None,
    max_retries=DEFAULT_MAX_RETRIES,
    retry_delay=DEFAULT_RETRY_DELAY
):
    params = {
        "appids": appid,
        "cc": country,
        "l": language
    }

    if filters:
        params["filters"] = filters

    for attempt in range(max_retries + 1):
        response = requests.get(
            STEAM_APP_DETAILS_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 429:
            if attempt >= max_retries:
                response.raise_for_status()

            wait_time = retry_delay * (attempt + 1)

            cu.log(
                "WARNING",
                f"Rate limited for app {appid}. "
                f"Retrying in {wait_time}s..."
            )

            time.sleep(wait_time)
            continue

        response.raise_for_status()

        data = response.json()

        app_data = data.get(str(appid))

        if not app_data:
            return None

        if not app_data.get("success"):
            return None

        return app_data.get("data")

    return None


def extract_game_data(details):
    game_data = {}

    game_data["appid"] = details.get("steam_appid")
    game_data["name"] = details.get("name")

    release_date = details.get("release_date", {})
    if release_date.get("coming_soon"):
        game_data["release_date"] = None
    else:
        date = release_date.get("date")
        game_data["release_date"] = (
            datetime.datetime.strptime(date, "%d %b, %Y").strftime("%Y-%m-%d")
            if date
            else None
        )

    is_free = details.get("is_free", False)
    game_data["is_free"] = is_free

    price_overview = details.get("price_overview", {})

    game_data["price"] = (
        0.0 if is_free
        else price_overview.get("final", 0) / 100
    )

    game_data["currency"] = price_overview.get("currency")
    game_data["about_the_game"] = details.get("about_the_game")
    game_data["short_description"] = details.get("short_description")
    game_data["detailed_description"] = details.get("detailed_description")

    game_data["dlc_count"] = len(details.get("dlc", []))

    game_data["achievements"] = details.get("achievements", {}).get("total", 0)
    game_data["recommendations"] = details.get("recommendations", {}).get("total", 0)

    platforms = details.get("platforms", {})
    game_data["windows"] = platforms.get("windows", False)
    game_data["mac"] = platforms.get("mac", False)
    game_data["linux"] = platforms.get("linux", False)

    metacritic = details.get("metacritic", {})
    game_data["metacritic_score"] = metacritic.get("score")
    game_data["metacritic_url"] = metacritic.get("url")

    return game_data


def load_dataset(file=DEFAULT_DATASET_INFILE):
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


def process_app(
    app,
    dataset,
    country=DEFAULT_COUNTRY_CODE,
    language=DEFAULT_LANGUAGE,
    max_retries=DEFAULT_MAX_RETRIES,
    retry_delay=DEFAULT_RETRY_DELAY
):
    appid = str(app["appid"])

    try:
        details = get_app_details(
            appid,
            country=country,
            language=language,
            max_retries=max_retries,
            retry_delay=retry_delay
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


def build_dataset(
    app_list,
    dataset,
    outfile=DEFAULT_DATASET_OUTFILE,
    country=DEFAULT_COUNTRY_CODE,
    language=DEFAULT_LANGUAGE,
    force=DEFAULT_FORCE_REWRITE,
    delay=DEFAULT_REQUEST_DELAY,
    max_retries=DEFAULT_MAX_RETRIES,
    retry_delay=DEFAULT_RETRY_DELAY
):
    total = len(app_list)

    cu.log(
        "INFO",
        f"Fetching details for {total} applications... "
        "(CTRL+C to exit)"
    )

    for app in tqdm(
        app_list,
        desc="Fetching games",
        unit="app",
        smoothing=0.1
    ):
        appid = str(app["appid"])
        name = app.get("name", "")

        if not force and appid in dataset:
            continue

        process_app(
            app,
            dataset,
            country=country,
            language=language,
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        cu.save_json(dataset, outfile)

        time.sleep(delay)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch Steam application list."
    )

    parser.add_argument(
        "-i", "--infile", type=str, default=DEFAULT_DATASET_INFILE,
        help="Input dataset file."
    )

    parser.add_argument(
        "-o", "--outfile", type=str, default=DEFAULT_DATASET_OUTFILE,
        help="Output dataset file."
    )

    parser.add_argument(
        "-ma", "--max-apps", type=int, default=None,
        help="Maximum number of apps to fetch. "
             "If omitted, fetch all apps."
    )

    parser.add_argument(
        "-c", "--country", type=str, default=DEFAULT_COUNTRY_CODE,
        help="Country code."
    )

    parser.add_argument(
        "-l", "--language", type=str, default=DEFAULT_LANGUAGE,
        help="Language code."
    )

    parser.add_argument(
        "-f", "--force", type=cu.str_to_bool, default=DEFAULT_FORCE_REWRITE,
        help="Overwrite existing apps."
    )

    parser.add_argument(
        "-d", "--delay", type=int, default=DEFAULT_REQUEST_DELAY,
        help="Time in seconds to delay each query."
    )
    parser.add_argument(
        "-r", "--retries", type=int, default=DEFAULT_MAX_RETRIES,
        help="Number of retries. Always retry when 0."
    )
    parser.add_argument(
        "-rd", "--retry-delay", type=int, default=DEFAULT_RETRY_DELAY,
        help="Time in seconds before retry query."
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    cu.log("INFO", "Starting GamesScraper.py")

    dataset = load_dataset(args.infile)

    app_list = load_app_list(args.max_apps)

    start_time = time.time()

    build_dataset(
        app_list,
        dataset,
        outfile=args.outfile,
        country=args.country,
        language=args.language,
        force=args.force,
        delay=args.delay,
        max_retries=args.retries,
        retry_delay=args.retry_delay
    )

    duration = time.time() - start_time

    cu.log(
        "INFO",
        f"Data fetching completed in {duration:.2f} seconds."
    )

    cu.save_json(dataset, args.outfile)

    cu.log(
        "INFO",
        f"Dataset saved to '{args.outfile}' "
        f"with {len(dataset)} entries."
    )


if __name__ == "__main__":
    main()
