# Fetch App List

`fetch_app_list.py` fetches the list of applications available through the Steam Web API and stores it locally as `app_list.json`.

The resulting list contains the Steam AppID and application name for each application.

## Example output

```json
[
    {
        "appid": 10,
        "name": "Counter-Strike"
    },
    {
        "appid": 20,
        "name": "Team Fortress Classic"
    },
    {
        "appid": 30,
        "name": "Day of Defeat"
    }
]
```

## Usage

Prepare a Steam API key as envorinment variable:
```bash
export STEAM_API_KEY=YOURSECRETKEY
```

Fetch the complete application list:

```bash
python fetch_app_list.py
```

Fetch only a limited number of applications:

```bash
python fetch_app_list.py -m 1000
```

## Arguments

| Short | Long | Description |
|---|---|---|
| `-m` | `--max-apps` | Maximum number of applications to fetch. If omitted, all applications are fetched. |

## API

The script uses the Steam Web API:

```text
IStoreService/GetAppList/v1/
```

A Steam Web API key is required.

The API returns applications in batches. The script continues requesting batches until there are no more results or the requested maximum number of applications has been reached.

## Output

The application list is saved to:

```text
app_list.json
```

Each entry contains:

- `appid` — Steam application ID
- `name` — Application name

This file is used as input by `build_dataset.py`.

## Testing

Run the complete test suite:

```bash
pytest
```

Or run the tests with verbose output:

```bash
pytest -v
```