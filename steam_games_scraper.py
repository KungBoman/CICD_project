import json
import os
import time
from datetime import date

import duckdb
import requests
from dotenv import load_dotenv

con = duckdb.connect("steam_games.db")

# Find the current path direction
TABLE_NAME = "games_list"
TABLE_NAME_STEAMSPY = "steamspy_games_list"

DEFAULT_DATASET_STEAMSPY_FILE_JSONL = f"steam_spy_games_{date.today()}.jsonl"
DEFAULT_DATASET_FILE_JSONL = f"games_{date.today()}.jsonl"
ENCODING = "utf-8"
load_dotenv()
api_key = os.getenv("STEAMGAMES_API_KEY")  

if api_key is None:
    raise ValueError("STEAMGAMES_API_KEY not found, check .env file")

api_url = "https://api.steampowered.com/IStoreService/GetAppList/v1"
api_url_steamspy = f"https://steamspy.com/api.php?request=appdetails&appid={api_key}"

# handling exception when get dataset 
def get_with_retry(url, params, max_retries=3):
    for attempt in range(max_retries):
        try: 
            response = requests.get(url, params, timeout=5)
            response.raise_for_status()
            data = response.json()
            print("Success get data.")
            return data
        except requests.exceptions.Timeout:
            wait = 2 ** attempt
            time.sleep(wait)

        except requests.exceptions.HTTPError as error:
            error_code = error.response.status_code
            if 500 <= error_code < 600:
                wait = 2 ** attempt
                print(f"Server error {error_code}, try again after {wait}s (times {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else: 
                print(f"Request error : {error}")
                return None

        except requests.exceptions.RequestException as error:
            print(f"Another errror when calling the API: {error}")

    print("All retry attempts has been used, the attempt failed.")
    return None

def SteamGamesRequest(start_url):
    all_games = []
    url = start_url
    last_appid = 0
    
    while url is not None:
        # params = {"key":api_key, "last_appid": last_appid, "max_results":2000}
        
        params = {"response": True, "last_appid": last_appid, "key": api_key, "max_results":2000} 
        games_data = get_with_retry(url, params=params, max_retries=3)
        if games_data is None:
            print("Stopped due there is no data")
            break
        else:
            # get only valuse of dict "response"
            page = games_data["response"]
            # add only values from dict "apps" in dict "response" to all_games list
            all_games.extend(page["apps"])
            print(f"Data has been scraped from {url}")
            print(f"Fetched {len(page['apps'])} apps (total so far: {len(all_games)})")

        # Stop the while loop when there are no more pages.
        if not page.get('have_more_results'):
            break
        # If there are still pages, get the cursor for the next call
        else:
            last_appid = page["last_appid"] 
    return all_games

def SteamSpyRequest():
    all_steamspy_data = {}
    page = 0

    while True:
        params = {"request": "all", "page": page}
        steam_spy_data = get_with_retry(api_url_steamspy, params=params, max_retries=2)

        if steam_spy_data is None:
            print("Stopped due there is no data")
            break
        if not steam_spy_data:
            print(f"Page {page} empty — data has run out, stop")
            break
        else:
            all_steamspy_data.update(steam_spy_data)
            print(f"Page {page}: fetched {len(steam_spy_data)} apps (total so far: {len(all_steamspy_data)})")
            page += 1
            time.sleep(60)
        
    return all_steamspy_data

# SAVE TO JSONL FILE
def save_jsonl(games, filename):
    # Save it to a temporary file tmp_path first; rename it after the complete recording is finished.
    tmp_path = filename + ".tmp"
    with open(tmp_path, "w", encoding=ENCODING) as file:
        for game in games:
            line = json.dumps(game, ensure_ascii=False)
            file.write(line + "\n")
    # rename file tmp_path to filename
    os.replace(tmp_path, filename)

# Importing steam games data from a .JSONL file into empty table.
def import_to_empty_table(data_name):
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            appid INTEGER PRIMARY KEY,
            name VARCHAR,
            last_modified BIGINT,
            price_change_number BIGINT
        )
    """)

    con.execute(f"""
        INSERT INTO {TABLE_NAME}
        SELECT * FROM read_json_auto(?)
        ON CONFLICT (appid) DO NOTHING
    """,[data_name])

# update new data to table games_list
def update_data_to_table(data_name):
    con.execute(f"""
        INSERT INTO {TABLE_NAME}
        SELECT * FROM read_json_auto(?)
        ON CONFLICT (appid) DO UPDATE SET
            name = EXCLUDED.name,
            last_modified = EXCLUDED.last_modified,
            price_change_number = EXCLUDED.price_change_number
    """, [data_name])


def import_steamspy_data_to_empty_table(data_name):
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME_STEAMSPY} AS (
            SELECT  appid,
                    name,
                    developer,
                    publisher,
                    score_rank,
                    positive,
                    negative, 
                    userscore, 
                    owners, 
                    average_forever, 
                    average_2weeks,
                    median_forever, 
                    median_2weeks, 
                    price, 
                    initialprice, 
                    discount, 
                    ccu
        )
    """)

    con.execute(f"""
        INSERT INTO {TABLE_NAME_STEAMSPY}
        SELECT * FROM read_json_auto(?)
        ON CONFLICT (appid) DO NOTHING
    """,[data_name])

# update new data to table steamspy_games_list
def update_steamspy_data_to_table(data_name):
    con.execute(f"""
        INSERT INTO {TABLE_NAME_STEAMSPY}
        SELECT * FROM read_json_auto(?)
        ON CONFLICT (appid) DO UPDATE SET
            name = EXCLUDED.name,
            last_modified = EXCLUDED.last_modified,
            price_change_number = EXCLUDED.price_change_number
    """, [data_name])

# steam_games = SteamGamesRequest(api_url)

# save_jsonl(steam_games, DEFAULT_DATASET_FILE_JSONL)

# print(f"Saved {len(steam_games)} games to {DEFAULT_DATASET_FILE_JSONL}")   

# size_jsonl = os.path.getsize(DEFAULT_DATASET_FILE_JSONL) 

# import_to_empty_table(DEFAULT_DATASET_FILE_JSONL) 

# update_data_to_table(DEFAULT_DATASET_FILE_JSONL)

# con.execute(f"COPY {TABLE_NAME} TO 'games_list.csv' (FORMAT csv, HEADER true)")

# print(con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone())  
# print(con.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5").fetchall())



# all_steamspy_data = SteamSpyRequest()
# print(f"Total apps fetched: {len(all_steamspy_data)}")

# # Get the values ​​from the dictionary and change them to list before passing them to the save_jsonl which is for a list of dicts
# save_jsonl(list(all_steamspy_data.values()), DEFAULT_DATASET_STEAMSPY_FILE_JSONL)
# print(f"Saved {len(all_steamspy_data)} games to {DEFAULT_DATASET_STEAMSPY_FILE_JSONL}")

#test
print(con.execute(f"DESCRIBE SELECT * FROM read_json_auto('{DEFAULT_DATASET_STEAMSPY_FILE_JSONL}')").fetchall())

# import_steamspy_data_to_empty_table(DEFAULT_DATASET_STEAMSPY_FILE_JSONL)
# update_steamspy_data_to_table(DEFAULT_DATASET_STEAMSPY_FILE_JSONL)

# con.execute(f"COPY {TABLE_NAME_STEAMSPY} TO {TABLE_NAME_STEAMSPY} (FORMAT csv, HEADER true)")