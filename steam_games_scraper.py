import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("STEAMGAMES_API_KEY")

if api_key is None:
    raise ValueError("STEAMGAMES_API_KEY not found, check .env file")

api_url = "https://api.steampowered.com/IStoreService/GetAppList/v1"

# get data 
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

# test result of response 
data_test = get_with_retry(api_url, params={"key":api_key, "max_results":5})
print(json.dumps(data_test, indent=2))
print(data_test['response'].keys())

def get_all_games(start_url):
    all_games = []
    url = start_url
    last_appid = 0
    
    while url is not None:
       # params = {"key":api_key, "last_appid": last_appid, "max_results":2000}
        
        params = {"response": True, "last_appid": last_appid, "key": api_key } 
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
        # Stop the while True loop when there are no more pages.
        if not page.get('have_more_results'):
            break
        # If there are still pages, get the cursor for the next call
        else:
            last_appid = page["last_appid"] 

    return all_games

steam_games = get_all_games(api_url) 
print(f"Total apps fetched : {len(steam_games)}")       

