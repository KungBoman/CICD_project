from database_connection import run_query
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Steam Games API")

# get all games, 20 games/time, change offset to get other games
@app.get("/games")
# set validation, works when 1 < limit < 100, no negative values
def list_games( limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)): 
    try:
        games = run_query("SELECT * FROM games_applications LIMIT :limit OFFSET :offset", 
                        {"limit": limit, "offset": offset})
        return games
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

# get free games, move this up becase that static routes must always be placed before dynamic routes like games/{appid}
@app.get("/games/free")
def get_free_games(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    try:
        games = run_query("SELECT * FROM games_applications WHERE is_free = TRUE LIMIT :limit OFFSET :offset",
                         {"limit": limit, "offset": offset}) 
        return games
    
    except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

# get windows games     
@app.get("/games/platform/windows")
def search_windows_games(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
     try:
        games = run_query("SELECT * FROM games_applications WHERE windows = TRUE LIMIT :limit OFFSET :offset",
                         {"limit": limit, "offset": offset})
        return games
     except RuntimeError as e:
             raise HTTPException(status_code=500, detail=str(e))

# get mac games
@app.get("/games/platform/mac")
def search_mac_games(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
     try:
        games = run_query("SELECT * FROM games_applications WHERE mac = TRUE LIMIT :limit OFFSET :offset",
                         {"limit": limit, "offset": offset})
        return games
     except RuntimeError as e:
             raise HTTPException(status_code=500, detail=str(e))

# get linux games
@app.get("/games/platform/linux")
def search_linux_games(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
     try:
        games = run_query("SELECT * FROM games_applications WHERE linux = TRUE LIMIT :limit OFFSET :offset",
                         {"limit": limit, "offset": offset})
        return games
     except RuntimeError as e:
             raise HTTPException(status_code=500, detail=str(e))

# @app.get("/games/genres/{genre}")
# def search_games_with_genres():
#      try:
#         games = run_query("SELECT a.name, a.header_image, a FROM ")


# get games info with their name
@app.get("/games/search")
def search_games(name: str):
    try:
        games = run_query("SELECT * FROM games_applications WHERE name ILIKE :name",
                        {"name": f"%{name}%"})
        if not games:
            raise HTTPException(status_code=404, detail="Game not found")
        return games
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# get game info with their id
@app.get("/games/{appid}")
def find_game_with_id(appid:int):
    try:
        games = run_query("SELECT * FROM games_applications WHERE appid = :appid",
                         {"appid": appid})
        if not games:
            raise HTTPException(status_code=404, detail="Game not found")
        game = games[0]
        trailer = run_query("SELECT trailer_url FROM game_trailers WHERE appid = :appid", {"appid": appid})
        game["trailer_url"] = trailer[0]["trailer_url"] if trailer else None

        return game
    except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

            
     

    




    

