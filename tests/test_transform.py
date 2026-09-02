
from decimal import Decimal

import duckdb
from transform import transform_data


def test_price_is_cast_to_decimal(tmp_path):

    # Create a small file csv
    raw_file = tmp_path / "test_games.csv"

    raw_file.write_text(
        """appid,name,header_image,website,release_date,is_free,price,currency,about_the_game,short_description,detailed_description,dlc_count,achievements,recommendations,windows,mac,linux,metacritic_score,metacritic_url,support_url,support_email,interface_languages,audio_languages,developers,publishers,category_ids,category_descriptions, genre_ids, genre_descriptions
620,"  Portal 2  ","https://example.com/portal2.jpg","https://store.steampowered.com/app/620/Portal_2/","2011-04-19","false","19.99","EUR","About Portal 2","A puzzle game","Detailed description of Portal 2","2","50","10000","true","true","true","95","https://example.com/metacritic/portal2","https://example.com/support","support@example.com","English, French, German","English","Valve","Valve","Single-player, Multi-player, Steam Achievements","1, 49, 36, 37, 66, 68, 75, 69, 8, 62","Multi-player, PvP, Online PvP, Shared/Split Screen PvP, Color Alternatives, Custom Volume Controls, Keyboard Only Option, Stereo Sound, Valve Anti-Cheat enabled, Family Sharing",1,Action
570,"Dota 2","https://example.com/dota2.jpg","","2013-07-09","true","0","EUR","About Dota 2","A strategy game","Detailed description of Dota 2","0","100","50000","true","false","true","90","https://example.com/metacritic/dota2","","","English, Russian, Chinese","English, Russian","Valve","Valve","Multi-player, Steam Achievements","Action, Strategy", "English, French, German","English","Valve","Valve","Single-player, Multi-player, Steam Achievements","1, 49, 36, 37, 66, 68, 75, 69, 8, 62","Multi-player, PvP, Online PvP, Shared/Split Screen PvP, Color Alternatives, Custom Volume Controls, Keyboard Only Option, Stereo Sound, Valve Anti-Cheat enabled, Family Sharing",1,Action
"""

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

    # Check if result is 19.99
    assert result == Decimal("19.99")

