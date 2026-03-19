"""
Couche HTTP interne du SDK Parse Server Python.

Ce module est PRIVÉ. Il ne doit jamais être importé directement par les
utilisateurs du SDK. Tous les modules publics (ParseObject, ParseQuery, etc.)
passent exclusivement par ce module pour leurs requêtes HTTP.

Responsabilités :
- Gérer le client httpx (async + sync)
- Injecter les headers Parse obligatoires
- Retry automatique avec backoff exponentiel
- Convertir les erreurs HTTP en exceptions ParseError
- Logger les requêtes/réponses pour le debug
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from .exceptions import (
    ParseConnectionError,
    ParseError,
    ParseTimeoutError,
    raise_parse_error,
)

logger = logging.getLogger("parse_sdk.http")

# Codes HTTP qui déclenchent un retry automatique
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}

# Délai initial entre deux tentatives (secondes)
_RETRY_BASE_DELAY = 0.5


class ParseHTTPClient:
    """Client HTTP interne — couche d'abstraction sur httpx.

    Gère automatiquement :
    - Les headers Parse (App-Id, REST-Key, Master-Key, Session-Token)
    - Le retry avec backoff exponentiel
    - La conversion des erreurs en exceptions SDK

    Args:
        app_id: Identifiant de l'application Parse.
        rest_key: Clé REST de l'application.
        server_url: URL de base du serveur Parse (ex: https://my-parse.com/parse).
        master_key: Clé maître (optionnel — pour les opérations admin).
        timeout: Timeout des requêtes en secondes (défaut : 30).
        max_retries: Nombre maximum de tentatives (défaut : 3).

    Note:
        Ce client est instancié et géré par `ParseClient`. Ne pas instancier
        directement.
    """

    def __init__(
        self,
        app_id: str,
        rest_key: str,
        server_url: str,
        master_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._app_id = app_id
        self._rest_key = rest_key
        self._server_url = server_url.rstrip("/")
        self._master_key = master_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._session_token: str | None = None

        # Client async partagé — évite de rouvrir une connexion à chaque requête
        self._async_client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Gestion du session token (défini par ParseUser après login)
    # ------------------------------------------------------------------

    def set_session_token(self, token: str | None) -> None:
        """Définit le session token à envoyer dans les requêtes suivantes."""
        self._session_token = token

    def clear_session_token(self) -> None:
        """Supprime le session token (après logout)."""
        self._session_token = None

    # ------------------------------------------------------------------
    # Construction des headers
    # ------------------------------------------------------------------

    def _build_headers(
        self,
        use_master_key: bool = False,
        session_token: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, str]:
        """Construit les headers HTTP pour une requête Parse.

        Args:
            use_master_key: Ajoute X-Parse-Master-Key si True.
            session_token: Token de session à utiliser (priorité sur self._session_token).
            content_type: Content-Type de la requête.

        Returns:
            Dictionnaire de headers HTTP prêt à l'emploi.
        """
        headers: dict[str, str] = {
            "X-Parse-Application-Id": self._app_id,
            "X-Parse-REST-API-Key": self._rest_key,
            "Content-Type": content_type,
        }

        if use_master_key and self._master_key:
            headers["X-Parse-Master-Key"] = self._master_key

        token = session_token or self._session_token
        if token:
            headers["X-Parse-Session-Token"] = token

        return headers

    # ------------------------------------------------------------------
    # Gestion du client async
    # ------------------------------------------------------------------

    async def _get_async_client(self) -> httpx.AsyncClient:
        """Retourne le client async partagé, en le créant si nécessaire."""
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                follow_redirects=True,
            )
        return self._async_client

    async def close(self) -> None:
        """Ferme proprement le client HTTP async."""
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
            self._async_client = None

    # ------------------------------------------------------------------
    # Méthode principale : requête async avec retry
    # ------------------------------------------------------------------

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        content: bytes | None = None,
        use_master_key: bool = False,
        session_token: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """Exécute une requête HTTP vers Parse Server avec retry automatique.

        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE).
            path: Chemin relatif (ex: /classes/GameScore).
            json: Corps JSON de la requête.
            params: Paramètres de query string.
            data: Corps form-encoded (utilisé pour /login).
            content: Corps binaire brut (utilisé pour les fichiers).
            use_master_key: Utilise le Master Key si True.
            session_token: Session token à utiliser pour cette requête.
            content_type: Content-Type override.

        Returns:
            Réponse JSON désérialisée.

        Raises:
            ParseConnectionError: Erreur réseau ou serveur inaccessible.
            ParseTimeoutError: Requête expirée.
            ParseError: Toute erreur retournée par Parse Server.
        """
        url = f"{self._server_url}{path}"
        headers = self._build_headers(
            use_master_key=use_master_key,
            session_token=session_token,
            content_type=content_type,
        )

        client = await self._get_async_client()
        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                logger.debug(
                    "→ %s %s (tentative %d/%d)",
                    method,
                    path,
                    attempt + 1,
                    self._max_retries,
                )

                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                    data=data,
                    content=content,
                )

                logger.debug("← %d %s", response.status_code, path)

                if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries - 1:
                    delay = _RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "Erreur %d sur %s — retry dans %.1fs",
                        response.status_code,
                        path,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue

                return self._handle_response(response)

            except httpx.TimeoutException as exc:
                last_error = ParseTimeoutError(
                    f"Timeout sur {method} {path} après {self._timeout}s"
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(_RETRY_BASE_DELAY * (2 ** attempt))

            except httpx.NetworkError as exc:
                last_error = ParseConnectionError(
                    f"Erreur réseau sur {method} {path} : {exc}"
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(_RETRY_BASE_DELAY * (2 ** attempt))

        raise last_error or ParseConnectionError(f"Échec de la requête {method} {path}")

    # ------------------------------------------------------------------
    # Wrapper synchrone
    # ------------------------------------------------------------------

    def request_sync(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Version synchrone de `request()`.

        Utilise un client httpx synchrone séparé. Utile pour les contextes
        sans event loop (scripts, Django views classiques, etc.).

        Args:
            method: Méthode HTTP.
            path: Chemin relatif.
            **kwargs: Mêmes arguments que `request()`.

        Returns:
            Réponse JSON désérialisée.
        """
        url = f"{self._server_url}{path}"
        headers = self._build_headers(
            use_master_key=kwargs.pop("use_master_key", False),
            session_token=kwargs.pop("session_token", None),
            content_type=kwargs.pop("content_type", "application/json"),
        )

        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                with httpx.Client(
                    timeout=httpx.Timeout(self._timeout),
                    follow_redirects=True,
                ) as client:
                    response = client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        **kwargs,
                    )

                if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries - 1:
                    time.sleep(_RETRY_BASE_DELAY * (2 ** attempt))
                    continue

                return self._handle_response(response)

            except httpx.TimeoutException as exc:
                last_error = ParseTimeoutError(str(exc))
                if attempt < self._max_retries - 1:
                    time.sleep(_RETRY_BASE_DELAY * (2 ** attempt))

            except httpx.NetworkError as exc:
                last_error = ParseConnectionError(str(exc))
                if attempt < self._max_retries - 1:
                    time.sleep(_RETRY_BASE_DELAY * (2 ** attempt))

        raise last_error or ParseConnectionError(f"Échec de la requête {method} {path}")

    # ------------------------------------------------------------------
    # Traitement de la réponse HTTP
    # ------------------------------------------------------------------

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Parse la réponse HTTP et lève l'exception appropriée si erreur.

        Args:
            response: Réponse httpx brute.

        Returns:
            Corps JSON désérialisé.

        Raises:
            ParseError: Si le serveur retourne une erreur (code != 2xx).
        """
        try:
            body: dict[str, Any] = response.json()
        except Exception:
            body = {}

        # Parse Server retourne toujours {"error": "...", "code": N} en cas d'erreur
        if response.is_error:
            code = body.get("code", response.status_code)
            message = body.get("error", response.text or "Erreur inconnue")
            logger.debug("Erreur Parse %d : %s", code, message)
            raise_parse_error(code=int(code), message=str(message))

        return body

    # ------------------------------------------------------------------
    # Helpers HTTP raccourcis
    # ------------------------------------------------------------------

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """GET asynchrone."""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """POST asynchrone."""
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """PUT asynchrone."""
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """DELETE asynchrone."""
        return await self.request("DELETE", path, **kwargs)
