"""
Hiérarchie d'exceptions du SDK Parse Server Python.

Toutes les exceptions levées par le SDK héritent de ParseError.
Les codes d'erreur correspondent aux codes officiels de Parse Server.

Référence : https://docs.parseplatform.org/dotnet/guide/#error-codes
"""

from __future__ import annotations


class ParseError(Exception):
    """Exception de base pour toutes les erreurs du SDK Parse Server.

    Attributes:
        code: Code d'erreur Parse Server (entier).
        message: Message d'erreur lisible.

    Example:
        >>> try:
        ...     await obj.save()
        ... except ParseError as e:
        ...     print(f"Erreur {e.code}: {e.message}")
    """

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[Parse Error {code}] {message}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message!r})"


# ---------------------------------------------------------------------------
# Erreurs réseau et connexion
# ---------------------------------------------------------------------------

class ParseConnectionError(ParseError):
    """Impossible de joindre le serveur Parse (réseau, timeout, DNS).

    Code : -1 (erreur interne SDK, pas un code Parse officiel).
    """

    def __init__(self, message: str = "Connexion au serveur Parse impossible") -> None:
        super().__init__(code=-1, message=message)


class ParseTimeoutError(ParseConnectionError):
    """La requête a dépassé le délai d'attente configuré.

    Code : -2 (erreur interne SDK).
    """

    def __init__(self, message: str = "La requête a expiré (timeout)") -> None:
        ParseError.__init__(self, code=-2, message=message)


# ---------------------------------------------------------------------------
# Erreurs d'authentification et de session
# ---------------------------------------------------------------------------

class ParseAuthenticationError(ParseError):
    """Erreur d'authentification : identifiants invalides ou session expirée.

    Codes Parse : 101 (invalid credentials), 209 (invalid session token).
    """


class ParseSessionExpiredError(ParseAuthenticationError):
    """Le session token est expiré ou révoqué.

    Code Parse : 209.
    """

    def __init__(self, message: str = "Session expirée — reconnectez-vous") -> None:
        super().__init__(code=209, message=message)


# ---------------------------------------------------------------------------
# Erreurs sur les objets
# ---------------------------------------------------------------------------

class ParseObjectNotFoundError(ParseError):
    """L'objet demandé n'existe pas dans la base Parse.

    Code Parse : 101.
    """

    def __init__(
        self,
        class_name: str = "",
        object_id: str = "",
    ) -> None:
        if class_name and object_id:
            msg = f"Objet '{class_name}' avec objectId '{object_id}' introuvable"
        else:
            msg = "Objet introuvable"
        super().__init__(code=101, message=msg)


class ParseDuplicateValueError(ParseError):
    """Violation de contrainte d'unicité sur un champ.

    Code Parse : 137.
    """

    def __init__(self, field: str = "") -> None:
        msg = f"Valeur dupliquée sur le champ '{field}'" if field else "Valeur dupliquée"
        super().__init__(code=137, message=msg)


class ParseInvalidValueError(ParseError):
    """Valeur invalide pour un champ (mauvais type, format incorrect, etc.).

    Code Parse : 142.
    """


# ---------------------------------------------------------------------------
# Erreurs de permissions
# ---------------------------------------------------------------------------

class ParsePermissionError(ParseError):
    """Opération refusée par les ACL ou les Class-Level Permissions.

    Codes Parse : 119 (operation not allowed), 120 (master key required).
    """


class ParseMasterKeyRequiredError(ParsePermissionError):
    """Cette opération nécessite le Master Key.

    Code Parse : 119.
    """

    def __init__(self, message: str = "Le Master Key est requis pour cette opération") -> None:
        super().__init__(code=119, message=message)


# ---------------------------------------------------------------------------
# Erreurs de requêtes
# ---------------------------------------------------------------------------

class ParseQueryError(ParseError):
    """Erreur dans la construction ou l'exécution d'une requête ParseQuery.

    Code Parse : 102.
    """


class ParseInvalidQueryError(ParseQueryError):
    """La requête contient des paramètres invalides ou non supportés.

    Code Parse : 102.
    """

    def __init__(self, message: str = "Requête Parse invalide") -> None:
        super().__init__(code=102, message=message)


# ---------------------------------------------------------------------------
# Erreurs utilisateur
# ---------------------------------------------------------------------------

class ParseUsernameTakenError(ParseError):
    """Ce nom d'utilisateur est déjà pris.

    Code Parse : 202.
    """

    def __init__(self, username: str = "") -> None:
        msg = f"Le nom d'utilisateur '{username}' est déjà pris" if username else "Nom d'utilisateur déjà pris"
        super().__init__(code=202, message=msg)


