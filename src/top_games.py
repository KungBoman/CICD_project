from database_connection import engine
from sqlalchemy import text

TABLE_NAME = "top_lists"

def create_top_games():
    create_and_load = [
    "DROP TABLE IF EXISTS top_lists;",
    """CREATE TABLE IF NOT EXISTS top_lists(
        list_type TEXT,
        rank INT,
        appid INT REFERENCES games_applications(appid),
        PRIMARY KEY(list_type, rank)
    );""",

    """-- 1. Most appealing: high rating + sufficient reliability (many reviews)
    INSERT INTO top_lists (list_type, rank, appid)
    SELECT 'most_appealing', ROW_NUMBER() OVER (ORDER BY metacritic_score DESC, recommendations DESC), appid
    FROM games_applications
    WHERE metacritic_score IS NOT NULL AND recommendations >= 50
    ORDER BY metacritic_score DESC, recommendations DESC
    LIMIT 10;""",

    """-- 2. Best value: highest rating/price ratio (excluding free games as there is no "price" to compare ratios)
    INSERT INTO top_lists (list_type, rank, appid)
    SELECT 'best_value', ROW_NUMBER() OVER (ORDER BY (metacritic_score / price) DESC), appid
    FROM games_applications
    WHERE is_free = false AND price > 0 AND metacritic_score IS NOT NULL AND recommendations >= 50
    ORDER BY (metacritic_score / price) DESC
    LIMIT 10;""",

    """-- 3. Best free games
    -- Postgres considers NULL to be the largest when sorting DESC, 
    -- so rows with metacritic_score = NULL will be pushed to the top of the list
    -- NULLS LAST forces NULL rows to the bottom, whether DESC or ASC is being sorted
    INSERT INTO top_lists (list_type, rank, appid)
    SELECT 'best_free', ROW_NUMBER() OVER (ORDER BY recommendations DESC NULLS LAST, metacritic_score DESC NULLS LAST), appid
    FROM games_applications
    WHERE is_free = true AND recommendations > 0
    ORDER BY recommendations DESC NULLS LAST, metacritic_score DESC NULLS LAST
    LIMIT 10;""",

    """-- 4. To avoid (proxy: lowest rating in the reliable group)
    INSERT INTO top_lists (list_type, rank, appid)
    SELECT 'to_avoid', ROW_NUMBER() OVER (ORDER BY metacritic_score ASC), appid
    FROM games_applications
    WHERE metacritic_score IS NOT NULL AND recommendations >= 50
    ORDER BY metacritic_score ASC
    LIMIT 10;""",
]

    with engine.connect() as conn:
        for statement in create_and_load:
            conn.execute(text(statement))
        conn.commit()
        print(f"Create table {TABLE_NAME} successfully")

if __name__ == "__main__":
    create_top_games()
