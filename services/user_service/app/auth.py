from fastapi import FastAPI,HTTPException,Depends  # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # type: ignore
from jose import JWTError, jwt  # type: ignore
from passlib.context import CryptContext  # type: ignore
from datetime import datetime, timedelta  # type: ignore
from sqlmodel import Session  # type: ignore
from typing import Annotated  # type: ignore
from app.db import get_session

from typing import Optional
from app.schema import TokenData

auth_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "202c1ce08346feccacb35b21c9ce8c97f9728c5a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta:timedelta|None = None):
  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str) -> dict:
  try:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  except JWTError:
    raise HTTPException(
      status_code=401,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )


async def current_user(token: Annotated[str, Depends(auth_scheme)], session: Annotated[Session, Depends(get_session)]):
  payload = decode_jwt(token)
  username: Optional[str] = payload.get("sub")
  if username is None:
    raise HTTPException(
      status_code=401,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )
  from app.crud import db_user
  token_data = TokenData(username=username)     
  user = await db_user(session ,username=token_data.username)

  if user is None:
    raise HTTPException(
      status_code=401,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )
  return user

