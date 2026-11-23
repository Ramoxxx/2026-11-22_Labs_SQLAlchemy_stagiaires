from sqlalchemy import text, MetaData, Table, Column, Integer, String, delete, insert, update, select
from db import engine, reset_schema

reset_schema()

metadata = MetaData()

author = Table(
    "author", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
)

metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(insert(author),
                 [{"name": "Agatha"},
                  {"name": "Aristote"},
                  {"name": "JJRousseau"}])

requete = select(author.c.id, author.c.name).where(author.c.name.like("%e%")).order_by(author.c.name)
print(requete)

with engine.connect() as conn:
    for row in conn.execute(requete):
        print(row.id, row.name)



#with engine.begin() as conn :
 #   conn.execute(text("CREATE TABLE author(id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL)"))
  #  conn.execute(text("INSERT INTO author(name) VALUES(:nom)"), [{"nom": "Agatha Christie"},{"nom": "Jean-Jacques Rousseau"}])

print("__________")

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name FROM author WHERE name LIKE :debut"), {"debut": "A%"})
    for row in result :
        print(row.id, row.name)