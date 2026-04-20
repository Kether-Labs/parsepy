"""
Gestion des objets Parse (ParseObject).
Lecture, modification et sauvegarde des données.
"""

from __future__ import annotations

from typing import Any

from ._types import decode_parse_value, encode_parse_value
from .client import get_client


class ParseObject:
    """Représente un objet stocké sur Parse Server.

    Args:
        class_name: Le nom de la classe Parse (ex: "GameScore").
        object_id: L'identifiant unique de l'objet (si déjà existant).
    """

    def __init__(self, class_name: str, object_id: str | None = None) -> None:
        self.class_name = class_name
        self.object_id = object_id

        self._data: dict[str, Any] = {}
        self._dirty_keys: set[str] = set()

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère la valeur d'un champ.

        Args:
            key: Le nom du champ.
            default: Valeur par défaut si le champ n'existe pas.

        Returns:
            La valeur du champ (décodée si type spécial Parse).
        """
        value = self._data.get(key, default)
        return decode_parse_value(value)

    def set(self, key: str, value: Any) -> ParseObject:
        """Définit la valeur d'un champ.

        Args:
            key: Le nom du champ.
            value: La valeur à enregistrer.

        Returns:
            L'instance actuelle (pour le chaînage).
        """
        self._data[key] = value
        self._dirty_keys.add(key)

        return self

    async def save(
        self, use_master_key: bool = False, session_token: str | None = None
    ) -> None:
        """Sauvegarde l'objet sur Parse Server.

        Cette méthode envoie uniquement les champs modifiés (dirty).

        Args:
            use_master_key: Utilise le Master Key si True.
            session_token: Session token à utiliser pour cette requête.

        Raises:
            ParseError: Si le serveur retourne une erreur.
        """
        if not self._dirty_keys:
            return

        payload = {key: encode_parse_value(self._data[key]) for key in self._dirty_keys}
        client = get_client()

        if self.object_id:
            path = f"/classes/{self.class_name}/{self.object_id}"
            response = await client.put(
                path,
                json=payload,
                use_master_key=use_master_key,
                session_token=session_token,
            )
        else:
            path = f"/classes/{self.class_name}"
            response = await client.post(
                path,
                json=payload,
                use_master_key=use_master_key,
                session_token=session_token,
            )

            if "objectId" in response:
                self.object_id = response["objectId"]

        self._data.update(response)
        self._dirty_keys.clear()

    def save_sync(
        self, use_master_key: bool = False, session_token: str | None = None
    ) -> None:
        """Version synchrone de `save()`.

        Args:
            use_master_key: Utilise le Master Key si True.
            session_token: Session token à utiliser pour cette requête.

        Raises:
            ParseError: Si le serveur retourne une erreur.
        """
        if not self._dirty_keys:
            return

        payload = {key: encode_parse_value(self._data[key]) for key in self._dirty_keys}
        client = get_client()

        if self.object_id:
            path = f"/classes/{self.class_name}/{self.object_id}"
            response = client.put_sync(
                path,
                json=payload,
                use_master_key=use_master_key,
                session_token=session_token,
            )
        else:
            path = f"/classes/{self.class_name}"
            response = client.post_sync(
                path,
                json=payload,
                use_master_key=use_master_key,
                session_token=session_token,
            )

            if "objectId" in response:
                self.object_id = response["objectId"]

        self._data.update(response)
        self._dirty_keys.clear()

    async def fetch(
        self, use_master_key: bool = False, session_token: str | None = None
    ) -> ParseObject:
        """Récupère les dernières données de l'objet depuis le serveur.

        Met à jour l'instance actuelle et efface les modifications locales non sauvegardées.

        Args:
            use_master_key: Utilise le Master Key si True.
            session_token: Session token à utiliser pour cette requête.

        Returns:
            L'instance actuelle de ParseObject.

        Raises:
            RuntimeError: Si l'objet n'a pas d'objectId.
            ParseError: Si le serveur retourne une erreur.
        """
        if not self.object_id:
            raise RuntimeError("Impossible de fetch un objet sans objectId")

        client = get_client()
        path = f"/classes/{self.class_name}/{self.object_id}"
        response = await client.get(
            path, use_master_key=use_master_key, session_token=session_token
        )

        self._data = response
        self._dirty_keys.clear()
        return self

    def fetch_sync(
        self, use_master_key: bool = False, session_token: str | None = None
    ) -> ParseObject:
        """Version synchrone de `fetch()`.

        Args:
            use_master_key: Utilise le Master Key si True.
            session_token: Session token à utiliser pour cette requête.

        Returns:
            L'instance actuelle de ParseObject.

        Raises:
            RuntimeError: Si l'objet n'a pas d'objectId.
        """
        if not self.object_id:
            raise RuntimeError("Impossible de fetch un objet sans objectId")

        client = get_client()
        path = f"/classes/{self.class_name}/{self.object_id}"
        response = client.get_sync(
            path, use_master_key=use_master_key, session_token=session_token
        )

        self._data = response
        self._dirty_keys.clear()
        return self

    async def delete(
        self, use_master_key: bool = False, session_token: str | None = None
    ) -> None:
        """Supprime l'objet sur Parse Server.

        Args:
            use_master_key: Utilise le Master Key si True.
            session_token: Session token à utiliser pour cette requête.

        Raises:
            RuntimeError: Si l'objet n'a pas d'objectId.
            ParseError: Si le serveur retourne une erreur.
        """
        if not self.object_id:
            raise RuntimeError("Impossible de supprimer un objet sans objectId")

        client = get_client()
        path = f"/classes/{self.class_name}/{self.object_id}"
        await client.delete(
            path, use_master_key=use_master_key, session_token=session_token
        )

        self.object_id = None
        self._data.clear()
        self._dirty_keys.clear()

    def delete_sync(
        self, use_master_key: bool = False, session_token: str | None = None
    ) -> None:
        """Version synchrone de `delete()`.

        Args:
            use_master_key: Utilise le Master Key si True.
            session_token: Session token à utiliser pour cette requête.

        Raises:
            RuntimeError: Si l'objet n'a pas d'objectId.
        """
        if not self.object_id:
            raise RuntimeError("Impossible de supprimer un objet sans objectId")

        client = get_client()
        path = f"/classes/{self.class_name}/{self.object_id}"
        client.delete_sync(
            path, use_master_key=use_master_key, session_token=session_token
        )

        self.object_id = None
        self._data.clear()
        self._dirty_keys.clear()

    def increment(self, key: str, amount: int = 1) -> ParseObject:
        """Incrémente un champ numérique.

        Args:
            key: Le nom du champ.
            amount: La valeur à ajouter (défaut: 1).

        Returns:
            L'instance actuelle (pour le chaînage).
        """
        from ._types import Increment

        return self.set(key, Increment(amount))

    def add_to_array(self, key: str, values: list[Any]) -> ParseObject:
        """Ajoute des éléments à un champ tableau.

        Args:
            key: Le nom du champ.
            values: Liste des valeurs à ajouter.

        Returns:
            L'instance actuelle (pour le chaînage).
        """
        from ._types import AddToArray

        return self.set(key, AddToArray(values))

    def add_unique(self, key: str, values: list[Any]) -> ParseObject:
        """Ajoute des éléments à un tableau seulement s'ils sont absents.

        Args:
            key: Le nom du champ.
            values: Liste des valeurs à ajouter.

        Returns:
            L'instance actuelle (pour le chaînage).
        """
        from ._types import AddUniqueToArray

        return self.set(key, AddUniqueToArray(values))

    def remove_from_array(self, key: str, values: list[Any]) -> ParseObject:
        """Supprime des éléments d'un champ tableau.

        Args:
            key: Le nom du champ.
            values: Liste des éléments à supprimer.

        Returns:
            L'instance actuelle (pour le chaînage).
        """
        from ._types import RemoveFromArray

        return self.set(key, RemoveFromArray(values))

    def unset(self, key: str) -> ParseObject:
        """Supprime un champ de l'objet.

        Args:
            key: Le nom du champ à supprimer.

        Returns:
            L'instance actuelle (pour le chaînage).
        """
        from ._types import DeleteField

        return self.set(key, DeleteField())
