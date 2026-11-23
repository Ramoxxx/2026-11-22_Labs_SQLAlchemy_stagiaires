# Cahier d'exercices : SQLAlchemy 2.1 avec Python 3.15 et PostgreSQL

Formation BStorm de 2 jours. Fil rouge : la base de données d'une bibliothèque (auteurs, livres, étiquettes, membres, emprunts).

Chaque exercice part du résultat du précédent. Les solutions se trouvent dans le dossier `solutions/` et ont été exécutées sur Python 3.15, SQLAlchemy 2.1.9, psycopg 3.3.9 et PostgreSQL. Ne les ouvrez qu'après avoir essayé.

| N° | Exercice | Module | Durée |
|---|---|---|---|
| 01 | Démarrer PostgreSQL et créer la base | 02 | 15 min |
| 02 | Premier contact avec un Engine | 02 | 15 min |
| 03 | Une connexion sans secret dans le code | 02 | 15 min |
| 04 | Créer la première table avec Core | 03 | 20 min |
| 05 | Lire et écrire avec Core | 03 | 25 min |
| 06 | Provoquer un rollback | 03 | 15 min |
| 07 | Premier modèle ORM : Member | 04 | 25 min |
| 08 | Relation un-à-plusieurs : Author et Book | 05 | 25 min |
| 09 | Relation plusieurs-à-plusieurs : les étiquettes | 05 | 20 min |
| 10 | Atelier J1 : le modèle complet et ses données | 05 | 1 h 30 |
| 11 | Les états d'un objet dans la Session | 06 | 20 min |
| 12 | Six requêtes ORM | 07 | 30 min |
| 13 | Mesurer et corriger un N+1 | 07 | 25 min |
| 14 | Pagination par clé | 07 | 15 min |
| 15 | Une API asynchrone avec FastAPI | 08 | 30 min |
| 16 | Passer le schéma sous Alembic | 09 | 40 min |
| 17 | Corriger une injection SQL et réduire les droits | 10 | 25 min |
| 18 | Tester sur un vrai PostgreSQL | 10 | 30 min |
| 19 | Bonus Python 3.15 : une CLI à imports paresseux | 10 | 15 min |

## Installation (avant l'exercice 01)

PostgreSQL 18 est installé sur votre poste (installeur Windows d'EDB, avec pgAdmin 4). Notez le mot de passe du superutilisateur `postgres` choisi à l'installation.

Dans un terminal (PowerShell), dans le dossier du kit dézippé :

```powershell
uv sync                      # installe Python 3.15 et les dépendances verrouillées dans uv.lock
copy .env.example .env       # identifiants de la base de labo, jamais commités (macOS/Linux : cp)
```

---

## Exercice 01 : Démarrer PostgreSQL et créer la base

**Objectif :** disposer d'un serveur PostgreSQL, d'un rôle applicatif `app` et d'une base `bibliotheque` qui lui appartient.
**Durée :** 15 min

1. Ouvrez pgAdmin 4 et connectez-vous au serveur PostgreSQL 18 avec le mot de passe de `postgres`.
2. Ouvrez le Query Tool sur la base `postgres` (clic droit → Query Tool).
3. Écrivez la requête SQL qui crée un rôle `app` qui peut se connecter, avec le mot de passe `app`, et exécutez-la (F5).
4. Écrivez la requête qui crée la base `bibliotheque`, dont le propriétaire est `app`, et exécutez-la **seule** : sélectionnez la ligne, puis F5.
5. Rafraîchissez l'arbre (clic droit → Refresh) et vérifiez : `app` apparaît dans Login/Group Roles, `bibliotheque` dans Databases, avec `app` comme propriétaire (onglet Properties).

**Résultat attendu :** le rôle `app` et la base `bibliotheque` sont visibles dans pgAdmin. La connexion avec le rôle `app` sera testée en Python à l'exercice 02.

**Indices :** `CREATE ROLE … LOGIN PASSWORD '…'` et `CREATE DATABASE … OWNER …`. Si vous obtenez « CREATE DATABASE cannot run inside a transaction block », vous avez exécuté les deux requêtes d'un seul coup.

**Pour aller plus loin :** pourquoi ne pas faire travailler l'application avec le rôle `postgres` ? (On y revient à l'exercice 17.)

---

## Exercice 02 : Premier contact avec un Engine

**Objectif :** se connecter depuis Python et lire le SQL émis.
**Durée :** 15 min

