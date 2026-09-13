import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load information from the .env file.
load_dotenv(override=True)

# Get connection information 
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "steam_games")

# create connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TABLE_NAME = "games_applications"

# Create an engine for connection
engine = create_engine(DATABASE_URL) 

def run_query(query: str, params: dict | None = None):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Database error: {e}")