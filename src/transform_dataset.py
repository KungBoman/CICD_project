import json

import common_util as cu
import duckdb

# Find the current path direction
RAW_TABLE = cu.DATA_DIR / "raw_games_dataset.csv"
TABLE_NAME = 'curated_games_dataset'
FLATTEN_TABLE_NAME = 'flatten_raw_games_dataset'
OUTPUT_FLATTEN_DATASET = cu.DATA_DIR / "flatten_raw_games_dataset.json"
OUTPUT_DATASET = cu.DATA_DIR / "curated_games_dataset.csv"


# Flattening raw json file
def flatten_json(raw_table, output_flatten):
    with open(raw_table, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Transform JSON object into a Python dict
    if isinstance(data, dict):
        records = list(data.values())
    # Transform JSON object into a Python list   
    elif isinstance(data, list):
        records = data
    else:
        raise TypeError(f"Json is not supported: {type(data)}")
    #save json file after flattening
    with open(output_flatten, "w", encoding="utf-8") as out:
        json.dump(records, out, ensure_ascii=False)

    return output_flatten

def load_dataset(raw_data):
    if raw_data.endswith(".json"):
        return f"read_json('{raw_data}')"
    elif raw_data.endswith(".csv"):
        return f"read_csv('{raw_data}')"
    elif raw_data.endswith(".parquet"):
        return f"read_parquet('{raw_data}')"
    else:
        raise ValueError(f"Not support the format: '{raw_data}'")

# create table and tranform dataset  
def transform_data(con, raw_table, table_name):
    read_dataset = load_dataset(str(raw_table))

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
            TRIM(interface_languages) AS interface_languages,
            TRIM(audio_languages) AS audio_languages,
            TRIM(developers) AS developers, -- have more than one value 
            TRIM(publishers) AS publishers, -- publishers have more than one value
            TRIM(category_ids) AS category_ids,
            TRIM(category_descriptions) AS category_descriptions,
            TRY_CAST(genre_ids AS INT) AS genre_ids,
            TRIM(genre_descriptions) AS genre_descriptions

        FROM --read_csv_auto('{raw_table}')
            {read_dataset}
""")

def log_summarize(con):
    print(
        con.execute(f"""
                sUMMARIZE
                SELECT *
                FROM read_csv_auto('{OUTPUT_DATASET}')
            """).fetchdf()
    )

def main():
    # create a in-memory duckdb database
    con = duckdb.connect(":memory:")

    try:
        flatten_json(RAW_TABLE, OUTPUT_FLATTEN_DATASET)
        transform_data(con, RAW_TABLE, TABLE_NAME)

        con.execute(
            f"COPY {TABLE_NAME} TO '{OUTPUT_DATASET}' "
            "(FORMAT CSV, HEADER true)"
        )
        # log_summarize(con)
    finally:
        con.close()

if __name__ == "__main__":
    main()