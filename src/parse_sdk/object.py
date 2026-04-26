"""
ParseObject — Represents a record in a Parse class.

This is the core of the SDK. Each ParseObject corresponds to a row in
a Parse Server table (called a “class”).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from ._types import decode_parse_value, encode_parse_value
from .client import get_client

if TYPE_CHECKING:
    pass


class ParseObject:
    """Represents an object stored in Parse Server.

    ParseObject is the base class for all Parse entities.
    It handles the full CRUD lifecycle: create, read,
    update, and delete.

    Args:
        class_name: Name of the Parse class (e.g., “GameScore”, “_User”).
        object_id: Object ID (optional for new objects).

    Attributes:
        object_id: The object’s unique ID (populated after save()).
        created_at: Creation date (populated after save()).
        updated_at: Last modification date (populated after save()).

    Example:
        >>> obj = ParseObject(“GameScore”)
        >>> obj.set(“player”, “Alice”)
        >>> obj.set(“score”, 100)
        >>> await obj.save()
        >>> print(obj.object_id)  # “Ed1nuqPvcm”
    """

    def __init__(
        self,
        class_name: str,
        object_id: str | None = None,
    ) -> None:
        self._class_name = class_name
        self._object_id = object_id
        self._data: dict[str, Any] = {}
        self._dirty: set[str] = set()

        # System attributes (populated by Parse)
        self.created_at: datetime | None = None
        self.updated_at: datetime | None = None

    @property
    def class_name(self) -> str:
        """Name of the Parse class."""
        return self._class_name

    @property
    def object_id(self) -> str | None:
        """Unique identifier of the object."""
        return self._object_id

    # ------------------------------------------------------------------
    # Access to data
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any | None = None) -> Any:
        """Retrieves the value of a field.

        Args:
            key: Field name.
            default: Default value if the field does not exist.

        Returns:
            The value of the field or the default value.
        """
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Sets the value of a field.

        Args:
            key: Field name.
            value: Value to set.
        """
        self._data[key] = value
        self._dirty.add(key)

    # ------------------------------------------------------------------
    # CRUD Operations - Async
    # ------------------------------------------------------------------

    async def save(self) -> None:
        """Saves the object to Parse Server.

        - If object_id is None → POST (create)
        - Otherwise → PUT (update)

        After save(), the object_id, created_at, and updated_at
        attributes are populated from the server response.

        Raises:
            ParseError: If the request fails.
        """
        client = get_client()

        # Prepare the data to be sent (only the “dirty” fields for PUT)

        if self._object_id:

            data = {k: encode_parse_value(self._data[k]) for k in self._dirty}
            path = f"/classes/{self._class_name}/{self._object_id}"
            response = await client.put(path, json=data)

        else:
            data = {k: encode_parse_value(v) for k, v in self._data.items()}
            path = f"/classes/{self._class_name}"
            response = await client.post(path, json=data)

        self._update_from_response(response)
        self._dirty.clear()

    async def fetch(self) -> None:
        """Loads the object's data from Parse Server.

        Throws:
            ParseObjectNotFoundError: If the object does not exist.
            ValueError: If `object_id` is undefined.
        """
        if not self._object_id:
            raise ValueError("object_id est requis pour fetch()")

        client = get_client()
        path = f"/classes/{self._class_name}/{self._object_id}"
        response = await client.get(path)

        # La réponse contient tous les champs
        self._populate_from_get(response)

    async def delete(self) -> None:
        """Removes the object from the Parse Server.

        Raises:
            ParseObjectNotFoundError: If the object does not exist.
            ValueError: If `object_id` is undefined.
        """
        if not self._object_id:
            raise ValueError("object_id is required for delete()")

        client = get_client()
        path = f"/classes/{self._class_name}/{self._object_id}"
        await client.delete(path)

        # Reset the object
        self._object_id = None
        self._data.clear()
        self._dirty.clear()

    # ------------------------------------------------------------------
    # CRUD Operations - Sync
    # ------------------------------------------------------------------

    def save_sync(self) -> None:
        """Synchronous version of save()."""
        client = get_client()

        if self._object_id:
            data = {k: encode_parse_value(self._data[k]) for k in self._dirty}
            path = f"/classes/{self._class_name}/{self._object_id}"
            response = client.request_sync("PUT", path, json=data)
        else:
            data = {k: encode_parse_value(self._data[k]) for k in self._data}
            path = f"/classes/{self._class_name}"
            response = client.request_sync("POST", path, json=data)

        self._update_from_response(response)
        self._dirty.clear()

    def fetch_sync(self) -> None:
        """Synchronous version of fetch()."""
        if not self._object_id:
            raise ValueError("object_id is required for fetch_sync()")

        client = get_client()
        path = f"/classes/{self._class_name}/{self._object_id}"
        response = client.request_sync("GET", path)

        self._populate_from_get(response)

    def delete_sync(self) -> None:
        """Synchronous version of delete()."""
        if not self._object_id:
            raise ValueError("object_id is required for delete_sync()")

        client = get_client()
        path = f"/classes/{self._class_name}/{self._object_id}"
        client.request_sync("DELETE", path)

        self._object_id = None
        self._data.clear()
        self._dirty.clear()

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _update_from_response(self, response: dict[str, Any]) -> None:
        """Updates the object's attributes from a POST/PUT response."""
        if "objectId" in response:
            self._object_id = response["objectId"]
        if "createdAt" in response:
            self.created_at = decode_parse_value(response["createdAt"])
        if "updatedAt" in response:
            self.updated_at = decode_parse_value(response["updatedAt"])

    def _populate_from_get(self, response: dict[str, Any]) -> None:
        """Populates the object from a GET response."""
        # System fields
        self._object_id = response.get("objectId")
        self.created_at = decode_parse_value(response.get("createdAt"))
        self.updated_at = decode_parse_value(response.get("updatedAt"))

        # Autres champs
        for key, value in response.items():
            if key not in ("objectId", "createdAt", "updatedAt", "className"):
                self._data[key] = decode_parse_value(value)

    def __repr__(self) -> str:
        return f"ParseObject({self._class_name!r}, object_id={self._object_id!r})"