class ParseEmailTakenError(ParseError):
    """Cette adresse email est déjà associée à un compte.

    Code Parse : 203.
    """

    def __init__(self, email: str = "") -> None:
        msg = f"L'email '{email}' est déjà utilisé" if email else "Email déjà utilisé"
        super().__init__(code=203, message=msg)


class ParseEmailNotFoundError(ParseError):
    """Aucun compte associé à cette adresse email.

    Code Parse : 205.
    """

    def __init__(self, message: str = "Aucun compte associé à cet email") -> None:
        super().__init__(code=205, message=message)


# ---------------------------------------------------------------------------
# Erreurs de fichiers
# ---------------------------------------------------------------------------

class ParseFileError(ParseError):
    """Erreur lors d'une opération sur un ParseFile.

    Code Parse : 130.
    """


class ParseFileNotFoundError(ParseFileError):
    """Le fichier demandé est introuvable sur le serveur.

    Code Parse : 130.
    """

    def __init__(self, filename: str = "") -> None:
        msg = f"Fichier '{filename}' introuvable" if filename else "Fichier introuvable"
        super().__init__(code=130, message=msg)


# ---------------------------------------------------------------------------
# Erreurs de Cloud Functions
# ---------------------------------------------------------------------------

class ParseCloudFunctionError(ParseError):
    """Erreur levée par une Cloud Function côté serveur.

    Code Parse : 141.
    """

    def __init__(self, function_name: str = "", message: str = "") -> None:
        full_msg = f"Cloud Function '{function_name}' : {message}" if function_name else message
        super().__init__(code=141, message=full_msg or "Erreur dans la Cloud Function")


class ParseCloudFunctionNotFoundError(ParseCloudFunctionError):
    """La Cloud Function demandée n'existe pas sur le serveur.

    Code Parse : 141.
    """

    def __init__(self, function_name: str = "") -> None:
        msg = f"Cloud Function '{function_name}' introuvable" if function_name else "Cloud Function introuvable"
        ParseError.__init__(self, code=141, message=msg)


# ---------------------------------------------------------------------------
# Erreurs de débit
# ---------------------------------------------------------------------------

class ParseRateLimitError(ParseError):
    """Limite de débit dépassée — trop de requêtes en peu de temps.

    Code Parse : 155.
    """

    def __init__(self, message: str = "Limite de requêtes dépassée — réessayez dans quelques secondes") -> None:
        super().__init__(code=155, message=message)


# ---------------------------------------------------------------------------
# Erreur de Push Notifications
# ---------------------------------------------------------------------------

class ParsePushError(ParseError):
    """Erreur lors de l'envoi d'une notification push.

    Code Parse : 112.
    """

    def __init__(self, message: str = "Erreur lors de l'envoi de la notification push") -> None:
        super().__init__(code=112, message=message)


# ---------------------------------------------------------------------------
# Erreur de LiveQuery
# ---------------------------------------------------------------------------

class ParseLiveQueryError(ParseError):
    """Erreur de connexion ou d'abonnement LiveQuery.

    Code : -3 (erreur interne SDK).
    """

    def __init__(self, message: str = "Erreur LiveQuery") -> None:
        super().__init__(code=-3, message=message)


# ---------------------------------------------------------------------------
# Mapping code → exception (utilisé par _http.py)
# ---------------------------------------------------------------------------

#: Correspondance entre les codes d'erreur Parse et les exceptions SDK.
#: Utilisé par la couche HTTP pour lever l'exception la plus précise possible.
PARSE_ERROR_MAP: dict[int, type[ParseError]] = {
    101: ParseObjectNotFoundError,
    102: ParseInvalidQueryError,
    112: ParsePushError,
    119: ParseMasterKeyRequiredError,
    130: ParseFileError,
    137: ParseDuplicateValueError,
    141: ParseCloudFunctionError,
    142: ParseInvalidValueError,
    155: ParseRateLimitError,
    202: ParseUsernameTakenError,
    203: ParseEmailTakenError,
    205: ParseEmailNotFoundError,
    209: ParseSessionExpiredError,
}


def raise_parse_error(code: int, message: str) -> None:
    """Lève l'exception Parse la plus précise pour le code donné.

    Args:
        code: Code d'erreur retourné par Parse Server.
        message: Message d'erreur retourné par Parse Server.

    Raises:
        ParseError: L'exception la plus spécifique correspondant au code.
    """
    exc_class = PARSE_ERROR_MAP.get(code, ParseError)
    if exc_class is ParseError:
        raise ParseError(code=code, message=message)
    raise exc_class(message=message)  # type: ignore[call-arg]
