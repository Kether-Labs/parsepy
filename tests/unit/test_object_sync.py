"""Unit tests for ParseObject synchronous CRUD operations."""

from unittest.mock import MagicMock, patch

import pytest

from parse_sdk import ParseObject


class TestObjectSaveSync:
    """Tests for ParseObject.save_sync()."""

    def test_object_save_sync_create(self):
        """Test creating a new object synchronously."""
        with patch("parse_sdk.object.get_client") as mock_get_client:
            mock_http = MagicMock()
            mock_http.request_sync.return_value = {
                "objectId": "syncId",
                "createdAt": "2026-04-18T10:00:00.000Z",
            }
            mock_get_client.return_value = mock_http

            obj = ParseObject("GameScore")
            obj.set("score", 200)
            obj.save_sync()

            assert obj.object_id == "syncId"
            mock_http.request_sync.assert_called_once()
            # Verify it was a POST request
            call_args = mock_http.request_sync.call_args
            assert call_args[0][0] == "POST"

    def test_object_save_sync_update(self):
        """Test updating an existing object synchronously."""
        with patch("parse_sdk.object.get_client") as mock_get_client:
            mock_http = MagicMock()
            mock_http.request_sync.return_value = {
                "updatedAt": "2026-04-18T11:00:00.000Z",
            }
            mock_get_client.return_value = mock_http

            obj = ParseObject("GameScore", "abc123")
            obj.set("score", 300)
            obj.save_sync()

            assert len(obj._dirty) == 0
            # Verify it was a PUT request
            call_args = mock_http.request_sync.call_args
            assert call_args[0][0] == "PUT"


class TestObjectFetchSync:
    """Tests for ParseObject.fetch_sync()."""

    def test_object_fetch_sync(self):
        """Test fetching an object synchronously."""
        with patch("parse_sdk.object.get_client") as mock_get_client:
            mock_http = MagicMock()
            mock_http.request_sync.return_value = {
                "objectId": "abc",
                "score": 999,
                "createdAt": "2026-04-18T10:00:00.000Z",
                "updatedAt": "2026-04-18T11:00:00.000Z",
            }
            mock_get_client.return_value = mock_http

            obj = ParseObject("GameScore", "abc")
            obj.fetch_sync()

            assert obj.get("score") == 999
            assert obj.object_id == "abc"
            # Verify it was a GET request
            call_args = mock_http.request_sync.call_args
            assert call_args[0][0] == "GET"

    def test_object_fetch_sync_requires_object_id(self):
        """Test that fetch_sync requires object_id."""
        obj = ParseObject("GameScore")
        
        with pytest.raises(ValueError, match="object_id"):
            obj.fetch_sync()


class TestObjectDeleteSync:
    """Tests for ParseObject.delete_sync()."""

    def test_object_delete_sync(self):
        """Test deleting an object synchronously."""
        with patch("parse_sdk.object.get_client") as mock_get_client:
            mock_http = MagicMock()
            mock_http.request_sync.return_value = {}
            mock_get_client.return_value = mock_http

            obj = ParseObject("GameScore", "abc")
            obj.delete_sync()

            assert obj.object_id is None
            # Verify it was a DELETE request
            call_args = mock_http.request_sync.call_args
            assert call_args[0][0] == "DELETE"

    def test_object_delete_sync_requires_object_id(self):
        """Test that delete_sync requires object_id."""
        obj = ParseObject("GameScore")
        
        with pytest.raises(ValueError, match="object_id"):
            obj.delete_sync()