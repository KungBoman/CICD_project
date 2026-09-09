import time

import requests
from database_connection import engine
from sqlalchemy import text

STEAM_API_URL = "https://store.steampowered.com/api/appdetails"
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 1.5
MAX_RETRIES = 3 
TABLE_NAME = "game_trailers"

def fetch_trailer_url(appid: int):
    for attempt in range(MAX_RETRIES):
        try:
            respond = requests.get(STEAM_API_URL, params={"appids": appid}, timeout=REQUEST_TIMEOUT)
            respond.raise_for_status()
            data = respond.json()
            
            entry = data.get(str(appid))
            if not entry or not entry.get("success"):
                return None
            movies = entry.get("data", {}).get("movies")
            if not movies:
                return None

            first_movie = movies[0]
            return first_movie.get("hls_h264") or first_movie.get("dash_h264") or first_movie.get("dash_av1")
            
        except requests.exceptions.Timeout:
            wait = 2 ** attempt
            time.sleep(wait)

        except requests.exceptions.HTTPError as error:
            error_code = error.response.status_code
            if 500 <= error_code < 600:
                wait = 2 ** attempt
                print(f"Server error {error_code}, try again after {wait}s, time {attempt + 1}/{MAX_RETRIES}")
                time.sleep(wait)
            else:
                print(f"Request error : {error}")
                return None

        except requests.exceptions.RequestException as error:
            print(f"Another error when calling the API : {error}")

    print("All retries have been used, the attempt to get data failed")

def get_trailers():
    with engine.connect() as conn:
        result = conn.execute(text("""
        SELECT g.appid 
        FROM games_applications g
        LEFT JOIN game_trailers t ON g.appid = t.appid
        WHERE t.appid IS NULL
"""))
        
        appids = []
        for row in result:
            appids.append(row.appid)

    print(f"Need to get {len(appids)} trailers")

    for i, appid in enumerate(appids):
        trailer_url = fetch_trailer_url(appid)
        with engine.connect() as conn:
            conn.execute(text(f"""
            INSERT INTO {TABLE_NAME}(appid, trailer_url)
            VALUES(:appid, :trailer_url)
            -- Update the current trailer URL with the new trailer URL.
            ON CONFLICT(appid) DO UPDATE SET trailer_url=EXCLUDED.trailer_url, fetched_at=CURRENT_TIMESTAMP
        """), 
            {"appid":appid, "trailer_url":trailer_url})

            conn.commit()

        if(i + 1) % 20 == 0:
            print(f"Processed {i+1}/{len(appids)}")

        time.sleep(REQUEST_DELAY)
    print("Completed getting trailers")


def create_game_trailer_table():
    with engine.connect() as conn:
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
            appid INT PRIMARY KEY REFERENCES games_applications(appid),
            trailer_url TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        conn.commit()
    print(f"Create {TABLE_NAME} successfully")

if __name__ == "__main__":
    create_game_trailer_table()
    get_trailers()  