
import os
import json
import sys

CONFIG_FILE = "env/.cfg"
ENCODING = "utf-8"


def log(type, msg):
    print(f"[{type}] {msg}")


def get_steam_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding=ENCODING) as file:
            for line in file:
                line = line.strip()

                if line.startswith("STEAM_API_KEY="):
                    return line.split("=", 1)[1]

    log("ERROR", f"Configuration file '{CONFIG_FILE}' not found.")
    sys.exit(1)


def load_json(filename) -> dict:
    if not os.path.exists(filename):
        return {}

    with open(filename, "r", encoding=ENCODING) as file:
        return json.load(file)


def save_json(data, filename):
    with open(filename, "w", encoding=ENCODING) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )
