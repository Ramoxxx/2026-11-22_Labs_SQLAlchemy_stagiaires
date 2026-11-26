
from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String, Table, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


book_tag = Table(
    "book_tag",
    Base.metadata,
    Column("book_id", ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class Member(Base):
    __tablename__ = "member"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    loans: Mapped[list["Loan"]] = relationship(back_populates="member", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Member({self.name!r})"


class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Author({self.name!r})"


class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    year: Mapped[int | None]
    isbn: Mapped[str | None] = mapped_column(String(17), unique=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))

    author: Mapped["Author"] = relationship(back_populates="books")
    tags: Mapped[list["Tag"]] = relationship(secondary=book_tag, back_populates="books")
    loans: Mapped[list["Loan"]] = relationship(back_populates="book")

    def __repr__(self) -> str:
        return f"Book({self.title!r})"


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    books: Mapped[list["Book"]] = relationship(secondary=book_tag, back_populates="tags")

    def __repr__(self) -> str:
        return f"Tag({self.name!r})"


class Loan(Base):
    __tablename__ = "loan"
    __table_args__ = (
        CheckConstraint("due_date > loaned_at", name="ck_loan_dates"),
        Index("ix_loan_member_due", "member_id", "due_date"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"))
    loaned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    member: Mapped["Member"] = relationship(back_populates="loans")
    book: Mapped["Book"] = relationship(back_populates="loans")
