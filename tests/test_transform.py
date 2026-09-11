
import json
from datetime import date
from decimal import Decimal

import duckdb
import pytest

from src.transform_dataset import flatten_json, load_dataset, transform_data


# ---- test flatten_json ----
 # in case raw data is a dict
def test_flatten_json_dict_input(tmp_path):
    raw = {"100": {"name": "Game A"}, "200": {"name": "Game B"}}
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw))
    out_path = tmp_path / "flat.json"

    flatten_json(str(raw_path), str(out_path))

    result = json.loads(out_path.read_text())
    assert isinstance(result, list)
    assert len(result) == 2
    assert {"name": "Game A"} in result

 # in case raw data is already a list
def test_flatten_json_list_input(tmp_path):
    raw = [{"name": "Game A"}, {"name": "Game B"}]
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw))
    out_path = tmp_path / "flat.json"

    flatten_json(str(raw_path), str(out_path))
    result = json.loads(out_path.read_text())
    assert result == raw

# ---- test load_dataset ----
def test_load_dataset_csv():
    result = load_dataset("data/heo.csv")
    assert "read_csv" in result
    assert "heo.csv" in result

def test_load_dataset_unsupported():
    with pytest.raises(ValueError):
        load_dataset("data/heo.txt")

# --- test data type ---
TEST_ROW_CSV = """appid,name,header_image,website,release_date,is_free,price,currency,about_the_game,short_description,detailed_description,dlc_count,achievements,recommendations,windows,mac,linux,metacritic_score,metacritic_url,support_url,support_email,interface_languages,audio_languages,developers,publishers,category_ids,category_descriptions,genre_ids,genre_descriptions
30,Day of Defeat,https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/30/header.jpg?t=1745368580,http://www.dayofdefeat.com/,2003-05-01,False,"4.99",EUR,"Enlist in an intense brand of Axis vs. Allied teamplay set in the WWII European Theatre of Operations.","Enlist in an intense brand of Axis vs. Allied teamplay.","Enlist in an intense brand of Axis vs. Allied teamplay set in the WWII European Theatre of Operations.",0,0,4473,True,True,True,79,https://www.metacritic.com/game/pc/day-of-defeat?ftag=MCD-06-10aaa1f,,,"English, French, German, Italian, Spanish - Spain",,Valve,Valve,"1, 67, 66, 68, 69, 8, 62","Multi-player, Camera Comfort, Color Alternatives, Custom Volume Controls, Stereo Sound, Valve Anti-Cheat enabled, Family Sharing",1,Action"""

@pytest.fixture
def con():
    return duckdb.connect(":memory:")

def test_transform_price_cast_correctly(tmp_path, con):
    raw_file = tmp_path / "test_games.csv"
    raw_file.write_text(TEST_ROW_CSV)

    transform_data(con, raw_file.as_posix(), "test_games")

    result = con.execute("SELECT price FROM test_games").fetchone()[0]
    assert result == Decimal("4.99")


def test_transform_appid_cast_to_int(tmp_path, con):
    raw_file = tmp_path / "test_games.csv"
    raw_file.write_text(TEST_ROW_CSV)

    transform_data(con, raw_file.as_posix(), "test_games")

    result = con.execute("SELECT appid FROM test_games").fetchone()[0]
    assert result == 30
    assert isinstance(result, int)

def test_transform_release_date_cast_to_date(tmp_path, con):
    raw_file = tmp_path / "test_games.csv"
    raw_file.write_text(TEST_ROW_CSV)

    transform_data(con, raw_file.as_posix(), "test_games")

    result = con.execute("SELECT release_date FROM test_games").fetchone()[0]
    assert result == date(2003, 5, 1)

def test_transform_is_free_cast_to_boolean(tmp_path, con):
    raw_file = tmp_path / "test_games.csv"
    raw_file.write_text(TEST_ROW_CSV)

    transform_data(con, raw_file.as_posix(), "test_games")

    result = con.execute("SELECT is_free FROM test_games").fetchone()[0]
    assert result is False

def test_transform_metacritic_score_cast_to_smallint(tmp_path, con):
    raw_file = tmp_path / "test_games.csv"
    raw_file.write_text(TEST_ROW_CSV)

    transform_data(con, raw_file.as_posix(), "test_games")

    result = con.execute("SELECT metacritic_score FROM test_games").fetchone()[0]
    assert result == 79
    assert isinstance(result, int)

def test_transform_text_fields_trimmed(tmp_path, con):
    raw_file = tmp_path / "test_games.csv"
    raw_file.write_text(TEST_ROW_CSV)

    transform_data(con, raw_file.as_posix(), "test_games")

    result = con.execute("SELECT name FROM test_games").fetchone()[0]
    assert result == "Day of Defeat"
    assert result == result.strip() 


