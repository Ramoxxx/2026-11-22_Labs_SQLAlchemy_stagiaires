from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Book, Member
from db import engine

with Session(engine) as session, session.begin():
    print("\n1. Dune books :")
    stmt_books = select(Book).where(Book.title.ilike("%dune%"))
    books = session.scalars(stmt_books).all()    
    print("------")
    for book in books:
        print(book.title)
    print("------\n")

    print("\n2. book with id == 5 :")
    print("------")
    print(session.get(Book,5))

    print("\n3. Member with email bob@example.org :")
    print("------")
    stmt_member = select(Member).where(Member.email == 'bob@example.org')
    member = session.scalars(stmt_member).one()
    print(member.name)
    print("------\n")

    print("\n==========")


# session = Session(engine)
# stmt = select(Book).where(Book.title.ilike("%dune%"))
# books = session.scalars(stmt).all()
# print(books)