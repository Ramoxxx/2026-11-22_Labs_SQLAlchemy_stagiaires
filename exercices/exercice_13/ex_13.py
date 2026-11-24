from contextlib import contextmanager

from sqlalchemy import event, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, raiseload, selectinload

from db import engine
from models import Author, Book


@contextmanager
def compteur():
    n = [0]

    def _count(*args):
        n[0] += 1

    event.listen(engine, "before_cursor_execute", _count)
    try:
        yield n
    finally:
        event.remove(engine, "before_cursor_execute", _count)

