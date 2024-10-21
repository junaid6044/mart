from typing import Annotated  # type: ignore
from fastapi import FastAPI, Depends,HTTPException  # type: ignore
from sqlmodel import Session,select  # type: ignore
from passlib.context import CryptContext # type: ignore
from passlib.exc import UnknownHashError  # type: ignore
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer # type: ignore
from app.db import get_session
from app.schema import User,update_user,RegisterUser
from app.user_pb2 import Newuser # type: ignore
from app.kafka import produce_message,consume_messages

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def verify_password(plain_password,password):
  try:  
    return pwd_context.verify(plain_password,password)
  except UnknownHashError:
    print("Password hash could not be identified.")

def get_password_hash(password: str):
  return pwd_context.hash(password)

async def db_user(session: Annotated[Session, Depends(get_session)],
                   username: str | None = None,
                   email: str | None = None):
  user_record = select(User).where(User.userName == username)
  user = session.exec(user_record).first()

  if not user:
    user_record = select(User).where(User.email == email)
    user = session.exec(user_record).first()

  return user

async def auth_user(username:str| None ,password:str,
                     session: Annotated[Session, Depends(get_session)]):
    data_user = await db_user(session=session,username=username)
    if not data_user:
      return False
    if not verify_password(password,data_user.password):
      return False
    return data_user

async def register_user(user:RegisterUser , session: Annotated[Session, Depends(get_session)],
                        producer:Annotated[AIOKafkaProducer,Depends(produce_message)]):
  existing_user = await db_user(username=user.user_name, email=user.email, session=session)  # Corrected call
  if existing_user:
    raise HTTPException(status_code=400, detail="User already exists")
  new_user = User(userName=user.user_name, email=user.email, password=get_password_hash(user.password))
  user_data =Newuser(userName=new_user.userName, email=new_user.email)
  serialized_user = user_data.SerializeToString()
  await producer.send_and_wait('userService', serialized_user)
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  return new_user


async def user_patch_update(user_record,edit_user):
  if edit_user.user_name is not None and edit_user.user_name != "":
    user_record.user_name = edit_user.user_name
  if edit_user.email is not None and edit_user.email != "":
    user_record.email = edit_user.email
  if edit_user.password is not None and edit_user.password != "":
    user_record.password = get_password_hash(edit_user.password)
  return user_record
        
