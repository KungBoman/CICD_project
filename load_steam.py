import csv
import json


# Skapa en funktion som får sökvägen/namnet till en JSON-fil.
# Öppna filen för läsning. r=read.
# Läs JSON-Innehållet och omvandla det till python-data, och skicka tillbaka det. 

def load_json_data(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        return json.load(file)


def write_csv(rows, output_file):
    # Om listan är tom ska funktionen avslutas. Annars hade rows[0] kraschat.
    if not rows:
        return
    # Tar kolumnnamnen från första spelet.
    fieldnames = rows[0].keys()
    # Öppnar eller skapar output-filen för skrivning
    # "w" = Write. Finns filen redan skrivs den över.
    # newline="", används för att csv.modulen själv ska hantera radbytningarna korrekt.
    # encoding="urf-8", gör att text och specieltecken kan sparas korrekt.
    with open(output_file, "w", newline="", encoding="utf-8",) as file:
        # skapar själva csv.skrivare
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Skriver kolumnnamnen och datan under kolumnerna. 
        writer.writeheader()
        writer.writerows(rows)


def load_data(input_file, output_file):
    data = load_json_data(input_file)
    rows = list(data.values())
    write_csv(rows, output_file) 




load_data("test_games.json", "games.csv")
# load_data(test_data, "games.csv")