from sqlmodel import SQLModel, Field, Enum, Column # type: ignore
from typing import Optional # type: ignore
from uuid import UUID # type: ignore
from datetime import timedelta # type: ignore
import enum # type: ignore

class UserRole(str, enum.Enum):
  admin = "admin"
  user = "user"

class Token(SQLModel):
  access_token: str
  refresh_token: str
  token_type: str
  expires_in: timedelta

class TokenData(SQLModel):
  username: str

class UserBase(SQLModel):
  username: str = Field(nullable=False)
  password: str = Field(nullable=False)

class Userlogin(UserBase):
  pass

class UserUpdate(SQLModel):
  username: str

class User(UserBase, table=True):
  id: Optional[UUID] = Field(primary_key=True, index=True)
  email: str = Field(index=True, unique=True, nullable=False)
  role: UserRole = Field(default=UserRole.user, sa_column=Column("role", Enum(UserRole)))

class UserCreate(UserBase):
  email: str
  role: UserRole = Field(default=UserRole.user, sa_column=Column("role", Enum(UserRole)))

  