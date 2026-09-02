# Steam Game Dataset Builder

Fetches game information from the Steam Store API and builds a local dataset.

The script reads a Steam app list, fetches details for each application, and stores the resulting game data as either JSON or CSV.

Existing applications are skipped by default, allowing the script to resume an interrupted run. Use `--force` to fetch them again.

## Usage

```bash
python build_dataset.py
```

By default, the script reads from `games_dataset.json` and writes to `games_dataset.json`.

### Examples

Fetch the first 1000 apps:

```bash
python build_dataset.py -m 1000
```

Use a CSV dataset:

```bash
python build_dataset.py -i games_dataset.csv -o games_dataset.csv
```

Force existing apps to be fetched again:

```bash
python build_dataset.py -f true
```

Add a delay between requests:

```bash
python build_dataset.py -d 1
```

## Arguments

| Short | Long | Description |
|---|---|---|
| `-i` | `--infile` | Input dataset filename. Supports `.json` and `.csv`. |
| `-o` | `--outfile` | Output dataset filename. Supports `.json` and `.csv`. |
| `-m` | `--max-apps` | Maximum number of apps to fetch. |
| `-c` | `--country` | Steam Store country code. |
| `-l` | `--language` | Steam Store language code. |
| `-d` | `--delay` | Delay in seconds between requests. |
| `-r` | `--retries` | Maximum number of retries after a rate limit. |
| `-rd` | `--retry-delay` | Initial delay in seconds before retrying. |
| | `--incremental-retry-delay` | Increment the retry delay after each failed retry. |
| | `--sanitize-text` | Remove HTML tags and formatting codes from text fields. |
| `-f` | `--force` | Re-fetch apps that already exist in the dataset. |

## Input

The script expects an `app_list.json` containing Steam applications.

Example:

```json
[
    {
        "appid": 10,
        "name": "Counter-Strike"
    },
    {
        "appid": 20,
        "name": "Team Fortress Classic"
    }
]
```

The app list can be generated using `fetch_app_list.py`.

## Output

The output format is determined by the file extension.

```text
games_dataset.json
games_dataset.csv
```

JSON preserves the dataset structure directly*, while CSV stores each game as a row. 
###### *\* Not true at the moment.*

### Example

```json
{
    "10": {
        "appid": 10,
        "name": "Counter-Strike",
        "header_image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/10/header.jpg?t=1745368572",
        "website": null,
        "release_date": "2000-11-01",
        "is_free": false,
        "price": 8.19,
        "currency": "EUR",
        "about_the_game": "Play the world's number 1 online action game. Engage in an incredibly realistic brand of terrorist warfare in this wildly popular team-based game. Ally with teammates to complete strategic missions. Take out enemy sites. Rescue hostages. Your role affects your team's success. Your team's success affects your role.",
        "short_description": "Play the world's number 1 online action game. Engage in an incredibly realistic brand of terrorist warfare in this wildly popular team-based game. Ally with teammates to complete strategic missions. Take out enemy sites. Rescue hostages. Your role affects your team's success. Your team's success affects your role.",
        "detailed_description": "Play the world's number 1 online action game. Engage in an incredibly realistic brand of terrorist warfare in this wildly popular team-based game. Ally with teammates to complete strategic missions. Take out enemy sites. Rescue hostages. Your role affects your team's success. Your team's success affects your role.",
        "dlc_count": 0,
        "achievements": 0,
        "recommendations": 169576,
        "windows": true,
        "mac": true,
        "linux": true,
        "metacritic_score": 88,
        "metacritic_url": "https://www.metacritic.com/game/pc/counter-strike?ftag=MCD-06-10aaa1f",
        "support_url": "http://steamcommunity.com/app/10",
        "support_email": "",
        "interface_languages": "English, French, German, Italian, Spanish - Spain, Simplified Chinese, Traditional Chinese, Korean",
        "audio_languages": "English, French, German, Italian, Spanish - Spain, Simplified Chinese, Traditional Chinese, Korean",
        "developers": "Valve",
        "publishers": "Valve",
        "category_ids": "1, 49, 36, 37, 66, 68, 75, 69, 8, 62",
        "category_descriptions": "Multi-player, PvP, Online PvP, Shared/Split Screen PvP, Color Alternatives, Custom Volume Controls, Keyboard Only Option, Stereo Sound, Valve Anti-Cheat enabled, Family Sharing",
        "genre_ids": "1",
        "genre_descriptions": "Action"
    }
}
```

## Rate Limiting

The Steam Store API has rate limits. The script supports:

- A configurable delay between requests
- Automatic retries when receiving HTTP `429 Too Many Requests`
- Configurable retry delay
- Optional incremental retry delays

For example:

```bash
python build_dataset.py -d 1.5 -r 4 -rd 10 --incremental-retry-delay true
```

This waits one second between normal requests and retries rate-limited requests with an increasing delay. This allows the script to make efficient use of the API's rate limit while reducing the risk of repeated rate limiting.

## Text Sanitization

Steam descriptions may contain HTML tags, BBCode, and other formatting.

Text sanitization can be enabled with:

```bash
python build_dataset.py --sanitize-text true
```

When enabled, supported formatting and HTML markup are removed from text fields before they are stored in the dataset.

## Tests

Run the test suite with:

```bash
pytest
```

Or run it with verbose output:

```bash
pytest -v
```