from unittest.mock import MagicMock, patch

import pytest

from parse_sdk import ParseObject
from parse_sdk._types import (
    AddToArray,
    AddUniqueToArray,
    DeleteField,
    GeoPoint,
    Increment,
    Pointer,
    RemoveFromArray,
)


def test_object_initialization():
    obj = ParseObject("GameScore")
    assert obj.class_name == "GameScore"
    assert obj.object_id is None

    obj_with_id = ParseObject("GameScore", "abc123")
    assert obj_with_id.object_id == "abc123"


def test_object_set_get():
    obj = ParseObject("GameScore")
    obj.set("playerName", "Alice")
    assert obj.get("playerName") == "Alice"
    assert obj.get("nonExistent", "default") == "default"


def test_object_increment():
    obj = ParseObject("GameScore")
    result = obj.increment("score", 5)

    # Vérifie le chaînage
    assert result == obj
    # Vérifie que la valeur stockée est un objet Increment
    val = obj.get("score")
    assert isinstance(val, Increment)
    assert val.amount == 5
    # Vérifie que le champ est marqué comme modifié
    assert "score" in obj._dirty_keys


def test_object_add_to_array():
    obj = ParseObject("GameScore")
    obj.add_to_array("tags", ["python", "sdk"])

    val = obj.get("tags")
    assert isinstance(val, AddToArray)
    assert val.objects == ["python", "sdk"]
    assert "tags" in obj._dirty_keys


def test_object_add_unique():
    obj = ParseObject("GameScore")
    obj.add_unique("skills", ["async"])

    val = obj.get("skills")
    assert isinstance(val, AddUniqueToArray)
    assert val.objects == ["async"]


def test_object_remove_from_array():
    obj = ParseObject("GameScore")
    obj.remove_from_array("tags", ["old"])

    val = obj.get("tags")
    assert isinstance(val, RemoveFromArray)
    assert val.objects == ["old"]


def test_object_unset():
    obj = ParseObject("GameScore")
    obj.unset("temporaryField")

    val = obj.get("temporaryField")
    assert isinstance(val, DeleteField)


def test_object_chaining():
    obj = ParseObject("GameScore")
    result = obj.increment("score").add_to_array("tags", ["test"]).unset("old")
    assert result == obj


@pytest.mark.asyncio
async def test_object_save_dirty_tracking():
    # On mocke get_client pour ne pas faire de vraie requête réseau
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()

        # On définit une fonction asynchrone pour simuler l'appel réseau
        async def mock_post(*_args, **_kwargs):
            return {"objectId": "newId", "createdAt": "..."}

        mock_http.post.side_effect = mock_post
        mock_get_client.return_value = mock_http

        obj = ParseObject("GameScore")
        obj.set("score", 100)
        assert len(obj._dirty_keys) == 1

        await obj.save()

        # Après sauvegarde, les dirty_keys doivent être vides
        assert len(obj._dirty_keys) == 0
        assert obj.object_id == "newId"
        assert obj.get("score") == 100


@pytest.mark.asyncio
async def test_object_fetch():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()

        async def mock_get(*_args, **_kwargs):
            return {"objectId": "abc", "playerName": "Bob", "score": 500}

        mock_http.get.side_effect = mock_get
        mock_get_client.return_value = mock_http

        obj = ParseObject("GameScore", "abc")
        obj.set("score", 100)  # Modification locale
        assert len(obj._dirty_keys) == 1

        await obj.fetch()

        assert obj.get("playerName") == "Bob"
        assert obj.get("score") == 500
        assert len(obj._dirty_keys) == 0


@pytest.mark.asyncio
async def test_object_delete():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()

        async def mock_delete(*_args, **_kwargs):
            return {}

        mock_http.delete.side_effect = mock_delete
        mock_get_client.return_value = mock_http

        obj = ParseObject("GameScore", "abc")
        await obj.delete()

        assert obj.object_id is None
        assert obj._data == {}
        mock_http.delete.assert_called_once()


@pytest.mark.asyncio
async def test_object_save_with_geopoint():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()
        async def mock_post(_path, json, **_kwargs):
            assert json["location"]["__type"] == "GeoPoint"
            assert json["location"]["latitude"] == 48.8566
            return {"objectId": "geoId"}

        mock_http.post.side_effect = mock_post
        mock_get_client.return_value = mock_http

        obj = ParseObject("Place")
        obj.set("location", GeoPoint(48.8566, 2.3522))
        await obj.save()

        assert obj.object_id == "geoId"


@pytest.mark.asyncio
async def test_object_save_with_pointer():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()
        async def mock_post(_path, json, **_kwargs):
            assert json["owner"]["__type"] == "Pointer"
            assert json["owner"]["className"] == "_User"
            assert json["owner"]["objectId"] == "user123"
            return {"objectId": "postId"}

        mock_http.post.side_effect = mock_post
        mock_get_client.return_value = mock_http

        obj = ParseObject("Post")
        obj.set("owner", Pointer("_User", "user123"))
        await obj.save()

        assert obj.object_id == "postId"
