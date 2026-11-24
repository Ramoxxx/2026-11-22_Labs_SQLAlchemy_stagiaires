import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()  # lit le fichier .env du dossier courant s'il existe


def make_url(driver:str = "postgresql+psycopg"):
    return URL.create(
        driver,
        username=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT"),
        database=os.environ.get("DB_NAME"),
    )

engine = create_engine(
    make_url(),
    echo=int(os.environ.get("SQL_ECHO", 1)),
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

def reset_schema():
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))

