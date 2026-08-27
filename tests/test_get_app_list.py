from unittest.mock import patch

import fetch_app_list


def test_get_app_list():
    mock_response = {
        "response": {
            "apps": [
                {
                    "appid": 10,
                    "name": "Counter-Strike",
                    "last_modified": 1745368572,
                    "price_change_number": 37149137
                },
                {
                    "appid": 20,
                    "name": "Team Fortress Classic",
                    "last_modified": 1745368565,
                    "price_change_number": 37149137
                }
            ],
            "have_more_results": False,
            "last_appid": 20
        }
    }

    # Replaces the real "requests.get(...)" with a mock
    with patch("fetch_app_list.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response

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
        {
            "appid": 10,
            "name": "Counter-Strike"
        },
        {
            "appid": 20,
            "name": "Team Fortress Classic"
        }
    ]
