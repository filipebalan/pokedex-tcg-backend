from sqlalchemy.orm import DeclarativeBase

# Eu defino a classe base da qual todas as tabelas do SQLAlchemy irão herdar
class Base(DeclarativeBase):
    pass