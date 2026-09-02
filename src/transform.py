import duckdb

import common_util as cu

# Find the current path direction
RAW_TABLE = (cu.DATA_DIR / "raw_games_dataset.csv")
TABLE_NAME = 'curated_games_dataset'
OUTPUT_DATASET = (cu.DATA_DIR / "curated_games_dataset.csv")


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
            TRIM(interface_languages) AS interface_languages,
            TRIM(audio_languages) AS audio_languages,
            TRIM(developers) AS developers, -- have more than one value 
            TRIM(publishers) AS publishers, -- publishers have more than one value
            TRY_CAST(category_ids AS INT) AS category_ids,
            TRIM(category_descriptions) AS category_descriptions,
            TRY_CAST(genre_ids AS INT) AS genre_ids,
            TRIM(genre_descriptions) AS genre_descriptions,


        FROM read_csv_auto('{raw_table}')
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
