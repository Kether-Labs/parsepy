"""
Parsepy.

Ce module expose l'API publique du SDK. Importez depuis ici, jamais
depuis les modules internes (préfixés par `_`).

Usage rapide :

    from parse_sdk import ParseClient

    client = ParseClient(
        app_id="myAppId",
        rest_key="myRestKey",
        server_url="https://my-parse.com/parse",
    )

    # Les autres classes seront importables ici au fur et à mesure
    # de leur implémentation dans les phases suivantes :
    #
    # from parse_sdk import ParseObject, ParseQuery, ParseUser
    # from parse_sdk import ParseFile, ParseACL, ParseRole
    # from parse_sdk import GeoPoint, Pointer
"""

from __future__ import annotations

# Types spéciaux — disponibles dès le départ
from ._types import (
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

# Exceptions — toujours disponibles
from .exceptions import (
    ParseAuthenticationError,
    ParseCloudFunctionError,
    ParseCloudFunctionNotFoundError,
    ParseConnectionError,
    ParseDuplicateValueError,
    ParseEmailNotFoundError,
    ParseEmailTakenError,
    ParseError,
    ParseFileError,
    ParseFileNotFoundError,
    ParseInvalidQueryError,
    ParseInvalidValueError,
    ParseLiveQueryError,
    ParseMasterKeyRequiredError,
    ParseObjectNotFoundError,
    ParsePermissionError,
    ParsePushError,
    ParseQueryError,
    ParseRateLimitError,
    ParseSessionExpiredError,
    ParseTimeoutError,
    ParseUsernameTakenError,
)

# NOTE : ParseClient, ParseObject, ParseQuery, ParseUser, ParseFile, etc.
# seront ajoutés ici au fur et à mesure de leur implémentation.
# Chaque contributeur qui implémente un module doit aussi l'exporter ici.

__version__ = "0.1.0-dev"
__author__ = "Parse Server Python SDK Contributors"
__license__ = "MIT"

__all__ = [
    # Version
    "__version__",
    # Types spéciaux
    "GeoPoint",
    "Pointer",
    "ParseDate",
    "ParseBytes",
    "Increment",
    "AddToArray",
    "AddUniqueToArray",
    "RemoveFromArray",
    "DeleteField",
    "decode_parse_value",
    "encode_parse_value",
    # Exceptions
    "ParseError",
    "ParseConnectionError",
    "ParseTimeoutError",
    "ParseAuthenticationError",
    "ParseSessionExpiredError",
    "ParseObjectNotFoundError",
    "ParseDuplicateValueError",
    "ParseInvalidValueError",
    "ParsePermissionError",
    "ParseMasterKeyRequiredError",
    "ParseQueryError",
    "ParseInvalidQueryError",
    "ParseUsernameTakenError",
    "ParseEmailTakenError",
    "ParseEmailNotFoundError",
    "ParseFileError",
    "ParseFileNotFoundError",
    "ParseCloudFunctionError",
    "ParseCloudFunctionNotFoundError",
    "ParseRateLimitError",
    "ParsePushError",
    "ParseLiveQueryError",
]
