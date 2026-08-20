
from logging import INFO
import os
import json
import sys
import time

CONFIG_FILE = ".cfg"
ENCODING = "utf-8"
DEFAULT_DATASET_FILE = "games_dataset.json"

def Log(type, msg):
    print(f"[{type}] {msg}")

def get_steam_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            for line in file:
                if line.startswith("STEAM_API_KEY="):
                    return line.strip().split("=")[1]
    else:
        Log("ERROR", f"Configuration file '{CONFIG_FILE}' not found.")
        sys.exit(1)
    return None

def load_json(filename) -> dict:
    if not os.path.exists(filename):
        return {}
    with open(filename, "r", encoding=ENCODING) as file:
        return json.load(file)


def save_json(data, filename):
    with open(filename, "w", encoding=ENCODING) as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    Log("INFO", "Starting GamesScraper.py")

    steam_api_key = get_steam_api_key()
    if not steam_api_key:
        Log("INFO", f"Steam API Key invalid: {steam_api_key}")
        sys.exit(1)

    dataset = load_json(DEFAULT_DATASET_FILE)
    if not dataset:
        Log("INFO", f"No data found in '{DEFAULT_DATASET_FILE}'. Starting with an empty dataset.")
        dataset = {}
    else:
        Log("INFO", f"Loaded dataset from '{DEFAULT_DATASET_FILE}' with {len(dataset)} entries.")

    start_time = time.time()

   # TODO: Do stuff to get the data

    end_time = time.time()
    duration = end_time - start_time
    Log("INFO", f"Data fetching completed in {duration:.2f} seconds.")

    save_json(dataset, DEFAULT_DATASET_FILE)
    Log("INFO", f"Dataset saved to '{DEFAULT_DATASET_FILE}' with {len(dataset)} entries.")

    
