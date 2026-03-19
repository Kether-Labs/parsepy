"""
Tests unitaires pour _types.py et exceptions.py.

Ces tests ne nécessitent aucun serveur Parse — ils testent uniquement
la logique de sérialisation/désérialisation et la hiérarchie d'exceptions.

Lancez avec : pytest tests/unit/test_types_and_exceptions.py -v
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone

import pytest

from parse_sdk._types import (
    AddToArray,
    AddUniqueToArray,
    DeleteField,
    GeoPoint,
    Increment,
    ParseBytes,
    ParseDate,
    Pointer,
    RemoveFromArray,
    decode_parse_value,
    encode_parse_value,
)
from parse_sdk.exceptions import (
    ParseError,
    ParseObjectNotFoundError,
    ParseSessionExpiredError,
    ParseUsernameTakenError,
    raise_parse_error,
)


# ---------------------------------------------------------------------------
# GeoPoint
# ---------------------------------------------------------------------------

class TestGeoPoint:
    def test_to_parse(self) -> None:
        gp = GeoPoint(latitude=48.8566, longitude=2.3522)
        assert gp.to_parse() == {
            "__type": "GeoPoint",
            "latitude": 48.8566,
            "longitude": 2.3522,
        }

    def test_from_parse(self) -> None:
        data = {"__type": "GeoPoint", "latitude": 48.8566, "longitude": 2.3522}
        gp = GeoPoint.from_parse(data)
        assert gp.latitude == 48.8566
        assert gp.longitude == 2.3522

    def test_roundtrip(self) -> None:
        gp = GeoPoint(latitude=0.0, longitude=0.0)
        assert GeoPoint.from_parse(gp.to_parse()) == gp

    def test_invalid_latitude(self) -> None:
        with pytest.raises(ValueError, match="Latitude"):
            GeoPoint(latitude=91.0, longitude=0.0)

    def test_invalid_longitude(self) -> None:
        with pytest.raises(ValueError, match="Longitude"):
            GeoPoint(latitude=0.0, longitude=181.0)

    def test_equality(self) -> None:
        assert GeoPoint(1.0, 2.0) == GeoPoint(1.0, 2.0)
        assert GeoPoint(1.0, 2.0) != GeoPoint(1.0, 3.0)


# ---------------------------------------------------------------------------
# Pointer
# ---------------------------------------------------------------------------

class TestPointer:
    def test_to_parse(self) -> None:
        ptr = Pointer(class_name="Post", object_id="abc123")
        assert ptr.to_parse() == {
            "__type": "Pointer",
            "className": "Post",
            "objectId": "abc123",
        }

    def test_from_parse(self) -> None:
        data = {"__type": "Pointer", "className": "Post", "objectId": "abc123"}
        ptr = Pointer.from_parse(data)
        assert ptr.class_name == "Post"
        assert ptr.object_id == "abc123"

    def test_roundtrip(self) -> None:
        ptr = Pointer("GameScore", "xyz999")
        assert Pointer.from_parse(ptr.to_parse()) == ptr


# ---------------------------------------------------------------------------
# ParseDate
# ---------------------------------------------------------------------------

class TestParseDate:
    def test_to_parse_utc(self) -> None:
        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        pd = ParseDate(dt)
        result = pd.to_parse()
        assert result["__type"] == "Date"
        assert result["iso"].startswith("2024-01-15T12:00:00")
        assert result["iso"].endswith("Z")

    def test_from_parse(self) -> None:
        data = {"__type": "Date", "iso": "2024-01-15T12:00:00.000Z"}
        pd = ParseDate.from_parse(data)
        assert pd.value.year == 2024
        assert pd.value.month == 1
        assert pd.value.day == 15

    def test_naive_datetime_treated_as_utc(self) -> None:
        dt = datetime(2024, 6, 1, 0, 0, 0)
        pd = ParseDate(dt)
        assert pd.value.tzinfo is not None


# ---------------------------------------------------------------------------
# ParseBytes
# ---------------------------------------------------------------------------

class TestParseBytes:
    def test_to_parse(self) -> None:
        data = b"hello"
        pb = ParseBytes(data)
        result = pb.to_parse()
        assert result["__type"] == "Bytes"
        assert result["base64"] == base64.b64encode(data).decode()

    def test_from_parse(self) -> None:
        encoded = base64.b64encode(b"world").decode()
        pb = ParseBytes.from_parse({"__type": "Bytes", "base64": encoded})
        assert pb.data == b"world"

    def test_roundtrip(self) -> None:
        pb = ParseBytes(b"\x00\xff\xaa")
        assert ParseBytes.from_parse(pb.to_parse()) == pb


# ---------------------------------------------------------------------------
# Opérations atomiques
# ---------------------------------------------------------------------------

class TestAtomicOps:
    def test_increment(self) -> None:
        assert Increment(10).to_parse() == {"__op": "Increment", "amount": 10}
        assert Increment().to_parse() == {"__op": "Increment", "amount": 1}

    def test_add_to_array(self) -> None:
        op = AddToArray(["a", "b"])
        assert op.to_parse() == {"__op": "Add", "objects": ["a", "b"]}

    def test_add_unique(self) -> None:
        op = AddUniqueToArray(["x"])
        assert op.to_parse() == {"__op": "AddUnique", "objects": ["x"]}

    def test_remove_from_array(self) -> None:
        op = RemoveFromArray(["old"])
        assert op.to_parse() == {"__op": "Remove", "objects": ["old"]}

    def test_delete_field(self) -> None:
        assert DeleteField().to_parse() == {"__op": "Delete"}


# ---------------------------------------------------------------------------
# decode_parse_value / encode_parse_value
# ---------------------------------------------------------------------------

class TestCodecFunctions:
    def test_decode_geopoint(self) -> None:
        raw = {"__type": "GeoPoint", "latitude": 10.0, "longitude": 20.0}
        result = decode_parse_value(raw)
        assert isinstance(result, GeoPoint)
        assert result.latitude == 10.0

    def test_decode_pointer(self) -> None:
        raw = {"__type": "Pointer", "className": "Post", "objectId": "x"}
        result = decode_parse_value(raw)
        assert isinstance(result, Pointer)

    def test_decode_primitive_passthrough(self) -> None:
        assert decode_parse_value(42) == 42
        assert decode_parse_value("hello") == "hello"
        assert decode_parse_value(None) is None

    def test_encode_geopoint(self) -> None:
        gp = GeoPoint(1.0, 2.0)
        assert encode_parse_value(gp) == gp.to_parse()

    def test_encode_list(self) -> None:
        lst = [GeoPoint(0.0, 0.0), "text", 42]
        result = encode_parse_value(lst)
        assert isinstance(result[0], dict)
        assert result[1] == "text"
        assert result[2] == 42

    def test_encode_datetime(self) -> None:
        dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        result = encode_parse_value(dt)
        assert result["__type"] == "Date"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TestExceptions:
    def test_parse_error_base(self) -> None:
        err = ParseError(code=999, message="test error")
        assert err.code == 999
        assert err.message == "test error"
        assert "999" in str(err)

    def test_object_not_found(self) -> None:
        err = ParseObjectNotFoundError("GameScore", "abc")
        assert err.code == 101
        assert "GameScore" in err.message
        assert "abc" in err.message

    def test_session_expired(self) -> None:
        err = ParseSessionExpiredError()
        assert err.code == 209

    def test_username_taken(self) -> None:
        err = ParseUsernameTakenError("alice")
        assert err.code == 202
        assert "alice" in err.message

    def test_raise_parse_error_known_code(self) -> None:
        with pytest.raises(ParseSessionExpiredError):
            raise_parse_error(209, "Session expired")

    def test_raise_parse_error_unknown_code(self) -> None:
        with pytest.raises(ParseError) as exc_info:
            raise_parse_error(9999, "Unknown error")
        assert exc_info.value.code == 9999

    def test_exception_hierarchy(self) -> None:
        err = ParseSessionExpiredError()
        assert isinstance(err, ParseError)
        assert isinstance(err, Exception)
