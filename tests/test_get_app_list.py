from unittest.mock import MagicMock, patch

import fetch_app_list


def steam_app(appid, name):
    return {
        "appid": appid,
        "name": name,
        "last_modified": 123,
        "price_change_number": 456
    }


def expected_app(appid, name):
    return {
        "appid": appid,
        "name": name
    }


def make_mock_response(data):
    response = MagicMock()
    response.json.return_value = data
    return response


def test_get_app_list():
    mock_response = {
        "response": {
            "apps": [
                steam_app(10, "Counter-Strike"),
                steam_app(20, "Team Fortress Classic")
            ],
            "have_more_results": False,
            "last_appid": 20
        }
    }

    # Replaces the real "requests.get(...)" with a mock
    with patch("fetch_app_list.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        # No request to Steam, instead caught by mock_get,
        # so that when response.json() is called we get mock_response
        result = fetch_app_list.get_app_list("fake-api-key")

        # Then we test that the code actually did request as expected
        mock_get.assert_called_once_with(
            fetch_app_list.STEAM_APP_LIST_URL,
            params={
                "key": "fake-api-key",
                "max_results": fetch_app_list.MAX_RESULTS,
                "last_appid": 0
            },
            timeout=fetch_app_list.REQUEST_TIMEOUT
        )

    # And finally test if we transform the response to correct format
    assert result == [
        expected_app(10, "Counter-Strike"),
        expected_app(20, "Team Fortress Classic")
    ]


def test_get_app_list_empty_response():
    mock_response = {
        "response": {
            "apps": []
        }
    }

    with patch("fetch_app_list.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        result = fetch_app_list.get_app_list("fake-api-key")

    assert result == []


def test_get_app_list_pagination():
    first_response = {
        "response": {
            "apps": [
                steam_app(10, "Counter-Strike"),
                steam_app(20, "Team Fortress Classic")
            ],
            "have_more_results": True,
            "last_appid": 20
        }
    }

    second_response = {
        "response": {
            "apps": [
                steam_app(30, "Day of Defeat"),
                steam_app(40, "Deathmatch Classic")
            ],
            "have_more_results": False,
            "last_appid": 40
        }
    }

    with patch("fetch_app_list.requests.get") as mock_get:
        mock_get.side_effect = [
            make_mock_response(first_response),
            make_mock_response(second_response)
        ]

        result = fetch_app_list.get_app_list("fake-api-key")

        assert mock_get.call_count == 2

        # Test pagination params and algorithm - note last_appid
        mock_get.assert_any_call(
            fetch_app_list.STEAM_APP_LIST_URL,
            params={
                "key": "fake-api-key",
                "max_results": fetch_app_list.MAX_RESULTS,
                "last_appid": 0
            },
            timeout=fetch_app_list.REQUEST_TIMEOUT
        )

        mock_get.assert_any_call(
            fetch_app_list.STEAM_APP_LIST_URL,
            params={
                "key": "fake-api-key",
                "max_results": fetch_app_list.MAX_RESULTS,
                "last_appid": 20
            },
            timeout=fetch_app_list.REQUEST_TIMEOUT
        )

    assert result == [
        expected_app(10, "Counter-Strike"),
        expected_app(20, "Team Fortress Classic"),
        expected_app(30, "Day of Defeat"),
        expected_app(40, "Deathmatch Classic")
    ]


def test_get_app_list_max_apps():
    """
    Test max_apps parameter, that we actually get the max number of results
    """
    mock_response = {
        "response": {
            "apps": [
                steam_app(10, "Counter-Strike"),
                steam_app(20, "Team Fortress Classic"),
                steam_app(30, "Day of Defeat"),
            ],
            "have_more_results": True,
            "last_appid": 30
        }
    }

    with patch("fetch_app_list.requests.get") as mock_get:
        mock_get.return_value = make_mock_response(mock_response)

        result = fetch_app_list.get_app_list(
            "fake-api-key",
            max_apps=3
        )

    assert result == [
        expected_app(10, "Counter-Strike"),
        expected_app(20, "Team Fortress Classic"),
        expected_app(30, "Day of Defeat"),
    ]

    mock_get.assert_called_once_with(
        fetch_app_list.STEAM_APP_LIST_URL,
        params={
            "key": "fake-api-key",
            "max_results": 3,
            "last_appid": 0
        },
        timeout=fetch_app_list.REQUEST_TIMEOUT
    )
