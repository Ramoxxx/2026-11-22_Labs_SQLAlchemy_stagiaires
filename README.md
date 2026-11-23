# Labs : SQLAlchemy 2.1 avec Python 3.15 et PostgreSQL

Kit d'exercices de la formation BStorm (2 jours). Fil rouge : la base d'une bibliothèque.

## Démarrage

Prérequis : PostgreSQL 18 installé localement (Windows : installeur EDB, avec pgAdmin 4).

```powershell
uv sync                    # Python 3.15 + dépendances verrouillées (uv.lock)
copy .env.example .env     # identifiants de labo (macOS/Linux : cp)
```

Puis suivez `exercices/cahier.md`, en commençant par l'exercice 01.

## Contenu

| Dossier / fichier | Rôle |
|---|---|
| `exercices/cahier.md` | Énoncés des 19 exercices, résultats attendus, questions |

Vous écrivez votre code dans ce dossier, exercice par exercice. Les solutions sont montrées par le formateur à la correction.

Versions testées le 19/11/2026 : Python 3.15, SQLAlchemy 2.1.9, psycopg 3.3.9, Alembic 1.20.1, FastAPI 0.165.
`db.reset_schema()` supprime toutes les tables : réservé aux exercices.