1. Créez `ex02_premier_contact.py`.
2. Créez un Engine vers `postgresql+psycopg://app:app@localhost:5432/bibliotheque` avec `echo=True`.
3. Dans un bloc `with engine.connect() as conn:`, exécutez avec `text()` la requête `SELECT version(), current_database(), current_user`.
4. Affichez les trois valeurs. Repérez dans la sortie les lignes `BEGIN` et `ROLLBACK` journalisées par SQLAlchemy.

```python
from sqlalchemy import create_engine, text

engine = ...  # à compléter

with engine.connect() as conn:
    row = conn.execute(text("...")).one()
    print(row)
```

**Résultat attendu :** `Base : bibliotheque` et `Rôle : app`, précédés du SQL journalisé.

**Questions :** pourquoi voit-on un `ROLLBACK` alors qu'on n'a rien écrit ? Que se passe-t-il avec l'URL `postgresql://…` sans `+psycopg` ? (Depuis SQLAlchemy 2.1, psycopg 3 est le driver PostgreSQL par défaut : l'URL fonctionne aussi. Pourquoi garder `+psycopg` malgré tout ?)

---

## Exercice 03 : Une connexion sans secret dans le code

**Objectif :** sortir les identifiants du code et centraliser l'Engine dans un module `db.py`.
**Durée :** 15 min

1. Vérifiez que `.env` contient `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` et qu'il figure dans `.gitignore`.
2. Créez `db.py` : chargez `.env` avec `load_dotenv()`, construisez l'URL avec `URL.create(...)` et créez un Engine unique avec `pool_pre_ping=True`.
3. Dans `ex03_connexion_sure.py`, importez `engine` et affichez `current_user` et `current_database()`.
4. Tentez une connexion avec un mot de passe faux (`make_url().set(password="faux")`) et interceptez `OperationalError`.
5. Affichez l'URL sans le mot de passe avec `render_as_string(hide_password=True)`.

**Résultat attendu :**
```
Connecté en tant que app sur bibliotheque
Connexion refusée : OperationalError
URL affichée sans secret : postgresql+psycopg://app:***@localhost:5432/bibliotheque
```

**Pour aller plus loin :** `git status` ne doit jamais montrer `.env`. Où stockeriez-vous ces valeurs en production ?

---

## Exercice 04 : Créer la première table avec Core

**Objectif :** décrire une table en Python et la créer.
**Durée :** 20 min

1. Dans `ex04_table_core.py`, créez un `MetaData()` et une `Table("book", …)` avec : `id` entier clé primaire, `title` texte de 200 caractères obligatoire, `year` entier facultatif, `isbn` texte de 17 caractères unique.
2. Appelez `metadata.create_all(engine)` deux fois de suite. Que se passe-t-il au second appel ?
3. Vérifiez dans pgAdmin (bibliotheque → Schemas → public → Tables → book → Columns, après un Refresh), ou en Python avec `inspect(engine).get_columns("book")`.

**Résultat attendu :** quatre colonnes ; `title` et `id` non nullables ; une contrainte unique sur `isbn` visible dans `\d book`.

**Question :** que fait `create_all()` si vous ajoutez une colonne au modèle puis le relancez ?

---

## Exercice 05 : Lire et écrire avec Core

**Objectif :** pratiquer `insert`, `select`, `update` et `delete`.
**Durée :** 25 min

Dans `ex05_crud_core.py`, en une seule transaction `engine.begin()` :

1. Insérez ces cinq livres en un seul appel et récupérez les `id` générés avec `.returning(book.c.id)` : Dune (1965), Neuromancer (1984), La Main gauche de la nuit (1969), Fondation (1951), Le Problème à trois corps (2008).
2. Affichez les livres publiés après 1960, du plus récent au plus ancien.
3. Corrigez l'année de Dune en 1966 et affichez le nombre de lignes modifiées.
4. Supprimez les livres antérieurs à 1960 et affichez le nombre de lignes supprimées.
5. Affichez le nombre de livres restants avec `func.count()`.

**Résultat attendu :** `id générés : [1, 2, 3, 4, 5]`, quatre livres affichés, 1 ligne mise à jour, 1 supprimée, 4 restantes.

**Piège à tester :** que se passe-t-il avec un `update(book).values(year=2000)` sans `.where()` ? (Testez dans une transaction que vous annulez.)

---

## Exercice 06 : Provoquer un rollback

**Objectif :** constater qu'une transaction est tout ou rien.
**Durée :** 15 min

