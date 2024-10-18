from fastapi import FastAPI, Depends, HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, AsyncGenerator
from typing_extensions import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select
from app import settings, kafka, db
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer # type: ignore
import asyncio
import json
from passlib.context import CryptContext

# Configuration for JWT
ALGORITHM = "HS256"
SECRET_KEY = "A Secure Secret Key"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection string and engine
connection = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg2")
engine = create_engine(connection)

# JWT token generation function
def create_access_token(subject: str, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
  expire = datetime.utcnow() + expires_delta
  to_encode = {"exp": expire, "sub": subject}
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt 

# Password hashing functions
def hash_password(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


# # Initialize FastAPI app
# app = FastAPI()


# # Token validation function
# def validate_token(token: str):
#   credentials_exception = HTTPException(
#     status_code=401,
#     detail="Could not validate credentials",
#     headers={"WWW-Authenticate": "Bearer"},
#   )
#   try:
#     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     username: str = payload.get("sub")
#     if username is None:
#       raise credentials_exception
#   except JWTError:
#     raise credentials_exception

# # Example endpoint to use the token (optional)
# @app.get("/secure-endpoint")
# def secure_endpoint(token: str):
#   validate_token(token)
#   return {"message": "This is a secure endpoint!"}

