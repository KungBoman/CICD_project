import common_util as cu


def test_save_and_load_csv_list(tmp_path):
    data = [
        {"appid": "10", "name": "Counter-Strike"},
        {"appid": "20", "name": "Team Fortress Classic"}
    ]

    filename = tmp_path / "games.csv"

    cu.save_csv(data, filename)

    result = cu.load_csv(filename)

    assert result == data


def test_save_and_load_csv_dict(tmp_path):
    data = {
        "10": {"appid": "10", "name": "Counter-Strike"},
        "20": {"appid": "20", "name": "Team Fortress Classic"}
    }

    filename = tmp_path / "games.csv"

    cu.save_csv(data, filename)

    result = cu.load_csv(filename, key="appid")

    assert result == data