1. Écrivez une fonction `count()` qui renvoie le nombre de livres.
2. Dans un bloc `engine.begin()`, insérez deux livres puis levez `RuntimeError`. Comparez `count()` avant et après.
3. Insérez un livre avec un ISBN déjà utilisé et interceptez `IntegrityError`. Affichez `type(exc.orig).__name__`.
4. Avec `engine.connect()`, insérez un livre sans appeler `conn.commit()`. Le livre est-il en base ?

**Résultat attendu :** le nombre de livres ne change à aucune étape ; l'erreur est `UniqueViolation`.

---

## Exercice 07 : Premier modèle ORM : Member

**Objectif :** écrire une classe déclarative typée avec des contraintes en base.
**Durée :** 25 min

1. Repartez d'une base vide avec `reset_schema()` (fourni dans `db.py`, à n'utiliser qu'en formation).
2. Créez `Base(DeclarativeBase)` et la classe `Member` : `id`, `email` (255, unique), `name` (100), `phone` facultatif (20), `created_at` horodaté avec fuseau, valeur par défaut calculée par PostgreSQL (`server_default=func.now()`).
3. Créez la table, ajoutez Alice et Bob avec une `Session`, puis relisez-les.
4. Ajoutez un second membre avec l'email d'Alice et interceptez l'erreur.

**Résultat attendu :** deux membres affichés avec la date du jour ; le doublon est refusé avec `UniqueViolation`.

**Questions :** quel type PostgreSQL a été créé pour `created_at` ? Pourquoi `phone` est-il nullable sans l'avoir écrit ?

---

## Exercice 08 : Relation un-à-plusieurs : Author et Book

**Objectif :** relier deux classes et naviguer dans les deux sens.
**Durée :** 25 min

1. Créez `Author` (`id`, `name`) et `Book` (`id`, `title`, `author_id` clé étrangère).
2. Ajoutez `Author.books` et `Book.author` avec `relationship(back_populates=…)`, et `cascade="all, delete-orphan"` côté auteur.
3. Créez Ursula K. Le Guin avec trois livres en n'ajoutant que l'autrice à la session. Avant le commit, affichez `leguin.books[0].author.name`.
4. Relisez un livre et affichez son auteur, puis tous les livres de cet auteur.
5. Supprimez l'autrice et comptez les livres restants.

**Résultat attendu :** la navigation fonctionne dans les deux sens avant même le flush ; il reste 0 livre après la suppression.

---

## Exercice 09 : Relation plusieurs-à-plusieurs : les étiquettes

**Objectif :** utiliser une table d'association.
**Durée :** 20 min

À partir d'ici, le modèle vit dans `models.py`.

1. Créez la table `book_tag` (deux clés étrangères formant la clé primaire) et la classe `Tag` (`name` unique).
2. Ajoutez `Book.tags` et `Tag.books` avec `secondary=book_tag`.
3. Créez Dune (sf, classique, prix-hugo) et Neuromancer (sf, prix-hugo).
4. Requête : les livres étiquetés « classique » (`select(Book).join(Book.tags).where(...)`).
5. Retirez « prix-hugo » de Neuromancer et vérifiez `prix.books`.

**Résultat attendu :** `classiques : [Book('Dune')]` puis `prix-hugo : ['Dune']`.

---

## Exercice 10 : Atelier J1 : le modèle complet et ses données

**Objectif :** livrer le modèle de la bibliothèque, réutilisé pendant tout le jour 2.
**Durée :** 1 h 30, en binôme

