import pytest
from unittest.mock import MagicMock, patch

from parse_sdk import ParseObject, GeoPoint, Pointer
from parse_sdk._types import Increment, AddToArray, AddUniqueToArray, RemoveFromArray, DeleteField

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
    result = (
        obj.increment("score")
           .add_to_array("tags", ["test"])
           .unset("old")
    )
    assert result == obj

@pytest.mark.asyncio
async def test_object_save_dirty_tracking():
    # On mocke get_client pour ne pas faire de vraie requête réseau
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()
        
        # On définit une fonction asynchrone pour simuler l'appel réseau
        async def mock_post(*args, **kwargs):
            return {"objectId": "newId", "createdAt": "..."}
            
        mock_http.post = mock_post
        mock_get_client.return_value = mock_http
        
        obj = ParseObject("GameScore")
        obj.set("score", 100)
        assert len(obj._dirty_keys) == 1
        
        await obj.save()
        
        # Après sauvegarde, les dirty_keys doivent être vides
        assert len(obj._dirty_keys) == 0
        assert obj.object_id == "newId"
