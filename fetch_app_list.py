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

import common_util as cu

import time
import requests
import argparse


APPLIST_FILE = "app_list.json"

STEAM_APP_LIST_URL = "https://api.steampowered.com/IStoreService/GetAppList/v1/"

REQUEST_TIMEOUT = 15
MAX_RESULTS = 50000


def get_app_list(steam_api_key, max_apps=None):
    cu.log("INFO", "Fetching Steam application list...")

    app_list = []
    last_appid = 0

    while True:
        if max_apps is not None:
            remaining = max_apps - len(app_list)

            if remaining <= 0:
                break

            request_max_results = min(
                MAX_RESULTS,
                remaining
            )
        else:
            request_max_results = MAX_RESULTS

        params = {
            "key": steam_api_key,
            "max_results": request_max_results,
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
            app_list.append({
                "appid": app["appid"],
                "name": app.get("name", "")
            })

        have_more_results = response_data.get("have_more_results")
        last_appid = response_data.get("last_appid")

        cu.log(
            "INFO",
            f"Fetched {len(response_apps)} apps "
            f"(total: {len(app_list)})"
            + ("..." if have_more_results else "")
        )

        if not have_more_results:
            break

    return app_list


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Fetch Steam application list."
    )

    parser.add_argument(
        "-ma",
        "--max-apps",
        type=int,
        default=None,
        help="Maximum number of apps to fetch. "
             "If omitted, fetch all apps."
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    cu.log("INFO", "Starting fetch_app_list.py")

    steam_api_key = cu.get_steam_api_key()

    if not steam_api_key:
        cu.log("ERROR", "Steam API Key is invalid.")
        sys.exit(1)

    start_time = time.time()

    try:
        app_list = get_app_list(
            steam_api_key,
            max_apps=args.max_apps
        )

    except requests.RequestException as error:
        cu.log(
            "ERROR",
            f"Failed to fetch Steam app list: {error}"
        )
        sys.exit(1)

    end_time = time.time()
    duration = end_time - start_time

    cu.log(
        "INFO",
        f"Fetched {len(app_list)} applications "
        f"in {duration:.2f} seconds.")

    cu.save_json(app_list, APPLIST_FILE)

    cu.log(
        "INFO",
        f"App list saved to '{APPLIST_FILE}' "
        f"with {len(app_list)} entries."
    )
