"""
Types spéciaux de Parse Server.

Parse Server utilise une sérialisation JSON particulière pour représenter
des types qui n'existent pas nativement en JSON (dates, fichiers, geo, etc.).

Chaque type implémente :
- `to_parse()` : sérialise vers le format JSON attendu par l'API Parse REST
- `from_parse()` : désérialise depuis une réponse JSON de Parse Server

Référence : https://docs.parseplatform.org/rest/guide/#data-types
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Classe de base
# ---------------------------------------------------------------------------


class ParseType:
    """Classe de base pour tous les types spéciaux Parse.

    Tout type Parse peut être sérialisé/désérialisé depuis/vers un dict JSON.
    """

    def to_parse(self) -> dict[str, Any]:
        """Sérialise ce type vers le format JSON de l'API Parse REST."""
        raise NotImplementedError

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> ParseType:
        """Désérialise depuis une réponse JSON de Parse Server."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_parse()})"


# ---------------------------------------------------------------------------
# GeoPoint
# ---------------------------------------------------------------------------


class GeoPoint(ParseType):
    """Coordonnées géographiques (latitude, longitude).

    Parse utilise ce type pour les requêtes géospatiales (near, within, etc.).

    Args:
        latitude: Latitude en degrés décimaux (-90 à 90).
        longitude: Longitude en degrés décimaux (-180 à 180).

    Example:
        >>> point = GeoPoint(latitude=48.8566, longitude=2.3522)
        >>> point.to_parse()
        {'__type': 'GeoPoint', 'latitude': 48.8566, 'longitude': 2.3522}
    """

    def __init__(self, latitude: float, longitude: float) -> None:
        if not -90 <= latitude <= 90:
            raise ValueError(
                f"Latitude invalide : {latitude} (doit être entre -90 et 90)"
            )
        if not -180 <= longitude <= 180:
            raise ValueError(
                f"Longitude invalide : {longitude} (doit être entre -180 et 180)"
            )
        self.latitude = latitude
        self.longitude = longitude

    def to_parse(self) -> dict[str, Any]:
        return {
            "__type": "GeoPoint",
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> GeoPoint:
        return cls(latitude=data["latitude"], longitude=data["longitude"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GeoPoint):
            return NotImplemented
        return self.latitude == other.latitude and self.longitude == other.longitude


# ---------------------------------------------------------------------------
# Pointer
# ---------------------------------------------------------------------------


class Pointer(ParseType):
    """Référence vers un autre objet Parse (relation de type clé étrangère).

    Args:
        class_name: Nom de la classe Parse référencée.
        object_id: Identifiant de l'objet référencé.

    Example:
        >>> ptr = Pointer(class_name="Post", object_id="abc123")
        >>> ptr.to_parse()
        {'__type': 'Pointer', 'className': 'Post', 'objectId': 'abc123'}
    """

    def __init__(self, class_name: str, object_id: str) -> None:
        self.class_name = class_name
        self.object_id = object_id

    def to_parse(self) -> dict[str, Any]:
        return {
            "__type": "Pointer",
            "className": self.class_name,
            "objectId": self.object_id,
        }

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> Pointer:
        return cls(class_name=data["className"], object_id=data["objectId"])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pointer):
            return NotImplemented
        return self.class_name == other.class_name and self.object_id == other.object_id


# ---------------------------------------------------------------------------
# ParseDate
# ---------------------------------------------------------------------------


class ParseDate(ParseType):
    """Date et heure au format ISO 8601 avec timezone UTC.

    Parse stocke toutes les dates en UTC. Cette classe facilite la conversion
    entre les objets `datetime` Python et le format JSON de Parse.

    Args:
        value: Objet datetime Python. Si naive (sans timezone), il est
               considéré comme UTC.

    Example:
        >>> from datetime import datetime, timezone
        >>> d = ParseDate(datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc))
        >>> d.to_parse()
        {'__type': 'Date', 'iso': '2024-01-15T12:00:00.000Z'}
    """

    def __init__(self, value: datetime) -> None:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        self.value = value

    def to_parse(self) -> dict[str, Any]:
        iso = (
            self.value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{self.value.microsecond // 1000:03d}Z"
        )
        return {"__type": "Date", "iso": iso}

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> ParseDate:
        iso = data["iso"]
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return cls(dt)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParseDate):
            return NotImplemented
        return self.value == other.value


# ---------------------------------------------------------------------------
# ParseBytes
# ---------------------------------------------------------------------------


class ParseBytes(ParseType):
    """Données binaires encodées en base64.

    Args:
        data: Les données binaires à stocker.

    Example:
        >>> pb = ParseBytes(b"hello world")
        >>> pb.to_parse()
        {'__type': 'Bytes', 'base64': 'aGVsbG8gd29ybGQ='}
    """

    def __init__(self, data: bytes) -> None:
        self.data = data

    def to_parse(self) -> dict[str, Any]:
        return {
            "__type": "Bytes",
            "base64": base64.b64encode(self.data).decode("utf-8"),
        }

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> ParseBytes:
        return cls(base64.b64decode(data["base64"]))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParseBytes):
            return NotImplemented
        return self.data == other.data


# ---------------------------------------------------------------------------
# Opérations atomiques Parse
# ---------------------------------------------------------------------------


class Increment(ParseType):
    """Opération atomique d'incrémentation d'un champ numérique.

    Évite les race conditions lors des mises à jour concurrentes.

    Args:
        amount: Valeur à ajouter (peut être négatif pour décrémenter).

    Example:
        >>> obj.set("score", Increment(10))
        >>> # → {"__op": "Increment", "amount": 10}
    """

    def __init__(self, amount: int | float = 1) -> None:
        self.amount = amount

    def to_parse(self) -> dict[str, Any]:
        return {"__op": "Increment", "amount": self.amount}

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> Increment:
        return cls(amount=data["amount"])


class AddToArray(ParseType):
    """Ajoute des éléments à un champ tableau (avec doublons).

    Args:
        objects: Liste d'éléments à ajouter.

    Example:
        >>> obj.set("tags", AddToArray(["python", "async"]))
        >>> # → {"__op": "Add", "objects": ["python", "async"]}
    """

    def __init__(self, objects: list[Any]) -> None:
        self.objects = objects

    def to_parse(self) -> dict[str, Any]:
        return {"__op": "Add", "objects": self.objects}

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> AddToArray:
        return cls(objects=data["objects"])


class AddUniqueToArray(ParseType):
    """Ajoute des éléments à un tableau seulement s'ils n'y sont pas déjà.

    Args:
        objects: Liste d'éléments à ajouter si absents.

    Example:
        >>> obj.set("tags", AddUniqueToArray(["python"]))
        >>> # → {"__op": "AddUnique", "objects": ["python"]}
    """

    def __init__(self, objects: list[Any]) -> None:
        self.objects = objects

    def to_parse(self) -> dict[str, Any]:
        return {"__op": "AddUnique", "objects": self.objects}

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> AddUniqueToArray:
        return cls(objects=data["objects"])


class RemoveFromArray(ParseType):
    """Supprime des éléments d'un champ tableau.

    Args:
        objects: Liste d'éléments à supprimer.

    Example:
        >>> obj.set("tags", RemoveFromArray(["deprecated"]))
        >>> # → {"__op": "Remove", "objects": ["deprecated"]}
    """

    def __init__(self, objects: list[Any]) -> None:
        self.objects = objects

    def to_parse(self) -> dict[str, Any]:
        return {"__op": "Remove", "objects": self.objects}

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> RemoveFromArray:
        return cls(objects=data["objects"])


class DeleteField(ParseType):
    """Supprime un champ d'un objet Parse.

    Example:
        >>> obj.set("deprecated_field", DeleteField())
        >>> # → {"__op": "Delete"}
    """

    def to_parse(self) -> dict[str, Any]:
        return {"__op": "Delete"}

    @classmethod
    def from_parse(cls, data: dict[str, Any]) -> DeleteField:
        return cls()


# ---------------------------------------------------------------------------
# Désérialiseur automatique
# ---------------------------------------------------------------------------

#: Mapping __type → classe ParseType pour la désérialisation automatique.
_TYPE_MAP: dict[str, type[ParseType]] = {
    "GeoPoint": GeoPoint,
    "Pointer": Pointer,
    "Date": ParseDate,
    "Bytes": ParseBytes,
}

#: Mapping __op → classe ParseType pour les opérations atomiques.
_OP_MAP: dict[str, type[ParseType]] = {
    "Increment": Increment,
    "Add": AddToArray,
    "AddUnique": AddUniqueToArray,
    "Remove": RemoveFromArray,
    "Delete": DeleteField,
}


def decode_parse_value(value: Any) -> Any:
    """Désérialise récursivement une valeur JSON Parse vers les types Python.

    Convertit automatiquement les dicts avec `__type` ou `__op` vers les
    classes ParseType correspondantes. Les autres valeurs sont retournées
    telles quelles.

    Args:
        value: Valeur brute depuis une réponse JSON Parse.

    Returns:
        La valeur convertie : ParseType, datetime, ou valeur primitive.

    Example:
        >>> decode_parse_value({"__type": "GeoPoint", "latitude": 48.8, "longitude": 2.3})
        GeoPoint(latitude=48.8, longitude=2.3)
    """
    if not isinstance(value, dict):
        return value

    if "__type" in value:
        type_cls = _TYPE_MAP.get(value["__type"])
        if type_cls:
            return type_cls.from_parse(value)

    if "__op" in value:
        op_cls = _OP_MAP.get(value["__op"])
        if op_cls:
            return op_cls.from_parse(value)

    return {k: decode_parse_value(v) for k, v in value.items()}


def encode_parse_value(value: Any) -> Any:
    """Sérialise récursivement une valeur Python vers le format JSON Parse.

    Args:
        value: Valeur Python à sérialiser.

    Returns:
        La valeur sérialisée compatible avec l'API Parse REST.
    """
    if isinstance(value, ParseType):
        return value.to_parse()
    if isinstance(value, datetime):
        return ParseDate(value).to_parse()
    if isinstance(value, list):
        return [encode_parse_value(v) for v in value]
    if isinstance(value, dict):
        return {k: encode_parse_value(v) for k, v in value.items()}
    return value
