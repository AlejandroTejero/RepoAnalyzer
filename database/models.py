# Tipos de campos de una tabla
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# Relaciones entre tablas
from sqlalchemy.orm import declarative_base, relationship

# Tabla base sobre la que heredan las demas
Base = declarative_base()


# ---- Creaciones de tablas ----

class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)

    commits = relationship("Commit", back_populates="repo")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    commits = relationship("Commit", back_populates="author")


class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True)
    hash = Column(String, unique=True, nullable=False)
    message = Column(String)
    date = Column(DateTime, nullable=False)

    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)

    repo = relationship("Repo", back_populates="commits")
    author = relationship("Author", back_populates="commits")