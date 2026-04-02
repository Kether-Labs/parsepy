# Guide de Contribution — SDK Python pour Parse Server (parsepy)

Merci de l'intérêt que vous portez à ce projet ! Ce guide vous explique comment contribuer efficacement, que vous soyez développeur, testeur ou documentaliste.

---

##  Table des matières

1. [Code de conduite](#-code-de-conduite)
2. [Prérequis](#-prérequis)
3. [Installation de l'environnement de développement](#-installation-de-lenvironnement-de-développement)
4. [Structure du projet](#-structure-du-projet)
5. [Stratégie de branches](#-stratégie-de-branches)
6. [Créer une contribution](#-créer-une-contribution)
7. [Standards de qualité](#-standards-de-qualité)
8. [Ouvrir une Pull Request](#-ouvrir-une-pull-request)
9. [Processus de Code Review](#-processus-de-code-review)
10. [Signaler un bug](#-signaler-un-bug)
11. [Proposer une fonctionnalité](#-proposer-une-fonctionnalité)
12. [Les rôles dans le projet](#-les-rôles-dans-le-projet)
13. [Communication](#-communication)

---

## Code de conduite

Ce projet adhère au [Contributor Covenant](https://www.contributor-covenant.org/fr/version/2/1/code_of_conduct/). 
En participant, vous vous engagez à maintenir un environnement **respectueux, inclusif et bienveillant** pour tous.

Comportements attendus :

- Utiliser un langage accueillant et inclusif
- Respecter les points de vue différents
- Accepter les critiques constructives avec ouverture
- Se concentrer sur ce qui est le mieux pour la communauté

Comportements inacceptables :

- Harcèlement sous toute forme
- Commentaires insultants ou dégradants
- Trolling ou attaques personnelles

Tout manquement peut être signalé à : **[]**

---

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.9+** — [python.org](https://www.python.org/downloads/)
- **Git** — [git-scm.com](https://git-scm.com/)
- **pip** ou **poetry** (recommandé)
- Un compte **GitHub**

Vérifiez vos versions :

```bash
python --version   # Python 3.9.x ou supérieur
git --version      # git version 2.x
```

---

## Installation de l'environnement de développement

### 1. Forker et cloner le dépôt

```bash
# 1. Forkez le projet depuis GitHub (bouton "Fork" en haut à droite)

# 2. Clonez votre fork localement
git clone https://github.com/Kether-Labs/parsepy.git
cd parsepy

# 3. Ajoutez le dépôt original comme remote "upstream"
git remote add upstream https://github.com/Kether-Labs/parsepy.git
```

### 2. Créer un environnement virtuel

```bash
# Avec venv (standard)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```
### 3. Installer les dépendances de développement

```bash
# Avec pip
pip install -e ".[dev]"

# Avec poetry
poetry install --with dev
```

### 4. Vérifier que tout fonctionne

```bash
# Lancer les tests
pytest

# Vérifier le linting
ruff check .
black --check .

# Vérifier le typage
mypy src/
```

Si toutes les commandes passent , votre environnement est prêt !

---

## Structure du projet

```
parsepy/
│
├── src/
│   └── parse_sdk/
│       ├── __init__.py          ← Point d'entrée public du SDK
│       ├── client.py            ← ParseClient (configuration)
│       ├── object.py            ← ParseObject
│       ├── query.py             ← ParseQuery
│       ├── user.py              ← ParseUser
│       ├── file.py              ← ParseFile
│       ├── cloud.py             ← Cloud Functions
│       ├── acl.py               ← ParseACL & ParseRole
│       ├── push.py              ← Push Notifications
│       ├── live_query.py        ← LiveQuery WebSocket
│       └── exceptions.py        ← Exceptions personnalisées
│
├── tests/
│   ├── unit/                    ← Tests unitaires (sans serveur)
│   ├── integration/             ← Tests d'intégration (avec Parse Server)
│   └── conftest.py              ← Fixtures pytest partagées
│
├── docs/
│   ├── getting-started.md
│   ├── api-reference/
│   └── examples/
│
├── .github/
│   ├── workflows/               ← GitHub Actions CI/CD
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── pyproject.toml               ← Configuration du projet
├── CONTRIBUTING.md              ← Ce fichier
├── CHANGELOG.md                 ← Historique des versions
├── CODE_OF_CONDUCT.md
└── README.md
```

---

## Stratégie de branches

Nous utilisons un **Git Flow simplifié** :

| Branche       | Rôle                                          |
| ------------- | --------------------------------------------- |
| `main`        | Code stable — releases officielles uniquement |
| `develop`     | Branche d'intégration — toujours à jour       |
| `feature/xxx` | Nouvelle fonctionnalité                       |
| `fix/xxx`     | Correction de bug                             |
| `docs/xxx`    | Amélioration de la documentation              |
| `test/xxx`    | Ajout ou amélioration de tests                |
| `chore/xxx`   | Maintenance (CI, dépendances, config)         |

> **Ne jamais pousser directement sur `main` ou `develop`.** 
> Toute modification passe obligatoirement par une Pull Request.

### Nommage des branches

```bash
# Bons exemples
feature/parse-object-crud
feature/parse-query-filters
fix/authentication-token-expiry
docs/installation-guide
test/parse-user-integration

# Mauvais exemples
my-branch
fix
update
```

---

## Créer une contribution

### Étape 1 — Trouver ou créer une Issue

- Consultez les [Issues ouvertes](https://github.com/Kether-Labs/parsepy/issues)
- Cherchez le label **`good first issue`** si vous débutez
- Si votre idée n'existe pas encore, créez une Issue avant de coder

### Étape 2 — S'assigner l'Issue

Commentez dans l'Issue :

```
Je prends cette tâche ! Je vais commencer par [décrivez brièvement votre approche].
```

Un mainteneur vous assignera officiellement.

### Étape 3 — Créer votre branche

```bash
# Mettez votre develop local à jour
git checkout develop
git pull upstream develop

# Créez votre branche de travail
git checkout -b feature/nom-de-votre-feature
```

### Étape 4 — Coder

Travaillez sur votre fonctionnalité en suivant les [standards de qualité](#-standards-de-qualité).

Committez régulièrement avec des messages clairs :

```bash
# Format de commit : type(scope): description courte
git commit -m "feat(query): add greater_than and less_than filters"
git commit -m "fix(user): fix session token not being cleared on logout"
git commit -m "docs(readme): add installation instructions for Windows"
git commit -m "test(object): add unit tests for ParseObject.save()"
```

**Types de commits acceptés :**

| Type       | Usage                                       |
| ---------- | ------------------------------------------- |
| `feat`     | Nouvelle fonctionnalité                     |
| `fix`      | Correction de bug                           |
| `docs`     | Documentation uniquement                    |
| `test`     | Ajout ou modification de tests              |
| `refactor` | Refactoring sans changement de comportement |
| `chore`    | Maintenance, dépendances, CI                |
| `style`    | Formatage, espaces (sans logique)           |

### Étape 5 — Pousser et ouvrir une PR

```bash
git push origin feature/nom-de-votre-feature
```

Puis ouvrez une **Pull Request** vers la branche `develop` sur GitHub.



Pas de **Pull Request ** directement sur main — toujours vers develop

---

## Standards de qualité

Toute contribution doit respecter ces standards **avant** d'être soumise.

### 1. Tests obligatoires

```bash
# Chaque nouvelle fonctionnalité doit avoir ses tests
pytest tests/ -v

# La couverture de code doit rester au-dessus de 80%
pytest --cov=src/parse_sdk --cov-report=term-missing
```

### 2. Typage statique (Type Hints)

```python
# Correct
async def find(self, limit: int = 100, skip: int = 0) -> list["ParseObject"]:
    ...

# Incorrect
async def find(self, limit=100, skip=0):
    ...
```

Vérifiez avec :

```bash
mypy src/
```

### 3. Style de code

Nous utilisons **Black** pour le formatage et **Ruff** pour le linting :

```bash
# Formater automatiquement
black src/ tests/

# Vérifier les problèmes de style
ruff check src/ tests/

# Corriger automatiquement ce qui peut l'être
ruff check --fix src/ tests/
```

### 4. Documentation du code (Docstrings)

Toute classe et méthode publique doit avoir une docstring au format **Google Style** :

```python
class ParseQuery:
    """Permet de construire et d'exécuter des requêtes sur Parse Server.

    Attributes:
        class_name: Le nom de la classe Parse à interroger.

    Example:
        >>> query = ParseQuery("GameScore")
        >>> query.equal_to("playerName", "Alice")
        >>> results = await query.find()
    """

    async def equal_to(self, key: str, value: object) -> "ParseQuery":
        """Filtre les objets dont le champ correspond exactement à la valeur.

        Args:
            key: Le nom du champ à filtrer.
            value: La valeur attendue.

        Returns:
            L'instance de ParseQuery (pour le chaînage).

        Example:
            >>> query.equal_to("score", 100)
        """
        ...
```

### 5. Support synchrone et asynchrone

Le SDK doit toujours proposer les deux interfaces :

```python
# API asynchrone (prioritaire)
results = await query.find()

# API synchrone (pour compatibilité)
results = query.find_sync()
```

---

## Ouvrir une Pull Request

Quand vous ouvrez une PR, remplissez le template fourni :

```markdown
## Description
Décrivez clairement les changements apportés et pourquoi.

## Issue liée
Closes #42

## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Amélioration de la documentation
- [ ] Refactoring
- [ ] Autre : ___

## Checklist
- [ ] Mon code respecte les standards du projet
- [ ] J'ai ajouté des tests pour mes changements
- [ ] Tous les tests existants passent
- [ ] J'ai mis à jour la documentation si nécessaire
- [ ] Mes commits suivent la convention définie
```

**Règles pour une bonne PR :**

- Une PR = une fonctionnalité ou un fix (pas tout à la fois)
- Titre clair et descriptif
- Description qui explique le *pourquoi*, pas seulement le *quoi*
- Liez toujours l'Issue correspondante avec `Closes #numéro`

---

## Processus de Code Review

### Pour les contributeurs

- Soyez réactif aux commentaires (répondez sous 48h si possible)
- Ne prenez pas les retours personnellement — ils améliorent le code
- Si vous n'êtes pas d'accord, expliquez calmement votre point de vue
- Une fois les retours adressés, signalez-le avec un commentaire

### Pour les reviewers

- Soyez bienveillant et constructif dans vos retours
- Expliquez *pourquoi* un changement est nécessaire
- Distinguez ce qui est bloquant (`BLOCKING:`) de ce qui est une suggestion (`SUGGESTION:`)
- Validez avec un ou un commentaire positif quand c'est bien fait

### Critères de validation d'une PR

Une PR est mergeable quand :

- [ ] Au moins **1 mainteneur** a approuvé
- [ ] Tous les checks **CI/CD sont verts** 
- [ ] Aucun conflit de merge
- [ ] La checklist PR est complète

---

## Signaler un bug

Utilisez le template d'Issue **Bug Report** en fournissant :

```markdown
## Description du bug
Une description claire et concise du problème.

## Comment reproduire
1. Initialiser le client avec '...'
2. Appeler la méthode '...'
3. Voir l'erreur

## Comportement attendu
Ce qui aurait dû se passer.

## Comportement observé
Ce qui s'est passé réellement.

## Environnement
- OS : Ubuntu 22.04 / Windows 11 / macOS 14
- Python : 3.11.2
- Version du SDK : 0.2.1
- Version Parse Server : 6.x

## Logs / Stack trace
```

Collez ici les logs ou messages d'erreur

```

```

---

## Proposer une fonctionnalité

Avant de coder une nouvelle fonctionnalité :

1. **Vérifiez** qu'elle n'est pas déjà dans la [Roadmap](ROADMAP.md) ou dans les Issues
2. **Ouvrez une Issue** avec le label `feature` en décrivant :
   - Le problème que ça résout
   - La solution proposée
   - Des exemples de code d'utilisation souhaitée
3. **Attendez validation** d'un mainteneur avant de commencer à coder

Cela évite de travailler pour rien et permet d'aligner la contribution avec la vision du projet.

---

## Les rôles dans le projet

| Rôle                   | Qui ?         | Responsabilités                                      |
| ---------------------- | ------------- | ---------------------------------------------------- |
| **Maintainer**         | Core Team     | Valide les PR, gère les releases, définit la roadmap |
| **Contributeur actif** | Tout le monde | Développe des features, corrige des bugs             |
| **Testeur**            | Volontaires   | Tests d'intégration Django / FastAPI / Flask         |
| **Documentaliste**     | Volontaires   | Guides, exemples, API Reference                      |

Les contributeurs réguliers et de qualité peuvent rejoindre la **Core Team** sur invitation.

---

## Communication

| Canal                  | Usage                                                        |
| ---------------------- | ------------------------------------------------------------ |
| **GitHub Issues**      | Bugs, fonctionnalités, tâches — tout ce qui concerne le code |
| **GitHub Discussions** | Débats d'architecture, idées générales, questions ouvertes   |
| **Whatsapps**          | Chat en temps réel, entraide rapide, annonces                |
| **Réunion mensuelle**  | Sync vidéo pour la roadmap (lien partagé sur Discord)        |

> **Règle d'or :** toute décision technique importante doit être documentée dans une Issue ou une Discussion GitHub, même si elle a été prise oralement.

---

##  Vos premières contributions

Vous débutez ? Voici par où commencer :

```
1. Donnez une étoile au projet sur GitHub
2. Lisez le README et la documentation existante
3. Présentez-vous dans le canal #introductions du Discord
4. Cherchez une issue avec le label "good first issue"
5. Commentez l'issue pour vous l'approprier
6. Codez, testez, documentez
7. Ouvrez votre première Pull Request
8. Recevez un feedback et apprenez !
```

**Bienvenue dans la communauté, et merci de contribuer à rendre Python encore plus puissant avec Parse Server ! **

---

*Ce guide est lui-même open source. Si vous pensez qu'il peut être amélioré, ouvrez une PR !*
