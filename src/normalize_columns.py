from sqlalchemy import text

from database_connection import engine


def normalize_multivalue_columns():
    create_and_load_data = ["""
    DROP TABLE IF EXISTS developers CASCADE;
    -- Dim tables: developers/publishers, create id
    CREATE TABLE IF NOT EXISTS developers (
        developer_id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );

    DROP TABLE IF EXISTS publishers CASCADE;
    CREATE TABLE IF NOT EXISTS publishers (
        publisher_id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );

    DROP TABLE IF EXISTS categories CASCADE;
    -- Dim tables: categories/genres using ID from games_applications
    CREATE TABLE IF NOT EXISTS categories (
        category_id INT PRIMARY KEY,
        description TEXT
    );

    DROP TABLE IF EXISTS genres CASCADE;
    CREATE TABLE IF NOT EXISTS genres (
        genre_id INT PRIMARY KEY,
        description TEXT
    );

    DROP TABLE IF EXISTS game_developers CASCADE;
    -- Junction tables: relationship many to many
    CREATE TABLE IF NOT EXISTS game_developers (
        appid INT REFERENCES games_applications(appid),
        developer_id INT REFERENCES developers(developer_id),
        PRIMARY KEY (appid, developer_id)
    );

    DROP TABLE IF EXISTS game_publishers CASCADE;
    CREATE TABLE IF NOT EXISTS game_publishers (
        appid INT REFERENCES games_applications(appid),
        publisher_id INT REFERENCES publishers(publisher_id),
        PRIMARY KEY (appid, publisher_id)
    );

    DROP TABLE IF EXISTS game_categories CASCADE;
    CREATE TABLE IF NOT EXISTS game_categories (
        appid INT REFERENCES games_applications(appid),
        category_id INT REFERENCES categories(category_id),
        PRIMARY KEY (appid, category_id)
    );

    DROP TABLE IF EXISTS game_genres CASCADE;
    CREATE TABLE IF NOT EXISTS game_genres (
        appid INT REFERENCES games_applications(appid),
        genre_id INT REFERENCES genres(genre_id),
        PRIMARY KEY (appid, genre_id)
    );

    -- Load the dim table developers (split strings, extract unique values)
    INSERT INTO developers (name)
    SELECT DISTINCT TRIM(unnest(string_to_array(developers, ',')))
    FROM games_applications
    WHERE developers IS NOT NULL
    ON CONFLICT (name) DO NOTHING;

    -- Load the junction table game_developers
    INSERT INTO game_developers (appid, developer_id)
    SELECT g.appid, d.developer_id
    FROM games_applications g
    CROSS JOIN LATERAL unnest(string_to_array(g.developers, ',')) AS dev_name
    JOIN developers d ON TRIM(dev_name) = d.name
    WHERE g.developers IS NOT NULL
    ON CONFLICT DO NOTHING;

    INSERT INTO publishers (name)
    SELECT DISTINCT TRIM(unnest(string_to_array(publishers, ',')))
    FROM games_applications
    WHERE publishers IS NOT NULL
    ON CONFLICT (name) DO NOTHING;

    INSERT INTO game_publishers (appid, publisher_id)
    SELECT g.appid, p.publisher_id
    FROM games_applications g
    CROSS JOIN LATERAL unnest(string_to_array(g.publishers, ',')) AS pub_name
    JOIN publishers p ON TRIM(pub_name) = p.name
    WHERE g.publishers IS NOT NULL
    ON CONFLICT DO NOTHING;

    -- use WITH ORDINALITY to pair ids with descriptions in the correct positions
    INSERT INTO categories (category_id, description)
    SELECT DISTINCT CAST(CAST(ids.val AS numeric) AS int), TRIM(descs.val)
    FROM games_applications g
    CROSS JOIN LATERAL unnest(string_to_array(g.category_ids, ',')) WITH ORDINALITY AS ids(val, ord)
    CROSS JOIN LATERAL unnest(string_to_array(g.category_descriptions, ',')) WITH ORDINALITY AS descs(val, ord2)
    WHERE ids.ord = descs.ord2 AND g.category_ids IS NOT NULL
    ON CONFLICT (category_id) DO NOTHING;

    INSERT INTO game_categories (appid, category_id)
    SELECT DISTINCT g.appid, CAST(CAST(ids.val AS numeric) AS int)
    FROM games_applications g
    CROSS JOIN LATERAL unnest(string_to_array(g.category_ids, ',')) AS ids(val)
    WHERE g.category_ids IS NOT NULL
    ON CONFLICT DO NOTHING;

    INSERT INTO genres (genre_id, description)
    SELECT DISTINCT CAST(CAST(ids.val AS numeric) AS int), TRIM(descs.val)
    FROM games_applications g
    CROSS JOIN LATERAL unnest(string_to_array(g.genre_ids, ',')) WITH ORDINALITY AS ids(val, ord)
    CROSS JOIN LATERAL unnest(string_to_array(g.genre_descriptions, ',')) WITH ORDINALITY AS descs(val, ord2)
    WHERE ids.ord = descs.ord2 AND g.genre_ids IS NOT NULL
    ON CONFLICT (genre_id) DO NOTHING;

    INSERT INTO game_genres (appid, genre_id)
    SELECT DISTINCT g.appid, CAST(CAST(ids.val AS numeric) AS int)
    FROM games_applications g
    CROSS JOIN LATERAL unnest(string_to_array(g.genre_ids, ',')) AS ids(val)
    WHERE g.genre_ids IS NOT NULL
    ON CONFLICT DO NOTHING;
    """]

    with engine.connect() as conn:
        for statement in create_and_load_data:
            conn.execute(text(statement))
        conn.commit()
    print("Normalized developers/publishers/categories/genres successfully")

if __name__ == "__main__":
    normalize_multivalue_columns()