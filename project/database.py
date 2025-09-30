import os
from sqlmodel import SQLModel, create_engine


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # verifies connections before using them
    pool_recycle=300,  # recycles connections after 5 minutes
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
