from unittest.mock import MagicMock, patch

import build_dataset


def make_mock_response(data):
    response = MagicMock()
    response.json.return_value = data
    return response


def test_get_app_details():
    mock_response = {
        "123": {
            "success": True,
            "data": {
                "steam_appid": 123,
                "name": "Test Game",
                "type": "game"
            }
        }
    }

    with patch("build_dataset.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        result = build_dataset.get_app_details(
            123,
            country="se",
            language="en"
        )

        mock_get.assert_called_once_with(
            build_dataset.STEAM_APP_DETAILS_URL,
            params={
                "appids": 123,
                "cc": build_dataset.DEFAULT_COUNTRY_CODE,
                "l": build_dataset.DEFAULT_LANGUAGE
            },
            timeout=build_dataset.REQUEST_TIMEOUT
        )

    assert result == {
        "steam_appid": 123,
        "name": "Test Game",
        "type": "game"
    }


def test_get_app_details_missing_app():
    mock_response = {
        "response": {}
    }

    with patch("build_dataset.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        result = build_dataset.get_app_details(123)

    assert result is None


def test_get_app_details_unsuccessful():
    mock_response = {
        "123": {
            "success": False
        }
    }

    with patch("build_dataset.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        result = build_dataset.get_app_details(123)

    assert result is None


def test_get_app_details_with_filters():
    mock_response = {
        "123": {
            "success": True,
            "data": {
                "steam_appid": 123
            }
        }
    }

    with patch("build_dataset.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        build_dataset.get_app_details(
            123,
            country="se",
            language="en",
            filters="price_overview"
        )

        mock_get.assert_called_once_with(
            build_dataset.STEAM_APP_DETAILS_URL,
            params={
                "appids": 123,
                "cc": "se",
                "l": "en",
                "filters": "price_overview"
            },
            timeout=build_dataset.REQUEST_TIMEOUT
        )
def test_extract_game_data():
    details = {
        "steam_appid": 123,
        "name": "Test Game",
        "is_free": False,
        "price_overview": {
            "final": 19990,
            "currency": "SEK"
        },
        "about_the_game": "A test game.",
        "platforms": {
            "windows": True,
            "mac": False,
            "linux": True
        },
        "metacritic": {
            "score": 85,
            "url": "https://example.com"
        }
    }

    result = build_dataset.extract_game_data(details)

    assert result == {
        "appid": 123,
        "name": "Test Game",
        "is_free": False,
        "price": 199.90,
        "currency": "SEK",
        "about_the_game": "A test game.",
        "windows": True,
        "mac": False,
        "linux": True,
        "metacritic_score": 85,
        "metacritic_url": "https://example.com"
    }
