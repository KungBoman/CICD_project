from pathlib import Path

import duckdb

# Find the current path direction
BASE_DIR = Path(__file__).resolve().parent

con = duckdb.connect("steam_games.db")
RAW_TABLE = (BASE_DIR / "test_data.csv").as_posix()
TABLE_NAME = 'transform_games_list'

# create table and tranform data  
def transform_data(con, raw_table, table_name):
    # Insert and transform data 
    con.execute(f"""
    CREATE OR REPLACE TABLE {table_name} AS 
        SELECT
            TRY_CAST(appid AS INT) AS appid,
            TRIM(name) AS name,
            TRIM(header_image) AS header_image,
            TRIM(website) AS website,
            TRY_CAST(release_date as DATE) AS release_date, -- upcomming game, date kan vara NULL
            TRY_CAST(is_free AS BOOLEAN) AS is_free,
            TRY_CAST(price AS DECIMAL(10,2)) AS price, -- check if price < 0
            TRIM(currency) AS currency, -- EUR
            TRIM(about_the_game) AS about_the_game,
            TRIM(short_description) AS short_description,
            TRIM(detailed_description) AS detailed_description,
            TRY_CAST(dlc_count AS INT) AS downloadable_content, -- check if value < 0
            TRY_CAST(achievements AS INT) AS achievements, -- achievements value should not be negative
            TRY_CAST(recommendations AS INT) AS recommendations, -- value should not be negative or NULL
            TRY_CAST(windows AS BOOLEAN) AS windows,
            TRY_CAST(mac AS BOOLEAN) AS mac,
            TRY_CAST(linux AS BOOLEAN) AS linux,
            TRY_CAST(metacritic_score AS SMALLINT) AS metacritic_score, -- check if 0 <= the value >= 100, OBS ! do not change value = 0 when it is NULL  
            TRIM(metacritic_url) AS metacritic_url, -- check if NULL or start with 'https: //
            TRIM(support_url) AS support_url, -- check if NULL or start with 'https: //
            TRIM(support_email) AS support_email, 
            TRIM(supported_languages) AS supported_languages, -- have more than one value like Japanese, English, Swedish
            TRIM(full_audio_languages) AS full_audio_languages, -- have more than one value
            TRIM(developers) AS developers, -- have more than one value 
            TRIM(publishers) AS publishers, -- publishers have more than one value
            TRIM(categories) AS categories, -- have more than one value
            TRIM(genres) AS genres

        FROM read_csv_auto('{raw_table}')
""")

if __name__ == "__main__":
    transform_data(con, RAW_TABLE, TABLE_NAME)
    con.execute(f"COPY {TABLE_NAME} TO transform_game_list.csv (FORMAT CSV, HEADER true)")

print(
    con.execute("""
        sUMMARIZE
        SELECT *
        FROM read_csv_auto(transform_game_list.csv)
    """).fetchdf()
)


