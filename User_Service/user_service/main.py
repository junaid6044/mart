from fastapi import FastAPI # type: ignore
import uvicorn # type: ignore
from jose import jwt, JWTError # type: ignore
from datetime import datetime, timedelta # type: ignore
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # type: ignore
from fastapi import HTTPException # type: ignore
from fastapi import Depends # type: ignore
from typing import Annotated # type: ignore
from service1.curd import verify_password # type: ignore


ALGORITHM = "HS256"
SECRET_KEY = "A Secure Secret Key"


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

fake_users_db: dict[str, dict[str, str]] = {
  "ahmad": {
    "username": "ahmad",
    "full_name": "Ahmad Ali",
    "email": "ahmad@example.com",
    "password": "ahmadsecret",
  },
  "mjunaid": {
    "username": "mjunaid",
    "full_name": "Muhammad Junaid",
    "email": "mjunaid@example.com",
    "password": "mjunaidsecret",
  },
}



@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):
  """
  Understanding the login system
  -> Takes form_data that have username and password
  """
  
  # We will add Logic here to check the username/email and password
  # If they are valid we will return the access token
  # If they are invalid we will return the error message

  user_in_fake_db = fake_users_db.get(form_data.username)
  if user_in_fake_db is None:
    raise HTTPException(status_code=400, detail="Incorrect username")

  # if user_in_fake_db["password"] != form_data.password:
  if not verify_password(form_data.password, user_in_fake_db["password"]):
    raise HTTPException(status_code=400, detail="Incorrect password")

  access_token_expires = timedelta(minutes=1)
  # generated_token = create_access_token(subject=form_data.username, expires_delta=access_token_expires)
  access_token = create_access_token(subject=user_in_fake_db["username"], expires_delta=access_token_expires)

  # return {"username": form_data.username, "password": form_data.password}
  # return {"username": form_data.username, "access_token": generated_token}
  return {"access_token": access_token, "token_type": "bearer", "expires_in": access_token_expires.total_seconds() }



@app.post("/signup")
def signup(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]):
  try:
    return signup_user(user, db, producer)
  except Exception as e:
    raise HTTPException(status_code=400,detail=str(e))


@app.get("/")
def root():
  return {
    "Name": "Muhammad Junaid",
    "Class_Detail": "Class 8(6 10 2024)"
  }


@app.get("/users/")
def read_users(token: Annotated[str, Depends(oauth2_scheme)]):
  return fake_users_db

@app.get("/users/me")
def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):
  user_token_data = decode_access_token(token)
  user_in_db = fake_users_db.get(user_token_data["sub"])
  return user_in_db


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
  uvicorn.run("user_service.main:app", host="127.0.0.1", port=8003, reload=True)
