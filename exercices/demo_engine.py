from sqlalchemy import create_engine, text

engine = create_engine("postgresql://app:app@localhost:5432/bibliotheque", echo=True)

# print(engine.driver, engine.dialect.name)

with engine.connect() as conn:
    print(conn.execute(text("SELECT current_user, current_database()")).one())


print(engine.pool.size(), engine.pool.status())