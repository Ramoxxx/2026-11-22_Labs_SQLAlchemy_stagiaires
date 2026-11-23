# Exercice 10 — Le modèle complet et le jeu de données

**Durée :** 40 min environ · **Slide de référence :** 31 (contrainte CHECK et index)

Jusqu'ici, chaque exercice avait sa propre `Base`. Un vrai projet n'en a qu'une. Vous allez rassembler tout le modèle dans un seul fichier, puis écrire un script qui remplit la base. Ces deux fichiers serviront pour l'exercice 12 et pour la suite de la formation : soignez-les.

## Partie 1 — `models.py`

Créez `models.py` à côté de `db.py`. Il contient **une seule** classe `Base` (héritée de `DeclarativeBase`) et les quatre modèles suivants, avec la syntaxe `Mapped[...]` / `mapped_column(...)`.

### `Member` (table `member`)
Reprenez votre classe de l'ex. 07 :
- `id` : clé primaire ;
- `email` : 255 caractères max, **unique** ;
- `name` : 100 caractères max ;
- `phone` : 20 caractères max, **facultatif** ;
- `created_at` : date et heure avec fuseau, **remplie par la base** à l'insertion.

### `Author` (table `author`) et `Book` (table `book`)
Reprenez vos classes de l'ex. 08 :
- `Author` : `id`, `name` (100 caractères max) ;
- `Book` : `id`, `title` (200 caractères max), `author_id` (clé étrangère vers `author`).
- **Relation 1-N dans les deux sens :** `author.books` (liste) et `book.author`, reliées par `back_populates`.
- **Cascade :** quand on ajoute un auteur à la session, ses livres doivent suivre automatiquement, et supprimer un auteur supprime ses livres.
- Ajoutez un `__repr__` à `Author` et à `Book` : vos `print` seront lisibles.

### `Loan` (table `loan`) — nouveau
Un emprunt relie un membre et un livre :
- `id` : clé primaire ;
- `member_id` : clé étrangère vers `member`. Si le membre est supprimé, **la base** supprime ses emprunts ;
- `book_id` : clé étrangère vers `book` ;
- `loaned_at` : date et heure avec fuseau, remplie par la base par défaut ;
- `due_date` : date et heure avec fuseau, obligatoire ;
- `returned_at` : date et heure avec fuseau, facultative (vide tant que le livre n'est pas rendu).

Contraintes à déclarer **dans la base** (`__table_args__`) :
- une contrainte CHECK nommée `ck_loan_dates` : la date de retour prévue est postérieure à la date d'emprunt ;
- un index nommé `ix_loan_member_due` sur (`member_id`, `due_date`).

Relations à ajouter : `loan.member` ↔ `member.loans` et `loan.book` ↔ `book.loans`.

## Partie 2 — `seed.py`

Écrivez `seed.py`, qui repart d'une base vide à chaque lancement :
1. Appelez `reset_schema()` (dans `db.py`), puis créez les tables à partir des métadonnées de `Base`.
2. Dans **une seule transaction**, créez les données ci-dessous.
3. Contrainte : n'ajoutez à la session que les **auteurs** et les **membres**. Les livres et les emprunts doivent y entrer par les relations.

### Les auteurs et leurs livres (10 livres)

| Auteur | Livres, dans cet ordre |
|---|---|
| Ursula K. Le Guin | Les Dépossédés · La Main gauche de la nuit · Le Sorcier de Terremer · Le Nom du monde est forêt |
| Frank Herbert | Dune · Le Messie de Dune · Les Enfants de Dune |
| Agatha Christie | Le Crime de l'Orient-Express · Ils étaient dix · Mort sur le Nil |

Créez les auteurs dans cet ordre. Attention à l'orthographe de **« Dune »** : l'ex. 12 la recherche.

### Les membres

| Nom | E-mail |
|---|---|
| Alice | alice@example.org |
| Bob | bob@example.org |
| Chloé | chloe@example.org |
| David | david@example.org |

### Les emprunts

Chaque emprunt a commencé il y a N jours (calculé à partir de **maintenant**, en UTC) et doit être rendu 21 jours après son début.

| Membre | Livre | Commencé il y a |
|---|---|---|
| Alice | Les Dépossédés | 2 jours |
| Alice | Dune | 5 jours |
| Alice | Le Crime de l'Orient-Express | 10 jours |
| Bob | Dune | 20 jours |
| Chloé | La Main gauche de la nuit | 3 jours |
| David | Ils étaient dix | 40 jours |

Ces durées ne sont pas choisies au hasard : l'ex. 12 cherche les emprunts des 30 derniers jours.

## Partie 3 — Vérifier

À la fin de `seed.py`, dans une **nouvelle** session :
1. Affichez le nombre de lignes de chaque table (une requête `select` avec `func.count()` par modèle).
2. Essayez d'enregistrer un emprunt dont la date de retour prévue est **la veille** de sa date d'emprunt. Interceptez l'erreur, annulez la transaction et affichez le nom de l'erreur PostgreSQL d'origine.

**Résultat attendu** avec `uv run python seed.py` :

```
author 3
book 10
member 4
loan 6
CHECK refusé : CheckViolation
```

**Pas de passage à l'ex. 12 sans ce résultat.** Relancer le script doit donner exactement la même chose.

## Si vous bloquez

- **`NoReferencedTableError` ou relation introuvable :** vérifiez les noms de tables dans vos `ForeignKey` (`"author.id"`, pas `"Author.id"`).
- **`back_populates` qui plante :** le nom donné d'un côté doit être exactement l'attribut de l'autre côté.
- **Les livres ne sont pas insérés :** regardez la `cascade` de `Author.books`.
- **Pas de `CheckViolation` :** la contrainte est-elle bien dans `__table_args__`, et avez-vous recréé les tables ?

## Bonus, si vous avez fini

- Faites afficher, pour chaque membre, les titres de ses emprunts en cours. Activez `echo` : combien de requêtes partent ?
- Supprimez Bob dans une session à part : que deviennent ses emprunts ? Pourquoi ?
