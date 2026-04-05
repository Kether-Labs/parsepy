from unittest.mock import MagicMock, patch

import httpx
import pytest

from parse_sdk._http import ParseHTTPClient
from parse_sdk.exceptions import ParseConnectionError, ParseTimeoutError


@pytest.mark.asyncio
async def test_http_use_master_key():
    client = ParseHTTPClient(
        app_id="app",
        rest_key="rest",
        server_url="https://api.parse.com/parse",
        master_key="secret"
    )

    with patch("httpx.AsyncClient.request") as mock_request:
        mock_request.return_value = MagicMock(status_code=200, json=lambda: {}, is_error=False)

        await client.get("/classes/GameScore", use_master_key=True)

        args, kwargs = mock_request.call_args
        assert kwargs["headers"]["X-Parse-Master-Key"] == "secret"

@pytest.mark.asyncio
async def test_http_retry_logic():
    client = ParseHTTPClient(
        app_id="app",
        rest_key="rest",
        server_url="https://api.parse.com/parse",
        max_retries=2
    )

    with patch("httpx.AsyncClient.request") as mock_request:
        # Premier appel : 503, Deuxième appel : 200
        mock_request.side_effect = [
            MagicMock(status_code=503, is_error=True, text="Service Unavailable"),
            MagicMock(status_code=200, json=lambda: {"ok": True}, is_error=False)
        ]

        with patch("asyncio.sleep", return_value=None): # Skip sleep
            response = await client.get("/classes/GameScore")
            assert response == {"ok": True}
            assert mock_request.call_count == 2

@pytest.mark.asyncio
async def test_http_timeout_exception():
    client = ParseHTTPClient(
        app_id="app",
        rest_key="rest",
        server_url="https://api.parse.com/parse",
        max_retries=1
    )

    with (
        patch("httpx.AsyncClient.request", side_effect=httpx.TimeoutException("Timeout")),
        pytest.raises(ParseTimeoutError),
    ):
        await client.get("/classes/GameScore")

@pytest.mark.asyncio
async def test_http_network_error():
    client = ParseHTTPClient(
        app_id="app",
        rest_key="rest",
        server_url="https://api.parse.com/parse",
        max_retries=1
    )

    with (
        patch("httpx.AsyncClient.request", side_effect=httpx.NetworkError("Network")),
        pytest.raises(ParseConnectionError),
    ):
        await client.get("/classes/GameScore")

def test_http_sync_retry_and_errors():
    client = ParseHTTPClient(
        app_id="app",
        rest_key="rest",
        server_url="https://api.parse.com/parse",
        max_retries=2
    )

    with (
        patch("httpx.Client.request") as mock_request,
        patch("time.sleep", return_value=None),
    ):
        # Simulation d'un timeout puis succès
        mock_request.side_effect = [
            httpx.TimeoutException("Timeout"),
            MagicMock(status_code=200, json=lambda: {"ok": True}, is_error=False),
        ]
        response = client.get_sync("/classes/GameScore")
        assert response == {"ok": True}
        assert mock_request.call_count == 2
