from unittest.mock import MagicMock, patch

from parse_sdk import ParseObject


def test_object_save_sync():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()
        mock_http.post_sync.return_value = {"objectId": "syncId"}
        mock_get_client.return_value = mock_http

        obj = ParseObject("GameScore")
        obj.set("score", 200)
        obj.save_sync()

        assert obj.object_id == "syncId"
        assert len(obj._dirty_keys) == 0
        mock_http.post_sync.assert_called_once()


def test_object_update_sync():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()
        mock_http.put_sync.return_value = {"updatedAt": "..."}
        mock_get_client.return_value = mock_http

        obj = ParseObject("GameScore", "abc")
        obj.set("score", 300)
        obj.save_sync()

        assert len(obj._dirty_keys) == 0
        mock_http.put_sync.assert_called_once()


def test_object_fetch_sync():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()
        mock_http.get_sync.return_value = {"objectId": "abc", "score": 999}
        mock_get_client.return_value = mock_http

        obj = ParseObject("GameScore", "abc")
        obj.fetch_sync()

        assert obj.get("score") == 999
        mock_http.get_sync.assert_called_once()


def test_object_delete_sync():
    with patch("parse_sdk.object.get_client") as mock_get_client:
        mock_http = MagicMock()
        mock_http.delete_sync.return_value = {}
        mock_get_client.return_value = mock_http

        obj = ParseObject("GameScore", "abc")
        obj.delete_sync()

        assert obj.object_id is None
        mock_http.delete_sync.assert_called_once()
