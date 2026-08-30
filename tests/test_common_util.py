import common_util as cu


def expected_app(appid, name):
    return {
        "appid": appid,
        "name": name
    }


def test_save_and_load_csv_list(tmp_path):
    data = [
        expected_app(10, "Counter-Strike"),
        expected_app(20, "Team Fortress Classic")
    ]

    filename = tmp_path / "games.csv"

    cu.save_csv(data, filename)

    result = cu.load_csv(filename)

    assert result == data


def test_Save_And_load_csv_dict(tmp_path):
    data = {
        "10": expected_app(10, "Counter-Strike"),
        "20": expected_app(20, "Team Fortress Classic")
    }

    filename = tmp_path / "games.csv"

    cu.save_csv(data, filename)

    cu.save_csv(data, filename)

    result = cu.load_csv(filename, key="appid")

    assert result == data
