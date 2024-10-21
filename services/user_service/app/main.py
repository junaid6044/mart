from fastapi import FastAPI,Depends,HTTPException  # type: ignore
from contextlib import asynccontextmanager  # type: ignore
import logging  # type: ignore
import asyncio  # type: ignore
from sqlmodel import Session,select  # type: ignore
from typing import Annotated  # type: ignore
from aiokafka import AIOKafkaProducer  # type: ignore
from datetime import datetime, timedelta  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from app.schema import User,token,RegisterUser,update_user
from app.db import create_table, get_session
from app.crud import register_user,auth_user,verify_password,user_patch_update
from app.kafka import produce_message,consume_messages
from app.auth import current_user
from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

@asynccontextmanager
async def lifespan(app: FastAPI):
	print("lifspan event is started")
	task = asyncio.create_task(consume_messages('userService', 'broker:19092'))
	create_table()
	yield
    
    
app = FastAPI(lifespan=lifespan,
               title="FastAPI User Service",
               description="This is a FastAPI Service",
               version="1.0.0"
)

@app.get("/")
async def root():
	return {"message": "Welcome to the User Services API!"}

@app.post("/register")
async def register(user:RegisterUser,
                   session:Annotated[Session,Depends(get_session)],
                   producer:Annotated[AIOKafkaProducer,Depends(produce_message)]):
	new_user = await register_user(user=user,session=session,producer=producer)
	return new_user

@app.post("/token", response_model=token)
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                session:Annotated[Session,Depends(get_session)]):
	user = await auth_user(form_data.username,form_data.password,session)
	if not user:
		raise HTTPException(
			status_code=404,
			detail="Incorrect username or password")
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
	return {"access_token": access_token, "token_type": "bearer"}

@app.get('/user')
async def get_user(session: Annotated[Session, Depends(get_session)],
									 current_user: Annotated[User, Depends(current_user)]):

	statement = select(User).where(User.id == current_user.id)
	statement1 = session.exec(statement).all()
	return statement1


@app.get('/user/{id}')
async def get_user_data_by_id(id: int,
															session: Annotated[Session, Depends(get_session)],
															current_user: Annotated[User, Depends(current_user)]):
    
	if id != current_user.id:
		raise HTTPException(status_code=403, detail="You are not authorized to access this data")

	user_record = select(User).where(User.id == id)
	user = session.exec(user_record).first()

	if user is None:
		raise HTTPException(status_code=404, detail="User not found")
	
	return user


@app.patch('/user/{id},{password}',response_model=User)
async def updated_user(
	id: int,edit_user:update_user, password:str, 
	session: Annotated[Session, Depends(get_session)],
	current_user: Annotated[User, Depends(current_user)]):

	if id != current_user.id:
		raise HTTPException(status_code=403, detail="You are not authorized to access this data")

	match_user =select(User).where(User.id == id)
	user_record = session.exec(match_user).first()
	if user_record is None:
		raise HTTPException(status_code=404, detail="User not found")
	if not verify_password(password,user_record.password):
		raise HTTPException(status_code=403, detail="Yout password is incorrect please provide the correct password")
	user_record1 = await user_patch_update(user_record,edit_user)
	session.add(user_record1)
	session.commit()
	session.refresh(user_record1)
	return user_record1

@app.delete('/user/{id}')
async def delete_user(id:int,password:str, 
	session: Annotated[Session, Depends(get_session)],
	current_user: Annotated[User, Depends(current_user)]):
		
	if id != current_user.id:
		raise HTTPException(status_code=403, detail="You are not authorized to access this data")
	
	match_user =select(User).where(User.id == id)
	user_record = session.exec(match_user).first()
	if user_record is None:
		raise HTTPException(status_code=404, detail="User not found")
	if not verify_password(password,user_record.password):
		raise HTTPException(status_code=403, detail="You password is incorrect please provide the correct password")
	session.delete(user_record)
	session.commit()
	return {"message":"User deleted successfully"}
