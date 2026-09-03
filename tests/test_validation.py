
import common_util as cu
import pandas as pd

# Define the location of the transformed dataset.
# Hoa's transformation creates this CSV file inside the "data" folder.
DATASET_PATH = cu.DATA_DIR / "curated_games_dataset.csv"


def load_dataset():
    """
    Load the transformed Steam game dataset.

    This helper function is used by all validation tests, so we do not
    have to repeat the same CSV-loading code in every test.
    """

    # Check that the transformation output exists before reading it.
    # If the file is missing, pytest will show a clear error message.
    assert DATASET_PATH.exists(), (
        f"Transformed dataset not found: {DATASET_PATH}"
    )

    # Read the CSV file into a pandas DataFrame.
    return pd.read_csv(DATASET_PATH)


def test_appid_not_null():
    """
    Validate that every game has an appid.

    The appid is the unique identifier for a Steam application,
    so it should never be missing.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Check that no appid value is missing.
    # .notna() returns True for values that are not missing.
    # .all() requires every row to pass the check.
    assert df["appid"].notna().all()


def test_appid_unique():
    """
    Validate that every appid is unique.

    The appid identifies a specific Steam application, so the same
    appid should not appear more than once in the transformed dataset.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Check that every appid appears only once.
    # Pandas' .is_unique returns True if all values in the column are unique.
    assert df["appid"].is_unique


def test_name_not_empty():
    """
    Validate that every game has a non-empty name.

    The game name is an important descriptive field, so it should
    contain a value and should not be an empty string or whitespace.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Convert the name column to string and remove leading/trailing
    # whitespace before checking whether the value is empty.
    names = df["name"].astype(str).str.strip()

    # Check that every game has a non-empty name.
    assert names.ne("").all()


def test_price_not_negative():
    """
    Validate that game prices are never negative.

    A price of zero is valid, and a missing price (NULL/NaN) is also
    allowed because some games may not have a price.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Select rows where price is available.
    # Missing prices (NaN) are excluded because they are allowed.
    prices = df["price"].dropna()

    # Check that every available price is greater than or equal to zero.
    assert (prices >= 0).all()


def test_downloadable_content_not_negative():
    """
    Validate that the number of downloadable content items is not negative.

    A value of zero is valid because a game may have no DLC.
    Missing values are allowed for this validation.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Select only rows where downloadable_content has a value.
    # Missing values are allowed, so they are excluded from this check.
    downloadable_content = df["downloadable_content"].dropna()

    # Check that every available value is greater than or equal to zero.
    assert (downloadable_content >= 0).all()


def test_achievements_not_negative():
    """
    Validate that the number of achievements is not negative.

    A value of zero is valid because a game may have no achievements.
    Missing values are allowed for this validation.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Select only rows where achievements has a value.
    # Missing values are allowed, so they are excluded from this check.
    achievements = df["achievements"].dropna()

    # Check that every available value is greater than or equal to zero.
    assert (achievements >= 0).all()


def test_recommendations_not_negative():
    """
    Validate that the number of recommendations is not negative.

    A value of zero is valid because a game may have no recommendations.
    Missing values are allowed for this validation.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Select only rows where recommendations has a value.
    # Missing values are allowed, so they are excluded from this check.
    recommendations = df["recommendations"].dropna()

    # Check that every available value is greater than or equal to zero.
    assert (recommendations >= 0).all()


def test_metacritic_score_valid_range():
    """
    Validate that Metacritic scores are within the valid 0-100 range.

    A score of 0 or 100 is valid.
    Missing values are allowed because some games do not have a
    Metacritic score.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Select only rows where metacritic_score has a value.
    # Missing values are allowed, so they are excluded from this check.
    scores = df["metacritic_score"].dropna()

    # Check that every available score is between 0 and 100, inclusive.
    assert scores.between(0, 100).all()


def test_free_game_price_is_null():
    """
    Validate the business rule for free games.

    If a game is marked as free (is_free = True), its price should
    be 0 because a free game does not have a purchase price.
    """

    # Load the transformed dataset.
    df = load_dataset()

    # Select only the rows where the game is marked as free.
    free_games = df["is_free"]

    # Check that all free games have a price of 0.
    assert (free_games["price"] == 0).all()
