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

        result = build_dataset.get_app_details(123)

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
                "steam_appid": 123,
                "name": "Test Game"
            }
        }
    }

    with patch("build_dataset.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        result = build_dataset.get_app_details(
            123,
            config=build_dataset.DatasetConfig(
                filters="name,platforms,price_overview"
            )
        )

        mock_get.assert_called_once_with(
            build_dataset.STEAM_APP_DETAILS_URL,
            params={
                "appids": 123,
                "cc": "se",
                "l": "en",
                "filters": "name,platforms,price_overview"
            },
            timeout=build_dataset.REQUEST_TIMEOUT
        )

    assert result == {
        "steam_appid": 123,
        "name": "Test Game"
    }


def test_extract_game_data_and_convert_dataset_row():
    details = {
        "steam_appid": 123,
        "name": "Test Game",
        "header_image": "https://image.com",
        "website": "https://website.com",
        "release_date": {
            "coming_soon": False,
            "date": "1 Jan, 1970"
        },
        "is_free": False,
        "price_overview": {
            "final": 19990,
            "currency": "SEK"
        },
        "about_the_game": "A test game.",
        "short_description": "A test game's short description.",
        "detailed_description": "A test game's detailed description.",
        "dlc": [480, 520],
        "achievements": {"total": 10},
        "recommendations": {"total": 25},
        "platforms": {
            "windows": True,
            "mac": False,
            "linux": True
        },
        "metacritic": {
            "score": 85,
            "url": "https://metacritic.com"
        },
        "support_url": "https://support.com",
        "support_email": "support@support.com",
        "supported_languages": "English, Swedish",
        "supported_audio_languages": "English",
        "developers": ["Dev1", "Dev2"],
        "publishers": ["Pub1", "Pub2"],
        "categories": ["Cat1", "Cat2"],
        "genres": ["Gen1", "Gen2"],
    }

    expected = build_dataset.extract_game_data(details)

    csv_row = {
        key: str(value) if value is not None else ""
        for key, value in expected.items()
    }

    result = build_dataset.convert_dataset_row(csv_row)

    assert result == expected


def test_extract_game_data_without_price():
    details = {
        "steam_appid": 123,
        "name": "Free Game",
        "is_free": True
    }

    result = build_dataset.extract_game_data(details)

    assert result == {
        "appid": 123,
        "name": "Free Game",
        "header_image": "",
        "website": "",
        "release_date": "1970-01-01",
        "is_free": True,
        "price": 0,
        "currency": "",
        "about_the_game": "",
        "short_description": "",
        "detailed_description": "",
        "dlc_count": 0,
        "achievements": 0,
        "recommendations": 0,
        "windows": False,
        "mac": False,
        "linux": False,
        "metacritic_score": "",
        "metacritic_url": "",
        "support_url": "",
        "support_email": "",
        "supported_languages": [],
        "supported_audio_languages": [],
        "developers": [],
        "publishers": [],
        "categories": [],
        "genres": [],
    }
