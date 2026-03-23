"""
Tests unitaires pour ParseClient.

Couvre:
- Initialisation avec paramètres valides
- Validation des paramètres obligatoires
- get_client() avant et après initialisation
"""

from __future__ import annotations

import pytest

from parse_sdk import ParseClient
from parse_sdk.client import get_client


class TestParseClientInit:
    """Tests d'initialisation de ParseClient."""

    def test_init_with_required_params(self) -> None:
        """ParseClient s'instancie avec les 3 paramètres obligatoires."""
        client = ParseClient(
            app_id="test_app",
            rest_key="test_key",
            server_url="https://test.parse.com/parse",
        )

        assert client._app_id == "test_app"
        assert client._rest_key == "test_key"
        assert client._server_url == "https://test.parse.com/parse"

    def test_init_with_all_params(self) -> None:
        """ParseClient accepte tous les paramètres optionnels."""
        client = ParseClient(
            app_id="test_app",
            rest_key="test_key",
            server_url="https://test.parse.com/parse",
            master_key="master",
            timeout=60.0,
            max_retries=5,
        )
        assert client._master_key == "master"
        assert client._timeout == 60.0
        assert client._max_retries == 5

    def test_init_strips_server_url_trailing_slash(self) -> None:
        """Le trailing slash de server_url est supprimé."""
        client = ParseClient(
            app_id="test",
            rest_key="test",
            server_url="https://test.parse.com/parse/",
        )
        # Le HTTPClient interne supprime le slash
        assert client._http_client._server_url == "https://test.parse.com/parse"


class TestParseClientValidation:
    """Tests de validation des paramètres."""

    def test_init_raises_on_empty_app_id(self) -> None:
        """ValueError si app_id est vide."""
        with pytest.raises(ValueError, match="app_id"):
            ParseClient(
                app_id="",
                rest_key="test",
                server_url="https://test.com",
            )

    def test_init_raises_on_none_app_id(self) -> None:
        """ValueError si app_id est None."""
        with pytest.raises(ValueError, match="app_id"):
            ParseClient(
                app_id=None,  # type: ignore
                rest_key="test",
                server_url="https://test.com",
            )

    def test_init_raises_on_empty_rest_key(self) -> None:
        """ValueError si rest_key est vide."""
        with pytest.raises(ValueError, match="rest_key"):
            ParseClient(
                app_id="test",
                rest_key="",
                server_url="https://test.com",
            )

    def test_init_raises_on_empty_server_url(self) -> None:
        """ValueError si server_url est vide."""
        with pytest.raises(ValueError, match="server_url"):
            ParseClient(
                app_id="test",
                rest_key="test",
                server_url="",
            )

    def test_init_raises_on_whitespace_only(self) -> None:
        """ValueError si le paramètre n'est que des espaces."""
        with pytest.raises(ValueError, match="app_id"):
            ParseClient(
                app_id="   ",
                rest_key="test",
                server_url="https://test.com",
            )


class TestGetClient:
    """Tests pour get_client()."""

    def test_get_client_before_init_raises(self) -> None:
        """RuntimeError si get_client() appelé avant initialisation."""
        # Reset le client global
        import parse_sdk.client as client_module

        client_module._current_client = None

        with pytest.raises(RuntimeError, match="ParseClient n'a pas été initialisé"):
            get_client()

    def test_get_client_returns_http_client(self) -> None:
        """get_client() retourne le ParseHTTPClient configuré."""
        from parse_sdk._http import ParseHTTPClient

        client = ParseClient(
            app_id="test",
            rest_key="test",
            server_url="https://test.com",
        )

        http = get_client()
        assert isinstance(http, ParseHTTPClient)
        assert http is client._http_client

    def test_get_client_returns_same_instance(self) -> None:
        """get_client() retourne toujours la même instance."""
        _ = ParseClient(
            app_id="test",
            rest_key="test",
            server_url="https://test.com",
        )

        http1 = get_client()
        http2 = get_client()
        assert http1 is http2


class TestParseClientProperties:
    """Tests des propriétés de ParseClient."""

    def test_http_client_property(self) -> None:
        """La propriété http_client retourne le client HTTP."""
        client = ParseClient(
            app_id="test",
            rest_key="test",
            server_url="https://test.com",
        )

        http = client.http_client
        assert http is client._http_client
