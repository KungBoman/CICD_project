## Data Source

- **API**: [Steam Web API — IStoreService](https://steamapi.xpaw.me/IStoreService)
- **Ingestion pattern**: cursor-based pagination (`last_appid`), with retry + exponential backoff and incremental sync support via `if_modified_since`.

## Final Table Schema (Silver Layer)

| Column Name | Data Type | Description |
|---|---|---|
| `appid` | `INT` | Unique identifier for the application/game on Steam. Primary key of the table. |
| `name` | `STRING` | Official display name of the app as shown on the Steam store page. |
| `header_image` | `STRING` | URL to the store page's header/banner image (used for thumbnails in UI or reports). |
| `website` | `STRING` | Official external website URL for the game, if the developer provided one. |
| `release_date` | `DATE` | Date the app was (or will be) released on Steam. May be null/future for unreleased titles. |
| `is_free` | `BOOLEAN` | Whether the app is free-to-play (`true`) or requires purchase (`false`). |
| `price` | `DECIMAL` | Current listed price of the app in the given `currency`, before any discount. Null when `is_free = true`. |
| `currency` | `STRING` | ISO currency code (e.g. `USD`, `EUR`) that `price` is denominated in — depends on the storefront region used when fetching. |
| `about_the_game` | `STRING` | Long-form marketing/HTML description of the game (extended content, may include formatting tags). |
| `short_description` | `STRING` | One- to two-sentence summary of the game, used in search results and previews. |
| `detailed_description` | `STRING` | Full store-page description, typically the longest and most complete text field (superset of `about_the_game`). |
| `dlc_count` | `INT` | Number of downloadable content (DLC) packages associated with this base app. |
| `achievements` | `INT` | Total number of Steam achievements defined for the app. |
| `recommendations` | `INT` | Total count of user recommendations ("this game is recommended") — a popularity/engagement signal. |
| `windows` | `BOOLEAN` | Whether the app supports the Windows platform. |
| `mac` | `BOOLEAN` | Whether the app supports macOS. |
| `linux` | `BOOLEAN` | Whether the app supports Linux/SteamOS. |
| `metacritic_score` | `SMALLINT` | Aggregated critic score from Metacritic (0–100 scale). Null if the app has no Metacritic entry. |
| `metacritic_url` | `STRING` | Link to the app's Metacritic review page, when a score exists. |
| `support_url` | `STRING` | URL to the developer/publisher's official support page. |
| `support_email` | `STRING` | Contact email address for user support requests. |
| `supported_languages` | `STRING` | Comma-/HTML-delimited list of languages the game's interface and/or subtitles support. |
| `full_audio_languages` | `STRING` | Subset of `supported_languages` that also have full voice-over audio support. |
| `developers` | `STRING` | Name(s) of the studio(s) that developed the game. Multiple values may be comma-separated. |
| `publishers` | `STRING` | Name(s) of the publisher(s) responsible for distributing the game. |
| `categories` | `STRING` | Steam feature tags describing gameplay mechanics/platform features (e.g. "Single-player", "Multi-player", "Steam Achievements"). |
| `genres` | `STRING` | Genre classification(s) assigned by the store (e.g. "Action", "RPG", "Indie"). |

### Notes on schema decisions

- **`price` / `currency`**: values depend on the storefront region used at fetch time. If data is collected across multiple regions, standardize to a single currency during the Silver transform to avoid inconsistent aggregates.
- **`categories`, `genres`, `supported_languages`**: stored as denormalized strings in Bronze/Silver. Consider normalizing into separate mapping tables (or array/JSON columns) in the Gold layer depending on query patterns.
- **`about_the_game` vs `detailed_description`**: these often overlap significantly. Evaluate whether both are needed in Gold, or drop one to reduce storage.
