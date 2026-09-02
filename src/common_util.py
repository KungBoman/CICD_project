
import argparse
import csv
import json
import os
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
DATA_DIR = ROOT / "data"

ENCODING = "utf-8"


def log(type, msg):
    print(f"[{type}] {msg}")


def get_steam_api_key():
    api_key = os.getenv("STEAM_API_KEY")

    if api_key:
        return api_key

    log("ERROR", "Environment variable 'STEAM_API_KEY' not found.")
    sys.exit(1)


def load_json(filename) -> dict:
    if not os.path.exists(DATA_DIR / filename):
        return {}

    with open(DATA_DIR / filename, "r", encoding=ENCODING) as file:
        return json.load(file)


def save_json(data, filename):
    if not data:
        return

    with open(DATA_DIR / filename, "w", encoding=ENCODING) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_csv(filename: str, key=None) -> list | dict:
    if not os.path.exists(DATA_DIR / filename):
        return {}

    with open(DATA_DIR / filename, "r", encoding=ENCODING, newline="") as file:
        reader = csv.DictReader(file)

        if key is None:
            return list(reader)

        # TODO: Handle KeyError when the specified key is missing from CSV
        return {
            row[key]: row
            for row in reader
        }


def save_csv(data: list | dict, filename: str):
    if not data:
        return

    if isinstance(data, dict):
        data_rows = data.values()
    else:
        data_rows = data

    data_rows = list(data_rows)
    fieldnames = data_rows[0].keys()

    with open(DATA_DIR / filename, "w", encoding=ENCODING, newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)


def str_to_bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
