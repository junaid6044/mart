from sqlmodel import SQLModel, create_engine, Session  # type: ignore
from app import settings

connection_string = str(settings.DATABASE_URL).replace(
  "postgresql", "postgresql+psycopg2"
)

if not connection_string:
  raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(connection_string)

def create_table():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session

