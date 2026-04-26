"""
Unit tests for ParseObject.

Uses respx to mock HTTP requests.
"""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from parse_sdk import ParseObject


class TestParseObjectInit:
    """Initialization tests."""

    def test_init_with_class_name(self) -> None:
        """ParseObject initializes with a class_name."""
        obj = ParseObject("GameScore")
        assert obj.class_name == "GameScore"
        assert obj.object_id is None

    def test_init_with_object_id(self) -> None:
        """ParseObject can be initialized with an object_id."""
        obj = ParseObject("GameScore", object_id="abc123")
        assert obj.object_id == "abc123"


class TestParseObjectGetSet:
    """Testing get/set methods."""

    def test_set_and_get(self) -> None:
        """set() and get() work correctly."""
        obj = ParseObject("GameScore")
        obj.set("player", "Alice")
        obj.set("score", 100)

        assert obj.get("player") == "Alice"
        assert obj.get("score") == 100

    def test_get_with_default(self) -> None:
        """get() returns the default value if the field does not exist."""
        obj = ParseObject("GameScore")
        assert obj.get("unknown") is None
        assert obj.get("unknown", "default") == "default"


class TestParseObjectSave:
    """Testing save() method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_save_creates_object(self) -> None:
        """save() creates a new object via POST."""
        respx.post("/classes/GameScore").mock(
            return_value=Response(
                201,
                json={
                    "objectId": "abc123",
                    "createdAt": "2024-01-15T12:00:00.000Z",
                },
            )
        )

        obj = ParseObject("GameScore")
        obj.set("player", "Alice")
        obj.set("score", 100)

        await obj.save()

        assert obj.object_id == "abc123"
        assert obj.created_at is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_save_updates_object(self) -> None:
        """save() met à jour un objet existant via PUT."""
        # Mock la réponse PUT
        respx.put("/classes/GameScore/abc123").mock(
            return_value=Response(
                200,
                json={
                    "updatedAt": "2024-01-16T12:00:00.000Z",
                },
            )
        )

        obj = ParseObject("GameScore", object_id="abc123")
        obj.set("score", 200)

        await obj.save()

        assert obj.updated_at is not None


class TestParseObjectFetch:
    """Tests de la méthode fetch()."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_loads_object(self) -> None:
        """fetch() charge les données depuis le serveur."""
        respx.get("/classes/GameScore/abc123").mock(
            return_value=Response(
                200,
                json={
                    "objectId": "abc123",
                    "player": "Alice",
                    "score": 100,
                    "createdAt": "2024-01-15T12:00:00.000Z",
                    "updatedAt": "2024-01-15T12:00:00.000Z",
                },
            )
        )

        obj = ParseObject("GameScore", object_id="abc123")
        await obj.fetch()

        assert obj.get("player") == "Alice"
        assert obj.get("score") == 100

    def test_fetch_requires_object_id(self) -> None:
        """fetch() lève ValueError si object_id est None."""
        obj = ParseObject("GameScore")

        with pytest.raises(ValueError, match="object_id"):
            import asyncio

            asyncio.get_event_loop().run_until_complete(obj.fetch())


class TestParseObjectDelete:
    """Tests of the delete() method."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_delete_removes_object(self) -> None:
        """delete() removes the object."""
        respx.delete("/classes/GameScore/abc123").mock(
            return_value=Response(200, json={})
        )

        obj = ParseObject("GameScore", object_id="abc123")
        await obj.delete()

        assert obj.object_id is None

    def test_delete_requires_object_id(self) -> None:
        """delete() raises ValueError if object_id is None."""
        obj = ParseObject("GameScore")

        with pytest.raises(ValueError, match="object_id"):
            import asyncio

            asyncio.get_event_loop().run_until_complete(obj.delete())


class TestParseObjectSync:
    """Tests of the sync versions."""

    @respx.mock
    def test_save_sync(self) -> None:
        """save_sync() works."""
        respx.post("/classes/GameScore").mock(
            return_value=Response(
                201,
                json={
                    "objectId": "abc123",
                    "createdAt": "2024-01-15T12:00:00.000Z",
                },
            )
        )

        obj = ParseObject("GameScore")
        obj.set("player", "Alice")
        obj.save_sync()

        assert obj.object_id == "abc123"

    @respx.mock
    def test_fetch_sync(self) -> None:
        """fetch_sync() works."""
        respx.get("/classes/GameScore/abc123").mock(
            return_value=Response(
                200,
                json={
                    "objectId": "abc123",
                    "player": "Alice",
                    "createdAt": "2024-01-15T12:00:00.000Z",
                },
            )
        )

        obj = ParseObject("GameScore", object_id="abc123")
        obj.fetch_sync()

        assert obj.get("player") == "Alice"

    @respx.mock
    def test_delete_sync(self) -> None:
        """delete_sync() fonctionne."""
        respx.delete("/classes/GameScore/abc123").mock(
            return_value=Response(200, json={})
        )

        obj = ParseObject("GameScore", object_id="abc123")
        obj.delete_sync()

        assert obj.object_id is None