1. Complétez `models.py` avec `Loan` : `member_id` (suppression en cascade côté base), `book_id`, `loaned_at` (défaut serveur), `due_date`, `returned_at` facultatif, et les relations `Member.loans` et `Book.loans`.
2. Ajoutez une contrainte `CHECK (due_date > loaned_at)` et un index sur `(member_id, due_date)`.
3. Ajoutez à `Book` : `year` facultatif, `isbn` unique, un index sur `title`.
4. Écrivez `seed.py` : 3 auteurs, 10 livres, 5 étiquettes, 4 membres, 6 emprunts (voir la solution pour un jeu prêt à l'emploi).
5. Vérifiez la contrainte CHECK avec un emprunt dont la date de retour précède la date d'emprunt.

**Critères de réussite :** contraintes vérifiées par PostgreSQL, relations navigables dans les deux sens, aucun secret dans le code, `seed.py` relançable à volonté.

**Résultat attendu :** `author 3, book 10, tag 5, member 4, loan 6`, puis `CHECK refusé : CheckViolation`.

**Bonus :** affichez pour chaque membre la liste des titres qu'il a empruntés.

---

## Exercice 11 : Les états d'un objet dans la Session

**Objectif :** relier le code aux états transient, pending, persistent, detached.
**Durée :** 20 min

1. Écrivez `etat(obj)` qui renvoie l'état grâce à `sqlalchemy.inspect(obj)`.
2. Créez un livre et affichez son état après la création, après `session.add()`, après `session.flush()` (affichez aussi son `id`) et après la sortie du bloc.
3. Après la fermeture de la session, lisez `livre.title`. Quelle erreur obtenez-vous ?
4. Corrigez de deux manières : `sessionmaker(engine, expire_on_commit=False)`, puis en lisant la valeur avant la fermeture.
5. Lisez deux fois la même ligne dans une session (`session.get` puis `select`) : obtenez-vous le même objet Python ?

**Résultat attendu :** `transient`, `pending`, `persistent id = …`, `detached`, puis `DetachedInstanceError`, et `True` pour l'identity map.

---

## Exercice 12 : Six requêtes ORM

**Objectif :** écrire les requêtes courantes en style 2.x. Relancez `seed.py` avant de commencer.
**Durée :** 30 min

1. Les titres contenant « dune », sans tenir compte de la casse.
2. Le livre d'id 5, par clé primaire.
3. Le membre dont l'email est `bob@example.org` (exactement un résultat attendu).
4. Le nombre de livres par auteur, du plus prolifique au moins prolifique.
5. Les 3 membres ayant le plus emprunté sur les 30 derniers jours.
6. Les livres jamais empruntés (jointure externe).

**Résultat attendu :** requête 4 : Le Guin 4, Herbert 3, Christie 3 (ex aequo départagés par l'ordre de création des auteurs) ; requête 5 : Alice 3, puis Bob et Chloé 1 ; requête 6 : 5 titres.

**Indices :** `ilike`, `session.get`, `.one()`, `func.count(...).label("nb")`, `desc("nb")`, `outerjoin(...).where(Loan.id.is_(None))`.

---

## Exercice 13 : Mesurer et corriger un N+1

**Objectif :** compter les requêtes réellement envoyées, puis les réduire.
**Durée :** 25 min

1. Écrivez un gestionnaire de contexte `compteur()` qui écoute l'événement `before_cursor_execute` de l'Engine.
2. Listez les auteurs avec le nombre de leurs livres (`len(a.books)`) et comptez les requêtes.
3. Ajoutez `.options(selectinload(Author.books))` et recomptez.
4. Chargez un livre avec `.options(raiseload("*"))` puis accédez à `book.author` : que se passe-t-il ?

**Résultat attendu :** 4 requêtes (1 + 1 par auteur) sans option, 2 avec `selectinload`, une erreur avec `raiseload`.

**Question :** combien de requêtes avec 1 000 auteurs, avant et après la correction ?

---

## Exercice 14 : Pagination par clé

**Objectif :** parcourir une grande table à coût constant.
**Durée :** 15 min

1. Écrivez `page(session, after_id=0, size=3)` qui renvoie les livres d'id supérieur à `after_id`, triés par id.
2. Écrivez le générateur `toutes_les_pages(session, size)` qui enchaîne les pages jusqu'à une page vide.
3. Affichez les id de chaque page.

**Résultat attendu :** `[1, 2, 3]`, `[4, 5, 6]`, `[7, 8, 9]`, `[10]`.

**Question :** pourquoi `OFFSET 100000` est-il lent, même avec un index ?

---

## Exercice 15 : Une API asynchrone avec FastAPI

**Objectif :** passer en asyncio sans chargement implicite.
**Durée :** 30 min

1. Créez un `create_async_engine` avec la même URL (`make_url()`), puis un `async_sessionmaker(engine, expire_on_commit=False)`.
2. Écrivez la dépendance `get_session()` qui ouvre une `AsyncSession` par requête.
3. Écrivez `GET /books?after_id=&size=` (pagination de l'exercice 14) et `GET /books/{book_id}` (404 si absent). Les réponses passent par un modèle Pydantic `BookOut` (id, title, year, author, tags).
4. Chargez auteur et étiquettes avec `selectinload`.
5. Lancez `uv run fastapi dev ex15_api_async.py` et testez sur `http://127.0.0.1:8000/docs`.
6. Dans une session async, lisez `book.tags` sans chargement préalable : quelle erreur obtenez-vous ? Corrigez avec `await book.awaitable_attrs.tags`.

**Résultat attendu :** `200` sur la liste et le détail, `404` sur un id inconnu, `MissingGreenlet` sur l'accès paresseux.

---

## Exercice 16 : Passer le schéma sous Alembic

**Objectif :** versionner le schéma et faire évoluer une table sans perdre de données.
**Durée :** 40 min

1. Videz la base (`reset_schema()`), puis initialisez Alembic : `uv run alembic init migrations`.
2. Dans `migrations/env.py`, importez `Base` et `make_url`, définissez `target_metadata = Base.metadata` et passez l'URL à la configuration (l'URL ne va pas dans `alembic.ini`).
3. Générez la migration initiale : `uv run alembic revision --autogenerate -m "schema initial"`. Relisez le fichier, puis `uv run alembic upgrade head`.
4. Ajoutez `pages: Mapped[int | None]` à `Book`. Lancez `uv run alembic check` : que dit-il ?
5. Générez et appliquez la seconde migration. Testez `alembic downgrade -1`, `alembic current`, puis `alembic upgrade head`.
6. Affichez l'historique avec `alembic history`.

**Résultat attendu :** `check` signale la colonne manquante, puis `No new upgrade operations detected` après la migration ; l'historique montre deux révisions.

**Question :** que proposerait l'autogénération si vous renommiez `title` en `titre` ? Pourquoi est-ce dangereux ?

---

## Exercice 17 : Corriger une injection SQL et réduire les droits

**Objectif :** reconnaître et corriger deux failles courantes.
**Durée :** 25 min

Relancez `seed.py` pour repartir du jeu de données de référence. Code vulnérable fourni :
```python
def find_member_vulnerable(email: str) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT name FROM member WHERE email = '{email}'"))
        return [r.name for r in rows]
```

1. Appelez-la avec `' OR '1'='1`. Combien de membres sont renvoyés ?
2. Corrigez-la de deux façons : paramètre lié `:email` avec `text()`, puis requête ORM.
3. Écrivez `list_books(sort, desc)` où `sort` vient de l'utilisateur : utilisez une liste blanche de colonnes et refusez le reste.
4. En superutilisateur, créez un rôle `app_rw` qui peut lire et écrire les données mais pas modifier le schéma. Vérifiez qu'il ne peut ni créer ni supprimer de table.

**Résultat attendu :** la version vulnérable renvoie les 4 membres, les versions corrigées aucun ; `CREATE TABLE` échoue avec `permission denied for schema public`.

---

## Exercice 18 : Tester sur un vrai PostgreSQL

**Objectif :** des tests rapides, isolés, sur le même moteur que la production.
**Durée :** 30 min

1. Dans pgAdmin, créez une base de test `bibliotheque_test` dont le propriétaire est `app`. Dans `tests/conftest.py`, écrivez une fixture `engine` de portée session qui se connecte à l'URL de la variable d'environnement `TEST_DATABASE_URL`, puis recrée le schéma (`drop_all`, puis `create_all`).
2. Écrivez une fixture `session` : connexion, `conn.begin()`, `Session(bind=conn, join_transaction_mode="create_savepoint")`, chargement de `seed()`, puis `rollback` final.
3. Écrivez au moins ces tests : email unique ; contrainte de dates d'un emprunt ; suppression d'un auteur sans emprunts ; un livre emprunté ne peut pas disparaître ; la pagination couvre tous les livres ; la liste des auteurs tient en 2 requêtes.
4. Définissez la variable puis lancez les tests (PowerShell) : `$env:TEST_DATABASE_URL = "postgresql+psycopg://app:app@localhost/bibliotheque_test"`, puis `uv run pytest -q`.

**Résultat attendu :** `6 passed`.

**Question :** pourquoi un test « supprimer un auteur » peut-il échouer alors que la cascade est déclarée ? (Regardez les emprunts.)

---

## Exercice 19 : Bonus Python 3.15 : une CLI à imports paresseux

**Objectif :** utiliser les imports paresseux explicites de Python 3.15 (PEP 810).
**Durée :** 15 min

1. Écrivez une CLI avec deux commandes : `--help` et `stats` (nombre de livres, nombre d'emprunts en cours).
2. Importez SQLAlchemy, `db` et `models` avec `lazy from … import …`.
3. Affichez à la fin si `"sqlalchemy" in sys.modules` et le temps écoulé.

**Résultat attendu :** `--help` répond sans charger SQLAlchemy ; `stats` le charge au premier usage.

**Question :** pourquoi une bibliothèque qui supporte encore Python 3.11 ne peut-elle pas utiliser cette syntaxe ?
