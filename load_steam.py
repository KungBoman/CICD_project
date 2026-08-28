import csv
import json


# Skapa en funktion som får sökvägen/namnet till en JSON-fil.
# Öppna filen för läsning. r=read.
# Läs JSON-Innehållet och omvandla det till python-data, och skicka tillbaka det. 

def load_json_data(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        return json.load(file)



def load_data(data):
    print(data) 


test_data = [
    {
        "appid": 10,
        "name": "Counter-Strike",
        "is_free": False,
        "price": 8.19,
        "currency": "EUR",
        "windows": True,
        "mac": True,
        "linux": True,
        "metacritic_score": 88
    },
    {
        "appid": 20,
        "name": "Team Fortress Classic",
        "is_free": False,
        "price": 4.99,
        "currency": "EUR",
        "windows": True,
        "mac": False,
        "linux": True,
        "metacritic_score": 76
    }
]

load_data(test_data)