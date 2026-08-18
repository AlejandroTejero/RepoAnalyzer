# Lectura variables entorno
import os
from dotenv import load_dotenv
# Conexion de PostgreSQL
from sqlalchemy import create_engine
# Submodulo ORM que permite trabajar con python
from sqlalchemy.orm import sessionmaker

from database.models import Base

# Engine para database
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Crea todas las tablas definidas en models.py si no existen todavía."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Devuelve una sesión nueva para hablar con la base de datos."""
    return SessionLocal()