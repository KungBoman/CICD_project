import pandas as pd
from sqlalchemy import text

from database_connection import engine

TABLE_NAME = "games_applications"

def create_tables():
    with engine.connect() as conn:
        # delete old table to update to new structure
        conn.execute(text(f"DROP TABLE IF EXISTS {TABLE_NAME} CASCADE;"))
        # create table applications
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                appid INT PRIMARY KEY,
                name TEXT,
                header_image TEXT,
                website TEXT,
                release_date DATE,
                is_free BOOLEAN,
                price NUMERIC(10, 2),
                currency TEXT,
                about_the_game TEXT,
                short_description TEXT,
                detailed_description TEXT,
                downloadable_content INT,
                achievements INT,
                recommendations INT,
                windows BOOLEAN,
                mac BOOLEAN,
                linux BOOLEAN,
                metacritic_score SMALLINT,
                metacritic_url TEXT,
                support_url TEXT, 
                support_email TEXT, 
                interface_languages TEXT,
                audio_languages TEXT,
                developers TEXT,  
                publishers TEXT, 
                category_ids TEXT,
                category_descriptions TEXT,
                genre_ids TEXT,
                genre_descriptions TEXT,      
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # conn.execute() to send SQL commands directly to PostgreSQL
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_isfree ON {TABLE_NAME}(is_free);"))
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_name ON {TABLE_NAME}(name);"))
        
        # PostgreSQL saves these changes to the disk
        conn.commit()

        print(f"The {TABLE_NAME} table and indexes have been successfully created")

def load_data_to_postgres(df, table_name=TABLE_NAME):
    # Load data into PostgreSQL
    df.to_sql(
        name=table_name,       # declares the name of the target table in the database
        con=engine,            # passes the "connection engine" (SQLAlchemy Engine)
        if_exists='append',    # if the table already contains data append the data.
        index=False,           # do not load default index columns, already have the PK column id
        method='multi',        # increase insert speed
        chunksize=5000         # divide the data into smaller parts for loading.
    )
    print(f"The {len(df):,} records have been loaded into table '{table_name}'")


if __name__ == "__main__":

    df = pd.read_csv("data/curated_games_dataset.csv")
    create_tables()
    load_data_to_postgres(df)
   
