# Steam Game Dataset Builder

Fetches game information from the Steam Store API and builds a local dataset.

The script reads a Steam app list, fetches details for each application, and stores the resulting game data as either JSON or CSV.

## Usage

```bash
python build_dataset.py
```

By default, the script reads from `games_dataset.json` and writes to `games_dataset.json`.

### Example

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

## Arguments

| Short | Long | Description |
|---|---|---|
| `-i` | `--infile` | Input dataset filename. Supports `.json` and `.csv`. |
| `-o` | `--outfile` | Output dataset filename. Supports `.json` and `.csv`. |
| `-m` | `--max-apps` | Maximum number of apps to fetch. |
| `-c` | `--country` | Steam store country code. |
| `-l` | `--language` | Steam store language code. |
| `-d` | `--delay` | Delay in seconds between requests. |
| `-r` | `--retries` | Maximum number of retries after a rate limit. |
| `-rd` | `--retry-delay` | Initial delay in seconds before retrying. |
| | `--incremental-retry-delay` | Increment the retry delay after each failed retry. |
| | `--sanitize-text` | Remove HTML tags and formatting codes from text fields. |
| `-f` | `--force` | Re-fetch apps that already exist in the dataset. |

## Dataset

Each game contains information such as:

- Steam AppID
- Name
- Release date
- Free-to-play status
- Price and currency
- Game descriptions
- DLC count
- Achievement count
- Recommendation count
- Supported platforms
- Metacritic score and URL

## Input

The script expects an `app_list.json` containing Steam applications, for example:

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

The app list can be generated separately using the project's app-list fetching script.

## Output formats

The output format is determined by the file extension:

```text
games_dataset.json
games_dataset.csv
```

JSON preserves the dataset structure directly, while CSV stores the games as rows.
### Example
``` json
{
    "10": {
        "appid": 10,
        "name": "Counter-Strike",
        "release_date": "2000-11-01",
        "is_free": false,
        "price": 8.19,
        "currency": "EUR",
        "about_the_game": "Play the world's number 1 online action game.",
        "short_description": "Play the world's number 1 online action game.",
        "detailed_description": "Play the world's number 1 online action game.",
        "dlc_count": 0,
        "achievements": 0,
        "recommendations": 169557,
        "windows": true,
        "mac": true,
        "linux": true,
        "metacritic_score": 88,
        "metacritic_url": "https://www.metacritic.com/game/pc/counter-strike?ftag=MCD-06-10aaa1f"
    }
}
```

## Rate limiting

The Steam Store API has rate limits. The script supports:

- A configurable delay between requests
- Automatic retries when receiving HTTP `429 Too Many Requests`
- Configurable retry delay
- Optional incremental retry delays

For example:

```bash
python build_dataset.py -d 1 -r 4 -rd 10 --incremental-retry-delay true
```

This waits one second between normal requests and retries rate-limited requests with an increasing delay.

## Tests

Run the test suite with:

```bash
pytest
```

Or run it with more verbose output:

```bash
pytest -v
```