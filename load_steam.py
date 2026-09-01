import psycopg2
import csv


def read_csv_data(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_db_connetion():



def create_games_table(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                appid BIGINT PRIMARY KEY,
                name TEXT
                ....
            
            )

        """)
    connection.commit()


def insert_games(connection, rows): 


def load_data(input_file):

