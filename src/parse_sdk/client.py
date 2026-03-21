"""
ParseClient — Point d'entrée principal du SDK.

Ce module fournit la classe publique ParseClient que chaque utilisateur
installe pour configurer sa connexion à Parse Server.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._http import ParseHTTPClient

if TYPE_CHECKING:
    pass

# Variable de module pour le pattern singleton/global
_current_client: ParseHTTPClient | None = None


class ParseClient:
    """Client principal pour se connecter à Parse Server.

    ParseClient est le point d'entrée du SDK. Il stocke la configuration
    et fournit un accès partagé au client HTTP interne.

    Args:
        app_id: Identifiant de l'application Parse (obligatoire).
        rest_key: Clé REST API de l'application (obligatoire).
        server_url: URL du serveur Parse, ex: https://my-parse.com/parse (obligatoire).
        master_key: Clé maître pour les opérations admin (optionnel).
        timeout: Timeout des requêtes en secondes (défaut: 30).
        max_retries: Nombre max de tentatives en cas d'erreur (défaut: 3).

    Raises:
        ValueError: Si app_id, rest_key ou server_url est vide ou None.

    Example:
        >>> client = ParseClient(
        ...     app_id="myAppId",
        ...     rest_key="myRestKey",
        ...     server_url="https://my-parse.com/parse",
        ... )
        >>> http = get_client()
        >>> await http.get("/classes/GameScore")
    """

    def __init__(
        self,
        app_id: str,
        rest_key: str,
        server_url: str,
        master_key: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        """Initialise ParseClient avec la configuration de connexion.

        Args:
            app_id: Identifiant de l'application Parse (obligatoire).
            rest_key: Clé REST API de l'application (obligatoire).
            server_url: URL du serveur Parse (obligatoire).
            master_key: Clé maître pour les opérations admin (optionnel).
            timeout: Timeout des requêtes en secondes (défaut: 30.0).
            max_retries: Nombre max de tentatives (défaut: 3).

        Raises:
            ValueError: Si app_id, rest_key ou server_url est vide ou None.
        """
        # Validation des paramètres obligatoires
        self._validate_required_param(app_id, "app_id")
        self._validate_required_param(rest_key, "rest_key")
        self._validate_required_param(server_url, "server_url")

        # Stocker la configuration (optionnel mais utile pour debugging)
        self._app_id = app_id
        self._rest_key = rest_key
        self._server_url = server_url
        self._master_key = master_key
        self._timeout = timeout
        self._max_retries = max_retries

        # Créer le client HTTP interne
        self._http_client = ParseHTTPClient(
            app_id=app_id,
            rest_key=rest_key,
            server_url=server_url,
            master_key=master_key,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Enregistrer comme client global
        global _current_client
        _current_client = self._http_client

    @staticmethod
    def _validate_required_param(value: str | None, name: str) -> None:
        """Valide qu'un paramètre obligatoire n'est pas vide."""
        if value is None or not value.strip():
            raise ValueError(
                f"Le paramètre '{name}' est obligatoire et ne peut pas être vide"
            )

    @property
    def http_client(self) -> ParseHTTPClient:
        """Retourne le client HTTP interne."""
        return self._http_client


def get_client() -> ParseHTTPClient:
    """Retourne l'instance globale de ParseHTTPClient.

    Cette fonction est utilisée par tous les modules du SDK pour accéder
    au client HTTP configuré.

    Returns:
        L'instance de ParseHTTPClient créée par ParseClient.

    Raises:
        RuntimeError: Si ParseClient n'a pas encore été initialisé.

    Example:
        >>> from parse_sdk import ParseClient
        >>> from parse_sdk.client import get_client
        >>>
        >>> client = ParseClient(app_id="...", rest_key="...", server_url="...")
        >>> http = get_client()
        >>> await http.get("/classes/GameScore")
    """

    if _current_client is None:
        raise RuntimeError(
            "ParseClient n'a pas été initialisé. "
            "Créez d'abord une instance: ParseClient(app_id=..., rest_key=..., server_url=...)"
        )
    return _current_client
