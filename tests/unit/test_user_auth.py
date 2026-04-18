"""Unit tests for ParseUser authentication operations."""

import pytest
import respx
from httpx import Response

from parse_sdk import ParseClient, ParseUser
from parse_sdk.client import get_client
from parse_sdk.exceptions import ParseUsernameTakenError, ParseEmailTakenError


@pytest.fixture(autouse=True)
def setup_client():
    """Setup a fresh ParseClient for each test."""
    client = ParseClient(
        app_id="test_app_id",
        rest_key="test_api_key",
        server_url="https://parse.example.com/parse",
    )
    yield get_client()


class TestParseUserProperties:
    """Tests for ParseUser property accessors."""
    
    def test_username_property(self, setup_client):
        """Test setting and getting username."""
        user = ParseUser()
        user.username = "alice"
        assert user.username == "alice"
        assert user["username"] == "alice"
    
    def test_password_property(self, setup_client):
        """Test setting and getting password."""
        user = ParseUser()
        user.password = "secret123"
        assert user.password == "secret123"
    
    def test_email_property(self, setup_client):
        """Test setting and getting email."""
        user = ParseUser()
        user.email = "alice@example.com"
        assert user.email == "alice@example.com"
    
    def test_session_token_property(self, setup_client):
        """Test getting session token."""
        user = ParseUser()
        user._data["sessionToken"] = "r:abc123"
        assert user.session_token == "r:abc123"


class TestSignUp:
    """Tests for user registration."""
    
    @respx.mock
    def test_sign_up_success(self, setup_client):
        """Test successful user signup."""
        respx.post("https://parse.example.com/parse/users").mock(
            return_value=Response(
                201,
                json={
                    "objectId": "user123",
                    "sessionToken": "r:abc123",
                    "createdAt": "2026-04-18T10:00:00.000Z",
                }
            )
        )
        
        user = ParseUser()
        user.username = "alice"
        user.password = "secret123"
        user.email = "alice@example.com"
        user.sign_up()
        
        assert user.object_id == "user123"
        assert user.session_token == "r:abc123"
        assert user["createdAt"] == "2026-04-18T10:00:00.000Z"
    
    @respx.mock
    def test_sign_up_username_taken(self, setup_client):
        """Test signup with taken username raises error."""
        respx.post("https://parse.example.com/parse/users").mock(
            return_value=Response(
                400,
                json={
                    "code": 202,
                    "error": "username alice already taken",
                }
            )
        )
        
        user = ParseUser()
        user.username = "alice"
        user.password = "secret123"
        
        with pytest.raises(ParseUsernameTakenError):
            user.sign_up()
    
    @respx.mock
    def test_sign_up_email_taken(self, setup_client):
        """Test signup with taken email raises error."""
        respx.post("https://parse.example.com/parse/users").mock(
            return_value=Response(
                400,
                json={
                    "code": 203,
                    "error": "email already taken",
                }
            )
        )
        
        user = ParseUser()
        user.username = "alice"
        user.password = "secret123"
        user.email = "taken@example.com"
        
        with pytest.raises(ParseEmailTakenError):
            user.sign_up()


class TestLogIn:
    """Tests for user login."""
    
    @respx.mock
    def test_log_in_success(self, setup_client):
        """Test successful login returns user with session token."""
        respx.post("https://parse.example.com/parse/login").mock(
            return_value=Response(
                200,
                json={
                    "objectId": "user123",
                    "sessionToken": "r:xyz789",
                    "username": "alice",
                    "email": "alice@example.com",
                    "createdAt": "2026-04-18T10:00:00.000Z",
                    "updatedAt": "2026-04-18T11:00:00.000Z",
                }
            )
        )
        
        user = ParseUser.log_in("alice", "secret123")
        
        assert user.object_id == "user123"
        assert user.session_token == "r:xyz789"
        assert user.username == "alice"
        assert user.email == "alice@example.com"
    
    @respx.mock
    def test_log_in_uses_form_encoded(self, setup_client):
        """Test that login uses form-encoded data, not JSON."""
        request_made = []
        
        def capture_request(request):
            request_made.append(request)
            return Response(
                200,
                json={
                    "objectId": "user123",
                    "sessionToken": "r:xyz789",
                    "username": "alice",
                }
            )
        
        respx.post("https://parse.example.com/parse/login").mock(
            side_effect=capture_request
        )
        
        ParseUser.log_in("alice", "secret123")
        
        # Verify form-encoded content type
        assert len(request_made) == 1
        content_type = request_made[0].headers.get("content-type", "")
        assert "application/x-www-form-urlencoded" in content_type


class TestLogOut:
    """Tests for user logout."""
    
    @respx.mock
    def test_log_out_success(self, setup_client):
        """Test successful logout clears session."""
        # First set a session token
        setup_client.set_session_token("r:abc123")
        
        respx.post("https://parse.example.com/parse/logout").mock(
            return_value=Response(200, json={})
        )
        
        ParseUser.log_out()
        
        assert setup_client.session_token is None
    
    def test_log_out_without_session(self, setup_client):
        """Test logout without session does nothing."""
        # No session token set
        if setup_client.session_token:
            setup_client.clear_session_token()
        
        # Should work without error
        ParseUser.log_out()


class TestPasswordReset:
    """Tests for password reset."""
    
    @respx.mock
    def test_request_password_reset_success(self, setup_client):
        """Test successful password reset request."""
        respx.post("https://parse.example.com/parse/requestPasswordReset").mock(
            return_value=Response(200, json={})
        )
        
        # Should not raise any exception
        ParseUser.request_password_reset("alice@example.com")