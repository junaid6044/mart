from contextlib import asynccontextmanager # type: ignore
from sqlmodel import SQLModel, create_engine, Session, select # type: ignore
from fastapi import FastAPI # type: ignore
from service1 import settings # type: ignore

connection_string = str(settings.DATABASE_URL)

engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

# Create the tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database connection")
    create_db_and_tables()
    yield

def db_session():
    with Session(engine) as session:
        yield session