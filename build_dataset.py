"""
build a dataset
"""

import argparse
import datetime
import html
import re
import sys
import time
from dataclasses import dataclass

import requests
from tqdm import tqdm

import common_util as cu

STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
"""
Documentation:
https://github-wiki-see.page/m/Revadike/InternalSteamWebAPI/wiki/
Get-App-Details?utm_source=chatgpt.com
"""

REQUEST_TIMEOUT = 15

DEFAULT_DATASET_INFILE = "data/games_dataset.json"
DEFAULT_DATASET_OUTFILE = "data/games_dataset.json"
DEFAULT_MAX_APPS = None
DEFAULT_COUNTRY_CODE = "se"
DEFAULT_LANGUAGE = "en"
DEFAULT_REQUEST_DELAY = 1.5
DEFAULT_MAX_RETRIES = 4
DEFAULT_RETRY_DELAY = 10
DEFAULT_INCREMENTAL_RETRY_DELAY = False
DEFAULT_SANITIZE_TEXT = True
DEFAULT_FORCE_REWRITE = False


@dataclass
class DatasetConfig:
    country: str = DEFAULT_COUNTRY_CODE
    language: str = DEFAULT_LANGUAGE
    filters: str = ""
    delay: float = DEFAULT_REQUEST_DELAY
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY
    incremental_retry_delay: float = DEFAULT_INCREMENTAL_RETRY_DELAY
    sanitize_text: bool = DEFAULT_SANITIZE_TEXT
    force: bool = DEFAULT_FORCE_REWRITE


def load_app_list(max_apps=None):
    app_list = cu.load_json("data/app_list.json")

    if not app_list:
        cu.log(
            "ERROR",
            "Missing app list. Run \"fetch_app_list.py\" first."
        )
        sys.exit(1)

    if max_apps is not None:
        app_list = app_list[:max_apps]
        cu.log(
            "INFO",
            f"Limiting app_list to {len(app_list)} apps for this run."
        )

    return app_list


