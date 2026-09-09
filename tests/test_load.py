import csv

from load_steam import (
    create_games_table,
    get_db_connection,
    insert_games,
    read_csv_data,
)


def test_full_load(tmp_path):
    file_path = tmp_path / "test_games.csv"

    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "appid",
                "name",
                "release_date",
                "is_free",
                "price",
                "currency",
            ],
        )

        writer.writeheader()
        writer.writerow({
            "appid": "10",
            "name": "Counter-Strike",
            "release_date": "2000-11-01",
            "is_free": "false",
            "price": "8.19",
            "currency": "EUR",
        })

    rows = read_csv_data(file_path)
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS games")
        connection.commit()

        create_games_table(connection)
        insert_games(connection, rows)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT appid, name, release_date, is_free, price, currency
                FROM games
                WHERE appid = 10
            """)
            result = cursor.fetchone()

        assert result is not None
        assert result[0] == 10
        assert result[1] == "Counter-Strike"
        assert str(result[2]) == "2000-11-01"
        assert result[3] is False
        assert float(result[4]) == 8.19
        assert result[5] == "EUR"

    finally:
        connection.close()