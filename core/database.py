# database.py

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de .env

DATABASE_URL = os.getenv("DATABASE_URL")

# Crear engine
engine = create_engine(DATABASE_URL, echo=True)

# Crear session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para FastAPI
def get_session():
    with Session(engine) as session:
        yield session

