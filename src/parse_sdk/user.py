"""ParseUser class for user authentication operations.

This module provides the ParseUser class which inherits from ParseObject
and adds authentication capabilities like sign_up, log_in, log_out, and
password reset functionality.
"""

from __future__ import annotations

from typing import Any

from .client import get_client
from .object import ParseObject


class ParseUser(ParseObject):
    """ParseUser inherits from ParseObject and provides authentication operations.

    ParseUser represents a user object in Parse Server. It extends ParseObject
    with authentication methods like sign_up, log_in, log_out, and password reset.

    The _User class in Parse Server has predefined fields:
        - username (required, unique)
        - password (required)
        - email (optional, unique if provided)
        - session_token (set after login/signup)

    Attributes:
        username: The user's unique username.
        password: The user's password (write-only, not returned by server).
        email: The user's email address.
        session_token: The session token after successful login/signup.

    Example:
        >>> user = ParseUser()
        >>> user.username = "alice"
        >>> user.password = "s3cr3t!"
        >>> user.email = "alice@example.com"
        >>> user.sign_up()

        >>> # Login
        >>> user = ParseUser.log_in("alice", "s3cr3t!")

        >>> # Logout
        >>> ParseUser.log_out()
    """

    def __init__(self) -> None:
        """Initialize a ParseUser instance."""
        super().__init__(class_name="_User")

    # ------------------------------------------------------------------
    # Properties for user fields
    # ------------------------------------------------------------------

    @property
    def username(self) -> str | None:
        """Get the username."""
        return self.get("username")

    @username.setter
    def username(self, value: str) -> None:
        """Set the username."""
        self.set("username", value)

    @property
    def password(self) -> str | None:
        """Get the password (note: server never returns actual password)."""
        return self.get("password")

    @password.setter
    def password(self, value: str) -> None:
        """Set the password."""
        self.set("password", value)

    @property
    def email(self) -> str | None:
        """Get the email address."""
        return self.get("email")

    @email.setter
    def email(self, value: str) -> None:
        """Set the email address."""
        self.set("email", value)

    @property
    def session_token(self) -> str | None:
        """Get the session token."""
        return self.get("sessionToken")

    # ------------------------------------------------------------------
    # Sign Up
    # ------------------------------------------------------------------

    def sign_up(self) -> None:
        """Register a new user on Parse Server.

        Creates a new user account with the provided username, password,
        and optional email. After successful signup, the user's object_id
        and session_token will be populated.

        Raises:
            ParseUsernameTakenError: If username is already taken (code 202).
            ParseEmailTakenError: If email is already taken (code 203).
            ParseInvalidParameterError: If required fields are missing.
        """
        client = get_client()

        data: dict[str, Any] = {
            "username": self.username,
            "password": self.password,
        }
        if self.email:
            data["email"] = self.email

        # Add any additional fields
        for key, value in self._data.items():
            if key not in data and key not in ("sessionToken", "password"):
                data[key] = value

        # POST /users (not /classes/_User)
        response = client.request_sync("POST", "/users", json=data)

        # Update self with response data
        if "objectId" in response:
            self._object_id = response["objectId"]
        if "sessionToken" in response:
            self._data["sessionToken"] = response["sessionToken"]
        if "createdAt" in response:
            self._data["createdAt"] = response["createdAt"]

        # Set session token on client for subsequent requests
        if self.session_token:
            client.set_session_token(self.session_token)

    # ------------------------------------------------------------------
    # Log In (classmethod)
    # ------------------------------------------------------------------

    @classmethod
    def log_in(cls, username: str, password: str) -> ParseUser:
        """Authenticate a user with username and password.

        Note: The /login endpoint expects form-encoded data, NOT JSON!

        Args:
            username: The user's username.
            password: The user's password.

        Returns:
            ParseUser: An authenticated ParseUser instance with session_token.
        """
        client = get_client()

        # ⚠️ CRITICAL: /login expects form-encoded data, NOT JSON!
        response = client.request_sync(
            "POST",
            "/login",
            data={"username": username, "password": password},
            content_type="application/x-www-form-urlencoded",
        )

        user = cls()

        if "objectId" in response:
            user._object_id = response["objectId"]
        if "sessionToken" in response:
            user._data["sessionToken"] = response["sessionToken"]
        if "username" in response:
            user._data["username"] = response["username"]
        if "email" in response:
            user._data["email"] = response["email"]
        if "createdAt" in response:
            user._data["createdAt"] = response["createdAt"]
        if "updatedAt" in response:
            user._data["updatedAt"] = response["updatedAt"]

        # Set session token on client
        if user.session_token:
            client.set_session_token(user.session_token)

        return user

    # ------------------------------------------------------------------
    # Log Out (classmethod)
    # ------------------------------------------------------------------

    @classmethod
    def log_out(cls) -> None:
        """Log out the current user.

        Clears the session token on the client side and notifies Parse Server
        to invalidate the session.
        """
        client = get_client()
        session_token = client.session_token

        if session_token:
            client.request_sync(
                "POST",
                "/logout",
                session_token=session_token,
            )
            client.clear_session_token()

    # ------------------------------------------------------------------
    # Password Reset (classmethod)
    # ------------------------------------------------------------------

    @classmethod
    def request_password_reset(cls, email: str) -> None:
        """Request a password reset email.

        Sends a password reset email to the specified email address.

        Args:
            email: The email address to send the reset link to.
        """
        client = get_client()

        client.request_sync(
            "POST",
            "/requestPasswordReset",
            json={"email": email},
        )

    # ------------------------------------------------------------------
    # Async versions
    # ------------------------------------------------------------------

    async def sign_up_async(self) -> None:
        """Async version of sign_up()."""
        client = get_client()

        data: dict[str, Any] = {
            "username": self.username,
            "password": self.password,
        }
        if self.email:
            data["email"] = self.email

        for key, value in self._data.items():
            if key not in data and key not in ("sessionToken", "password"):
                data[key] = value

        response = await client.request("POST", "/users", json=data)

        if "objectId" in response:
            self._object_id = response["objectId"]
        if "sessionToken" in response:
            self._data["sessionToken"] = response["sessionToken"]
        if "createdAt" in response:
            self._data["createdAt"] = response["createdAt"]

        if self.session_token:
            client.set_session_token(self.session_token)

    @classmethod
    async def log_in_async(cls, username: str, password: str) -> ParseUser:
        """Async version of log_in()."""
        client = get_client()

        response = await client.request(
            "POST",
            "/login",
            data={"username": username, "password": password},
            content_type="application/x-www-form-urlencoded",
        )

        user = cls()

        if "objectId" in response:
            user._object_id = response["objectId"]
        if "sessionToken" in response:
            user._data["sessionToken"] = response["sessionToken"]
        if "username" in response:
            user._data["username"] = response["username"]
        if "email" in response:
            user._data["email"] = response["email"]

        if user.session_token:
            client.set_session_token(user.session_token)

        return user

    @classmethod
    async def log_out_async(cls) -> None:
        """Async version of log_out()."""
        client = get_client()
        session_token = client.session_token

        if session_token:
            await client.request(
                "POST",
                "/logout",
                session_token=session_token,
            )
            client.clear_session_token()

    @classmethod
    async def request_password_reset_async(cls, email: str) -> None:
        """Async version of request_password_reset()."""
        client = get_client()

        await client.request(
            "POST",
            "/requestPasswordReset",
            json={"email": email},
        )
