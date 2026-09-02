"""
Persistent ignore list for Steam appids.

Example:
{
    "12345": {
        "reason": "steam_success_false",
        "first_seen": "2026-08-31",
        "last_seen": "2026-09-01"
    }
}
"""

from datetime import date

import common_util as cu

IGNORE_FILE = "ignored_appids.json"


def load_ignore_list() -> dict:
    """Load ignored appids from disk."""
    data = cu.load_json(IGNORE_FILE)

    if not isinstance(data, dict):
        return {}

    return data


def save_ignore_list(ignored_appids: dict) -> None:
    """Save ignored appids to disk."""
    cu.save_json(ignored_appids, IGNORE_FILE)


def add(
    ignored_appids: dict,
    appid: int,
    reason: str,
) -> None:
    """Add an appid to the ignore list or update its last_seen date."""

    appid = str(appid)
    today = date.today().isoformat()

    if appid in ignored_appids:
        ignored_appids[appid]["last_seen"] = today

        # Keep the original reason unless explicitly changed.
        if reason:
            ignored_appids[appid]["reason"] = reason

        return

    ignored_appids[appid] = {
        "reason": reason,
        "first_seen": today,
        "last_seen": today,
    }


def remove(ignored_appids: dict, appid: int) -> bool:
    """Remove an appid from the ignore list.

    Returns True if the appid existed and was removed.
    """
    appid = str(appid)

    if appid not in ignored_appids:
        return False

    del ignored_appids[appid]
    return True


def is_ignored(ignored_appids: dict, appid: int) -> bool:
    """Return True if the appid is ignored."""
    return str(appid) in ignored_appids


def get_reason(ignored_appids: dict, appid: int) -> str | None:
    """Return the ignore reason for an appid."""
    entry = ignored_appids.get(str(appid))

    if entry is None:
        return None

    return entry.get("reason")


def count(ignored_appids: dict) -> int:
    """Return total number of ignored appids."""
    return len(ignored_appids)


def count_by_reason(ignored_appids: dict) -> dict:
    """Return number of ignored apps grouped by reason."""

    result = {}

    for entry in ignored_appids.values():
        reason = entry.get("reason", "unknown")
        result[reason] = result.get(reason, 0) + 1

    return dict(sorted(result.items()))


def get_by_reason(ignored_appids: dict, reason: str) -> list[int]:
    """Return all appids with a specific ignore reason."""

    return [
        int(appid)
        for appid, entry in ignored_appids.items()
        if entry.get("reason") == reason
    ]


def print_analysis(ignored_appids: dict) -> None:
    """Print a simple analysis of the ignore list."""

    cu.log(
        "INFO",
        f"Ignored apps: {count(ignored_appids)}"
    )

    for reason, amount in count_by_reason(ignored_appids).items():
        cu.log(
            "INFO",
            f"  {reason}: {amount}"
        )


def save(ignored_appids: dict) -> None:
    """Convenience function for saving the current ignore list."""
    save_ignore_list(ignored_appids)
