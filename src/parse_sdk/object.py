"""
Module ParseObject — CRUD et gestion des données.

Ce module fournit la classe ParseObject qui représente un objet stocké
sur Parse Server. Elle permet de lire, modifier et sauvegarder des données.
"""

from __future__ import annotations

from typing import Any

from ._types import encode_parse_value
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

        # Données internes de l'objet
        self._data: dict[str, Any] = {}

        # Liste des clés modifiées localement qui doivent être envoyées au serveur
        self._dirty_keys: set[str] = set()

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère la valeur d'un champ.

        Args:
            key: Le nom du champ.
            default: Valeur par défaut si le champ n'existe pas.

        Returns:
            La valeur du champ (décodée si type spécial Parse).
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> ParseObject:
        """Définit la valeur d'un champ.

        Args:
            key: Le nom du champ.
            value: La valeur à enregistrer.

        Returns:
            L'instance actuelle (pour le chaînage).
        """
        # On encode la valeur (ex: datetime -> ParseDate)
        encoded_value = encode_parse_value(value)

        self._data[key] = value
        self._dirty_keys.add(key)

        return self

    async def save(
        self, use_master_key: bool = False, session_token: str | None = None
    ) -> None:
        """Sauvegarde l'objet sur Parse Server.

        Cette méthode envoie uniquement les champs modifiés (dirty).
        """
        if not self._dirty_keys:
            return

        # Construction du payload (données à envoyer)
        payload = {key: encode_parse_value(self._data[key]) for key in self._dirty_keys}

        client = get_client()

        if self.object_id:
            # Mise à jour (PUT)
            path = f"/classes/{self.class_name}/{self.object_id}"
            response = await client.put(
                path,
                json=payload,
                use_master_key=use_master_key,
                session_token=session_token,
            )
        else:
            # Création (POST)
            path = f"/classes/{self.class_name}"
            response = await client.post(
                path,
                json=payload,
                use_master_key=use_master_key,
                session_token=session_token,
            )

            # On récupère l'objectId généré par le serveur
            if "objectId" in response:
                self.object_id = response["objectId"]

        # Une fois sauvegardé, l'objet n'est plus "dirty"
        self._dirty_keys.clear()

    # --- MÉTHODES À IMPLÉMENTER POUR L'ISSUE #17 ---

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
