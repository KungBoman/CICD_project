import psycopg2
import csv
import os


def read_csv_data(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "steam_games"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )



def create_games_table(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                appid INTEGER PRIMARY KEY,
                name TEXT,
                release_date DATE,
                is_free BOOLEAN,
                price DECIMAL(10,2),
                currency TEXT
            )

        """)
    connection.commit()


def insert_games(connection, rows): 
    with connection.cursor() as cursor:
        for row in rows:
            cursor.execute(
                """
                INSERT INTO games (
                    appid,
                    name,
                    rekease_date,
                    is_free,
                    price,
                    currency
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    row["appid"],
                    row["name"],
                    row["release_date"],
                    row["is_free"],
                    row["price"],
                    row["currency"],
                )
            )
    connection.commit()


def load_data(input_file):
    rows = read_csv_data(input_file)
    connection = get_db_connection()

    create_games_table(connection)
    insert_games(connection, rows)

    connection.close()
