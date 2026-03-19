# Parsepy

> Le SDK Python officiel, moderne et maintenu pour [Parse Server](https://parseplatform.org/).

[![CI](https://github.com/Kether-Labs/parsepy/actions/workflows/ci.yml/badge.svg)](https://github.com/Kether-Labs/parsepy/actions)
[![PyPI](https://img.shields.io/pypi/v/parsepy)](https://pypi.org/project/parsepy/)
[![Python](https://img.shields.io/pypi/pyversions/parsepy)](https://pypi.org/project/parsepy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Coverage](https://codecov.io/gh/Kether-Labs/parsepy/branch/main/graph/badge.svg)](https://codecov.io/gh/Kether-Labs/parsepy)

Parse Server dispose de SDK officiels pour JavaScript, iOS, Android et .NET — mais **pas pour Python**. Ce SDK comble ce manque.

---

## Fonctionnalités (roadmap)

| Module | Statut |
|---|---|
| `ParseClient` — configuration et HTTP | 🚧 En cours |
| `ParseObject` — CRUD | 📋 Planifié |
| `ParseQuery` — requêtes | 📋 Planifié |
| `ParseUser` — authentification | 📋 Planifié |
| `ParseFile` — fichiers | 📋 Planifié |
| `ParseACL / ParseRole` — permissions | 📋 Planifié |
| Cloud Functions | 📋 Planifié |
| Push Notifications | 📋 Planifié |
| LiveQuery | 📋 Planifié |
| Intégrations Django / FastAPI / Flask | 📋 Planifié |

---

## Installation

```bash
pip install parsepy
```

Avec les extras frameworks :

```bash
pip install "parsepy[django]"
pip install "parsepy[fastapi]"
pip install "parsepy[flask]"
```

---

## Utilisation rapide

> **Note :** Les exemples ci-dessous reflètent l'API cible. Les modules sont implémentés progressivement — suivez la [Roadmap](ROADMAP.md).

```python
from parse_sdk import ParseClient, ParseObject, ParseQuery, ParseUser

# Initialisation
client = ParseClient(
    app_id="myAppId",
    rest_key="myRestKey",
    server_url="https://my-parse.com/parse",
)

# Créer un objet
score = ParseObject("GameScore")
score.set("playerName", "Alice")
score.set("score", 1337)
await score.save()

print(score.object_id)   # "Ed1nuqPvcm"
print(score.created_at)  # datetime(...)

# Requêter
query = ParseQuery("GameScore")
query.greater_than("score", 1000)
query.limit(10)
results = await query.find()

# Authentification
user = await ParseUser.log_in("alice", "password123")
print(user.session_token)
```

---

## Développement

### Prérequis

- Python 3.9+
- [pip](https://pip.pypa.io/) ou [poetry](https://python-poetry.org/)

### Installation de l'environnement

```bash
git clone https://github.com/Kether-Labs/parsepy.git
cd parsepy-python

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"
```

### Lancer les tests

```bash
pytest                          # tous les tests
pytest tests/unit/              # tests unitaires seulement
pytest --cov                    # avec rapport de couverture
```

### Vérifier le code

```bash
black src/ tests/               # formatage
ruff check src/ tests/          # linting
mypy src/                       # typage statique
```

---

## Contribuer

Les contributions sont les bienvenues ! Lisez le [Guide de contribution](CONTRIBUTING.md) avant de commencer.

Cherchez les issues avec le label [`good first issue`](https://github.com/Kether-Labs/parsepy/labels/good%20first%20issue) pour commencer.

---

## Communauté

- **Discussions GitHub** : [Questions & idées](https://github.com/Kether-Labs/parsepy/discussions)
- **Issues** : [Bugs & features](https://github.com/Kether-Labs/parsepy/issues)

---

## Licence

[MIT](LICENSE) — Copyright © 2026 Parse Server Python SDK Contributors
