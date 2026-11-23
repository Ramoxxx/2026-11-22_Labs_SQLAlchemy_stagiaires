from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Tag(Base):
    __tablename__ = "tag"