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
        "appid": 450,
        "name": "GTA 6",
        "playtime_hours": 15.5
    },
    {
        "appid": 422,
        "name": "call of duty",
        "playtime_hours": 14.6
    }
]

load_data(test_data)