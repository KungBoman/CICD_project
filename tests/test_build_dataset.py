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
