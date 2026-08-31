
from decimal import Decimal

import duckdb

from transform import transform_data


def test_price_is_cast_to_decimal(tmp_path):

    # Create a small file csv
    raw_file = tmp_path / "test_games.csv"

    raw_file.write_text(
        """appid,name,header_image,website,release_date,is_free,price,currency,about_the_game,short_description,detailed_description,dlc_count,achievements,recommendations,windows,mac,linux,metacritic_score,metacritic_url,support_url,support_email,supported_languages,full_audio_languages,developers,publishers,categories,genres
620,"  Portal 2  ","https://example.com/portal2.jpg","https://store.steampowered.com/app/620/Portal_2/","2011-04-19","false","19.99","EUR","About Portal 2","A puzzle game","Detailed description of Portal 2","2","50","10000","true","true","true","95","https://example.com/metacritic/portal2","https://example.com/support","support@example.com","English, French, German","English","Valve","Valve","Single-player, Multi-player, Steam Achievements","Action, Adventure"
570,"Dota 2","https://example.com/dota2.jpg","","2013-07-09","true","0","EUR","About Dota 2","A strategy game","Detailed description of Dota 2","0","100","50000","true","false","true","90","https://example.com/metacritic/dota2","","","English, Russian, Chinese","English, Russian","Valve","Valve","Multi-player, Steam Achievements","Action, Strategy"
999999,"Test Game"," https://example.com/test.jpg ","https://example.com/test","2026-01-01","false","abc","SEK","About Test Game","Test description","Detailed description","not_a_number","-5","abc","TRUE","FALSE","TRUE","101","not_a_url"," https://example.com/support ","test@example.com"," English , Swedish , English ","Swedish"," Test Developer "," Test Publisher ","Single-player","Indie"
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

