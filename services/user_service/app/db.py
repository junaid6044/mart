from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import FastAPI
from app import settings

connection_string = str(settings.DATABASE_URL)

engine = create_engine(
  connection_string, connect_args={}, pool_recycle=300
)

# Create the tables
def create_db_and_tables():
  SQLModel.metadata.create_all(engine)


def get_session():
  with Session(engine) as session:
    yield session

