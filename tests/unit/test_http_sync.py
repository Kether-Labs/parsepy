from unittest.mock import MagicMock, patch

from parse_sdk._http import ParseHTTPClient


def test_http_get_sync():
    client = ParseHTTPClient(
        app_id="app",
        rest_key="rest",
        server_url="https://api.parse.com/parse",
    )

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.request.return_value = MagicMock(
            status_code=200,
            json=lambda: {"results": []},
            is_error=False,
        )
        mock_client_class.return_value.__enter__.return_value = mock_client

        response = client.get_sync("/classes/GameScore")

        assert response == {"results": []}
        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://api.parse.com/parse/classes/GameScore"


def test_http_post_sync():
    client = ParseHTTPClient(
        app_id="app",
        rest_key="rest",
        server_url="https://api.parse.com/parse",
    )

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.request.return_value = MagicMock(
            status_code=201,
            json=lambda: {"objectId": "123"},
            is_error=False,
        )
        mock_client_class.return_value.__enter__.return_value = mock_client

        response = client.post_sync("/classes/GameScore", json={"score": 100})

        assert response == {"objectId": "123"}
        mock_client.request.assert_called_once()
        args, kwargs = mock_client.request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["json"] == {"score": 100}
