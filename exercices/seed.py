
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import engine, reset_schema
from models import Author, Base, Book, Loan, Member, Tag

NOW = datetime.now(timezone.utc)

reset_schema()
Base.metadata.create_all(engine)

with Session(engine) as session, session.begin():
    sf, fantasy, classique, prix, polar = (
        Tag(name=n) for n in ("sf", "fantasy", "classique", "prix-hugo", "polar"))

    leguin = Author(name="Ursula K. Le Guin")
    herbert = Author(name="Frank Herbert")
    christie = Author(name="Agatha Christie")
    leguin.books = [
        Book(title="Les Dépossédés", year=1974, isbn="978-2221252147", tags=[sf, prix]),
        Book(title="La Main gauche de la nuit", year=1969, isbn="978-2253072058", tags=[sf, prix, classique]),
        Book(title="Le Sorcier de Terremer", year=1968, isbn="978-2253113690", tags=[fantasy]),
        Book(title="Le Nom du monde est forêt", year=1972, isbn="978-2253072201", tags=[sf]),
    ]
    herbert.books = [
        Book(title="Dune", year=1965, isbn="978-2266320481", tags=[sf, classique, prix]),
        Book(title="Le Messie de Dune", year=1969, isbn="978-2266320498", tags=[sf]),
        Book(title="Les Enfants de Dune", year=1976, isbn="978-2266320504", tags=[sf]),
    ]
    christie.books = [
        Book(title="Le Crime de l'Orient-Express", year=1934, isbn="978-2702449028", tags=[polar, classique]),
        Book(title="Ils étaient dix", year=1939, isbn="978-2253010586", tags=[polar]),
        Book(title="Mort sur le Nil", year=1937, isbn="978-2702449066", tags=[polar]),
    ]

    alice = Member(email="alice@example.org", name="Alice")
    bob = Member(email="bob@example.org", name="Bob")
    chloe = Member(email="chloe@example.org", name="Chloé")
    david = Member(email="david@example.org", name="David")

    session.add_all([leguin, herbert, christie, alice, bob, chloe, david])

    emprunts = [
        (alice, leguin.books[0], 2), (alice, herbert.books[0], 5), (alice, christie.books[0], 10),
        (bob, herbert.books[0], 20), (chloe, leguin.books[1], 3), (david, christie.books[1], 40),
    ]
    for membre, livre, jours in emprunts:
        debut = NOW - timedelta(days=jours)
        membre.loans.append(Loan(book=livre, loaned_at=debut, due_date=debut + timedelta(days=21)))

with Session(engine) as session:
    for model in (Author, Book, Tag, Member, Loan):
        print(model.__tablename__, session.scalar(select(func.count()).select_from(model)))

    stmt = select(Book).join(Book.tags).where(Tag.name == "classique").order_by(Book.id)
    print("classiques :", session.scalars(stmt).all())

    # session.add(Loan(member_id=1, book_id=1, loaned_at=NOW, due_date=NOW - timedelta(days=1)))
    try:
        session.commit()
        print("commit done")
    except IntegrityError as exc:
        session.rollback()
        print("CHECK refusé :", type(exc.orig).__name__)
