from fastapi import FastAPI # type: ignore
import uvicorn # type: ignore
from jose import jwt, JWTError # type: ignore
from datetime import datetime, timedelta # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from fastapi import Depends # type: ignore
from typing import Annotated # type: ignore

ALGORITHM = "HS256"
SECRET_KEY = "A Secure Secret Key"


app = FastAPI()

users = [
  {"name": "Alice", "age": 25, "email": "alice@example.com"},
  {"name": "Bob", "age": 30, "email": "bob@example.com"},
  {"name": "Charlie", "age": 22, "email": "charlie@example.com"},
  {"name": "Diana", "age": 28, "email": "diana@example.com"}
]



@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):
  """
  Understanding the login system
  -> Takes form_data that have username and password
  """
  
  # We will add Logic here to check the username/email and password
  # If they are valid we will return the access token
  # If they are invalid we will return the error message

  access_token_expires = timedelta(minutes=1)
  generated_token = create_access_token(subject=form_data.username, expires_delta=access_token_expires)

  # return {"username": form_data.username, "password": form_data.password}
  return {"username": form_data.username, "access_token": generated_token}

@app.get("/")
def root():
  return {
    "Name": "Muhammad Junaid",
    "Class_Detail": "Class 8(6 10 2024)"
  }


@app.get("/users/")
def read_users():
  return users


def create_access_token(subject: str , expires_delta: timedelta) -> str:
  expire = datetime.utcnow() + expires_delta
  to_encode = {"exp": expire, "sub": str(subject)}
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

@app.get("/get_access_token")
def get_access_token(user_name: str):
  access_token_expires = timedelta(minutes=1)
  access_token = create_access_token(subject=user_name, expires_delta=access_token_expires)
  return {"access_token": access_token}


def decode_access_token(access_token: str):
  decoded_jwt = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
  return decoded_jwt

@app.get("/decode_token")
def decoding_token(access_token: str):
  try:
    decoded_token_data = decode_access_token(access_token)
    return {"decoded_token": decoded_token_data}
  except JWTError as e:
    return {"error": str(e)}


def start():
  uvicorn.run("mart_api.main:app", host="127.0.0.1", port=8000, reload=True)
