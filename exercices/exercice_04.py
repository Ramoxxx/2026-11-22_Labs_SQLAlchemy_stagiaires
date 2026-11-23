from sqlalchemy import MetaData, Table, Column, Integer, String
from db import engine

metadata = MetaData()

book = Table(
    "book",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("year", Integer),
    Column("isbn", String(17), unique=True)
)

metadata.create_all(engine)
metadata.create_all(engine)