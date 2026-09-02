
from decimal import Decimal

import duckdb
from transform import transform_data


def test_price_is_cast_to_decimal(tmp_path):

    # Create a small file csv
    raw_file = tmp_path / "test_games.csv"

    raw_file.write_text(
        """appid,name,header_image,website,release_date,is_free,price,currency,about_the_game,short_description,detailed_description,dlc_count,achievements,recommendations,windows,mac,linux,metacritic_score,metacritic_url,support_url,support_email,interface_languages,audio_languages,developers,publishers,category_ids,category_descriptions,genre_ids,genre_descriptions
30,Day of Defeat,https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/30/header.jpg?t=1745368580,http://www.dayofdefeat.com/,2003-05-01,False,"4.99",EUR,"Enlist in an intense brand of Axis vs. Allied teamplay set in the WWII European Theatre of Operations. Players assume the role of light/assault/heavy infantry, sniper or machine-gunner class, each with a unique arsenal of historical weaponry at their disposal. Missions are based on key historical operations. And, as war rages, players must work together with their squad to accomplish a variety of mission-specific objectives.","Enlist in an intense brand of Axis vs. Allied teamplay set in the WWII European Theatre of Operations. Players assume the role of light/assault/heavy infantry, sniper or machine-gunner class, each with a unique arsenal of historical weaponry at their disposal. Missions are based on key historical operations.","Enlist in an intense brand of Axis vs. Allied teamplay set in the WWII European Theatre of Operations. Players assume the role of light/assault/heavy infantry, sniper or machine-gunner class, each with a unique arsenal of historical weaponry at their disposal. Missions are based on key historical operations. And, as war rages, players must work together with their squad to accomplish a variety of mission-specific objectives.",0,0,4473,True,True,True,79,https://www.metacritic.com/game/pc/day-of-defeat?ftag=MCD-06-10aaa1f,,,"English, French, German, Italian, Spanish - Spain",,Valve,Valve,"1, 67, 66, 68, 69, 8, 62","Multi-player, Camera Comfort, Color Alternatives, Custom Volume Controls, Stereo Sound, Valve Anti-Cheat enabled, Family Sharing",1,Action"""

    )

    # Create a temporary database 
    con = duckdb.connect(":memory:")

    # Run transform function
    transform_data(
        con,
        raw_file.as_posix(),
        "test_games"
    )

    # Get price from test_game
    result = con.execute(
            "SELECT price FROM test_games"
            ).fetchone()[0]

    assert result == Decimal("4.99")