def get_app_details(appid, config=None):
    if config is None:
        config = DatasetConfig()

    params = {
        "appids": appid,
        "cc": config.country,
        "l": config.language
    }

    if config.filters:
        params["filters"] = config.filters

    for attempt in range(config.max_retries + 1):
        response = requests.get(
            STEAM_APP_DETAILS_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 429:
            if attempt >= config.max_retries:
                response.raise_for_status()

            wait_time = (
                config.retry_delay * (attempt + 1)
                if config.incremental_retry_delay
                else config.retry_delay
            )

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


def clean_description(text, config=None):
    if config is None:
        config = DatasetConfig()

    if not text:
        return ""

    if not config.sanitize_text:
        return text

    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove BBCode tags
    text = re.sub(r"\[/?[a-zA-Z][^\]]*\]", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_languages(value):
    interface_languages = []
    audio_languages = []

    if not value:
        return interface_languages, audio_languages

    # Remove HTML tags
    value = re.sub(r"<[^>]+>", "", value)

    # Remove the footnote text
    value = value.replace(
        "languages with full audio support",
        ""
    )

    for language in value.split(","):
        language = language.strip()

        if not language:
            continue

        is_full_audio = "*" in language
        language = language.replace("*", "").strip()

        interface_languages.append(language)

        if is_full_audio:
            audio_languages.append(language)

    return interface_languages, audio_languages


def extract_game_data(details, config=None):
    if config is None:
        config = DatasetConfig()

    game_data = {}

    game_data["appid"] = details.get("steam_appid")
    game_data["name"] = details.get("name")
    game_data["header_image"] = details.get("header_image", "")
    game_data["website"] = details.get("website", "")

    release_date = details.get("release_date", {})
    if release_date.get("coming_soon"):
        game_data["release_date"] = "1970-01-01"
    else:
        date = release_date.get("date")
        game_data["release_date"] = (
            datetime.datetime.strptime(
                date,
                "%d %b, %Y"
            ).replace(
                tzinfo=datetime.timezone.utc
            ).date().isoformat()
            if date
            else "1970-01-01"
        )

    is_free = details.get("is_free", False)
    game_data["is_free"] = is_free

    price_overview = details.get("price_overview", {})

    game_data["price"] = (
        0.0 if is_free
        else price_overview.get("final", 0) / 100
    )
    game_data["currency"] = price_overview.get("currency") or ""

    game_data["about_the_game"] = clean_description(
        details.get("about_the_game")
    )
    game_data["short_description"] = clean_description(
        details.get("short_description")
    )
    game_data["detailed_description"] = clean_description(
        details.get("detailed_description")
    )

    game_data["dlc_count"] = len(details.get("dlc", []))
    game_data["achievements"] = details.get("achievements", {}).get("total", 0)
    game_data["recommendations"] = details.get("recommendations", {}).get("total", 0)

    platforms = details.get("platforms", {})
    game_data["windows"] = platforms.get("windows", False)
    game_data["mac"] = platforms.get("mac", False)
    game_data["linux"] = platforms.get("linux", False)

    metacritic = details.get("metacritic", {})
    game_data["metacritic_score"] = metacritic.get("score") or ""
    game_data["metacritic_url"] = metacritic.get("url") or ""

    support_info = details.get("support_info", {})
    game_data["support_url"] = support_info.get("url") or ""
    game_data["support_email"] = support_info.get("email") or ""

    interface_languages, audio_languages = extract_languages(
        details.get("supported_languages")
    )
    game_data["interface_languages"] = ", ".join(interface_languages)
    game_data["audio_languages"] = ", ".join(audio_languages)

    game_data["developers"] = ", ".join(details.get("developers", []))
    game_data["publishers"] = ", ".join(details.get("publishers", []))

    categories = details.get("categories", [])
    category_ids = [
        str(cat["id"]) for cat in categories
    ]
    category_descriptions = [
        cat["description"] for cat in categories
    ]
    game_data["category_ids"] = ", ".join(category_ids)
    game_data["category_descriptions"] = ", ".join(category_descriptions)

    genres = details.get("genres", [])
    genre_ids = [
        str(gen["id"]) for gen in genres
    ]
    genre_descriptions = [
        gen["description"] for gen in genres
    ]
    game_data["genre_ids"] = ", ".join(genre_ids)
    game_data["genre_descriptions"] = ", ".join(genre_descriptions)

    return game_data


def convert_dataset_row(row):
    return {
        "appid": int(row["appid"]),
        "name": row["name"],
        "header_image": row["header_image"] or "",
        "website": row["website"] or "",
        "release_date": row["release_date"] or "1970-01-01",
        "is_free": row["is_free"].lower() == "true",
        "price": (
            float(row["price"])
            if row["price"]
            else 0.0
        ),
        "currency": row["currency"] or "",
        "about_the_game": row["about_the_game"],
        "short_description": row["short_description"],
        "detailed_description": row["detailed_description"],
        "dlc_count": int(row["dlc_count"]),
        "achievements": int(row["achievements"]),
        "recommendations": int(row["recommendations"]),
        "windows": row["windows"].lower() == "true",
        "mac": row["mac"].lower() == "true",
        "linux": row["linux"].lower() == "true",
        "metacritic_score": (
            int(row["metacritic_score"])
            if row["metacritic_score"]
            else ""
        ),
        "metacritic_url": row["metacritic_url"] or "",
        "support_url": row["support_url"] or "",
        "support_email": row["support_email"] or "",
        "interface_languages": row["interface_languages"],
        "audio_languages": row["audio_languages"],
        "developers": row["developers"],
        "publishers": row["publishers"],
        "category_ids": row["category_ids"],
        "category_descriptions": row["category_descriptions"],
        "genre_ids": row["genre_ids"],
        "genre_descriptions": row["genre_descriptions"],
    }


def load_dataset(filename=DEFAULT_DATASET_INFILE):
    if filename.endswith(".json"):
        dataset = cu.load_json(filename)
    elif filename.endswith(".csv"):
        rows = cu.load_csv(filename)
        dataset = {
            str(row["appid"]): convert_dataset_row(row)
            for row in rows
        }

    if not dataset:
        cu.log(
            "INFO",
            f"No data found in '{filename}'. "
            "Starting with an empty dataset."
        )
        dataset = {}
    else:
        cu.log(
            "INFO",
            f"Loaded dataset from '{filename}' "
            f"with {len(dataset)} entries."
        )

    return dataset


def save_dataset(dataset, filename):
    if filename.endswith(".json"):
        cu.save_json(dataset, filename)
    elif filename.endswith(".csv"):
        cu.save_csv(dataset, filename)
    else:
        raise ValueError(f"Unsupported file format: {filename}")


def process_app(app, dataset, config=None):
    if config is None:
        config = DatasetConfig()

    appid = str(app["appid"])

    try:
        details = get_app_details(appid, config=config)

        if not details:
            return

        if details.get("type") != "game":
            return

        game = extract_game_data(details, config)

        dataset[appid] = game

    except requests.RequestException as error:
        cu.log(
            "ERROR",
            f"Failed to fetch app {appid}: {error}"
        )

    except (KeyError, ValueError, TypeError) as error:
        cu.log(
            "ERROR",
            f"Unexpected error for app {appid}: {error}"
        )


def build_dataset(
    app_list,
    dataset,
    outfile,
    config=None,
):
    if config is None:
        config = DatasetConfig()

    apps_to_fetch = [
        app for app in app_list
        if config.force or str(app["appid"]) not in dataset
    ]

    total = len(apps_to_fetch)

    cu.log(
        "INFO",
        f"Fetching details for {total} applications... "
        "(CTRL+C to exit)"
    )

    for app in tqdm(
        apps_to_fetch,
        desc="Fetching games",
        unit="app",
        smoothing=0.1
    ):
        appid = str(app["appid"])

        if not config.force and appid in dataset:
            continue

        request_time = time.time()

        process_app(
            app,
            dataset,
            config=config
        )

        save_dataset(dataset, outfile)

        elapsed = time.time() - request_time
        wait_time = max(0, config.delay - elapsed)
        time.sleep(wait_time)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch Steam application details and build a dataset."
    )

    parser.add_argument(
        "-i", "--infile",
        type=str,
        default=DEFAULT_DATASET_INFILE,
        help="Input dataset filename. Supported formats: .json, .csv."
    )

    parser.add_argument(
        "-o", "--outfile",
        type=str,
        default=DEFAULT_DATASET_OUTFILE,
        help="Output dataset filename. Supported formats: .json, .csv."
    )

    parser.add_argument(
        "-m", "--max-apps",
        type=int,
        default=DEFAULT_MAX_APPS,
        help="Maximum number of apps to fetch. If omitted, all apps are fetched."
    )

    parser.add_argument(
        "-c", "--country",
        type=str,
        default=DEFAULT_COUNTRY_CODE,
        help="Country code used for Steam store data."
    )

    parser.add_argument(
        "-l", "--language",
        type=str,
        default=DEFAULT_LANGUAGE,
        help="Language used for Steam store data."
    )

    parser.add_argument(
        "-d", "--delay",
        type=int,
        default=DEFAULT_REQUEST_DELAY,
        help="Delay in seconds between requests."
    )

    parser.add_argument(
        "-r", "--retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help="Maximum number of retries after a rate limit."
    )

    parser.add_argument(
        "-rd", "--retry-delay",
        type=int,
        default=DEFAULT_RETRY_DELAY,
        help="Initial delay in seconds before retrying a rate-limited request."
    )

    parser.add_argument(
        "--incremental-retry-delay",
        type=cu.str_to_bool,
        default=DEFAULT_INCREMENTAL_RETRY_DELAY,
        help="Increment the retry delay after each failed retry."
    )

    parser.add_argument(
        "--sanitize-text",
        type=cu.str_to_bool,
        default=DEFAULT_SANITIZE_TEXT,
        help="Sanitize text fields by removing HTML tags and formatting codes."
    )

    parser.add_argument(
        "-f", "--force",
        type=cu.str_to_bool,
        default=DEFAULT_FORCE_REWRITE,
        help="Overwrite existing dataset entries."
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    config = DatasetConfig(
        country=args.country,
        language=args.language,
        delay=args.delay,
        max_retries=args.retries,
        retry_delay=args.retry_delay,
        incremental_retry_delay=args.incremental_retry_delay,
        sanitize_text=args.sanitize_text,
        force=args.force
    )

    cu.log("INFO", "Starting GamesScraper.py")

    dataset = load_dataset(args.infile)

    app_list = load_app_list(args.max_apps)

    start_time = time.time()

    build_dataset(
        app_list,
        dataset,
        outfile=args.outfile,
        config=config,
    )

    duration = time.time() - start_time

    cu.log(
        "INFO",
        f"Data fetching completed in {duration:.2f} seconds."
    )

    save_dataset(dataset, args.outfile)

    cu.log(
        "INFO",
        f"Dataset saved to '{args.outfile}' "
        f"with {len(dataset)} entries."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Quitting...")
