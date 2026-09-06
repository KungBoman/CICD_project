import csv

from load_steam import read_csv_data


def test_read_csv_data(tmp_path):
    file_path = tmp_path / "test_games.csv"

    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["appid", "name"]
        )

        writer.writeheader()
        writer.writerow({
            "appid": "10",
            "name": "Counter-Strike"
        })

    rows = read_csv_data(file_path)

    assert len(rows) == 1
    assert rows[0]["appid"] == "10"
    assert rows[0]["name"] == "Counter-Strike"