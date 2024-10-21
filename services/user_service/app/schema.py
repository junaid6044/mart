from sqlmodel import SQLModel, Field  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import Annotated,Optional  # type: ignore
from fastapi import Form  # type: ignore

class User(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  userName: str
  email:str
  password: str

class update_user(BaseModel):
  user_name: str|None = None
  email:str|None = None
  password: str|None = None 
    
class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  username: Optional[str] = None
    
class RegisterUser(BaseModel):
  user_name : Annotated[str, Form()]
  email : Annotated[str, Form()]
  password : Annotated[str, Form()]
        
class token(BaseModel):
  access_token: str
  token_type: str

