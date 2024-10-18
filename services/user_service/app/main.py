# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError # type: ignore
from datetime import datetime, timedelta
from typing import Optional, AsyncGenerator, Union, Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence
from app import settings, kafka, db, model # type: ignore
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer # type: ignore
import asyncio
from contextlib import asynccontextmanager
import json


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(connection_string)

# Database model for user information
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)  # Add username field for authentication
    password: str = Field(index=True)  # Add password field for authentication

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    # loop.run_until_complete(consume_messages('todos', 'broker:19092'))
    task = asyncio.create_task(kafka.consume_messages('todos', 'broker:19092'))
    db.create_db_and_tables()
    yield

# Initialize FastAPI app and create database tables
app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
    ])


@app.post("/signup", response_model=User)
async def create_user(user: User, session: Annotated[Session, Depends(db.get_session)], producer: Annotated[AIOKafkaProducer, Depends(kafka.get_kafka_producer)]):
    # user.password = hash_password(user.password)  # Hash the password before saving
    user_info = {field: getattr(user, field) for field in user.dict()}
    user_json = json.dumps(user_info).encode("utf-8")
    await producer.send_and_wait("todos", user_json)
    # session.add(user)
    # session.commit()
    # session.refresh(user)
    return {"message": "User saved successfully", "user": user}


# Login endpoint to authenticate users
@app.post("/login")
def login(user: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with Session(engine) as session:
        # Fetch user from database
        statement = select(User).where(User.username == user.username)
        user_in_db = session.exec(statement).first()
    
    if not user_in_db or user.password != user_in_db.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = model.create_access_token(subject=user.username)
    return {"username": user.username, "access_token": token}


@app.get("/users/", response_model=list[User])
def read_users(session: Annotated[Session, Depends(db.get_session)]):
    users = session.exec(select(User)).all()
    return users
