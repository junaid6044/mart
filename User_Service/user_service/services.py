import random # type: ignore
from jose import jwt # type: ignore
from passlib.context import CryptContext # type: ignore
from fastapi.security import OAuth2PasswordBearer # type: ignore
from service1.settings import * # type: ignore
from service1.models import * # type: ignore
from datetime import datetime, timedelta, timezone # type: ignore
from sqlmodel import Session, select # type: ignore
from fastapi import HTTPException, status # type: ignore
from pydantic import EmailStr # type: ignore
from typing import Union, Any # type: ignore
import requests # type: ignore
import json # type: ignore

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
  """
  Verify the password using the hash stored in the database.
  Args:
    plain_password (str): The password entered by the user.
    hashed_password (str): The password stored in the database.
  Returns:
    bool: True if the password is correct, False otherwise.
  """
  return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
  """
  Hash the password before storing it in the database.
  Args:
    password (str): The password entered by the user.
  Returns:
    str: The hashed password.
  """
  return pwd_context.hash(password)
