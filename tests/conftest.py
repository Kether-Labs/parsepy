"""
Fixtures pytest partagées entre les tests unitaires et d'intégration.

Les fixtures marquées @pytest.fixture(scope="session") sont créées une
seule fois pour toute la session de tests — utilisez-les pour les ressources
coûteuses à initialiser.

Les fixtures sans scope sont recréées à chaque test — utilisez-les pour
les objets qui doivent être isolés entre les tests.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Configuration Parse Server de test
# Ces valeurs correspondent au docker-compose.test.yml
# ---------------------------------------------------------------------------

TEST_APP_ID = "test-app-id"
TEST_REST_KEY = "test-rest-key"
TEST_MASTER_KEY = "test-master-key"
TEST_SERVER_URL = "http://localhost:1337/parse"


# ---------------------------------------------------------------------------
# Fixtures HTTP (disponibles dès maintenant pour les tests unitaires)
# ---------------------------------------------------------------------------

@pytest.fixture
def parse_server_url() -> str:
    """URL du serveur Parse de test."""
    return TEST_SERVER_URL


@pytest.fixture
def parse_credentials() -> dict[str, str]:
    """Identifiants Parse pour les tests.

    Returns:
        Dictionnaire avec app_id, rest_key, master_key, server_url.
    """
    return {
        "app_id": TEST_APP_ID,
        "rest_key": TEST_REST_KEY,
        "master_key": TEST_MASTER_KEY,
        "server_url": TEST_SERVER_URL,
    }


# ---------------------------------------------------------------------------
# Fixtures de types Parse (utiles pour tous les modules)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_geopoint() -> dict[str, float]:
    """Coordonnées GPS de Paris — utile pour tester GeoPoint."""
    return {"latitude": 48.8566, "longitude": 2.3522}


@pytest.fixture
def sample_pointer() -> dict[str, str]:
    """Pointeur Parse vers un objet fictif."""
    return {"className": "Post", "objectId": "abc123"}


@pytest.fixture
def parse_date_iso() -> str:
    """Date ISO 8601 au format Parse Server."""
    return "2024-01-15T12:00:00.000Z"


# ---------------------------------------------------------------------------
# NOTE pour les contributeurs
# ---------------------------------------------------------------------------
# Quand vous implémentez ParseClient (#1), ajoutez ici :
#
#   @pytest.fixture
#   def http_client(parse_credentials):
#       from parse_sdk._http import ParseHTTPClient
#       return ParseHTTPClient(**parse_credentials)
#
# Quand vous implémentez ParseObject (#2), ajoutez :
#
#   @pytest.fixture
#   def mock_object():
#       return {"objectId": "abc123", "score": 100, "createdAt": "...", "updatedAt": "..."}
#
# Rangez les fixtures complexes dans des fichiers conftest.py locaux :
#   tests/unit/conftest.py      ← fixtures spécifiques aux tests unitaires
#   tests/integration/conftest.py ← fixtures avec un vrai serveur Parse
