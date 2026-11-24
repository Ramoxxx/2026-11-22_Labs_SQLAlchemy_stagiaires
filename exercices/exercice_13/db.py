"""Exercice 03 : configuration de la connexion, sans secret dans le code.

Ce module est réutilisé par toutes les solutions suivantes.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

load_dotenv()  # lit le fichier .env du dossier courant s'il existe


def make_url(driver: str = "postgresql+psycopg") -> URL:
    return URL.create(
        driver,
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ.get("DB_NAME", "bibliotheque"),
    )


engine = create_engine(
    make_url(),
    echo=os.environ.get("SQL_ECHO") == "1",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)


def reset_schema() -> None:
    """Réservé aux exercices : supprime TOUTES les tables du schéma public."""
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
