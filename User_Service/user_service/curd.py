from uuid import uuid4 # type: ignore
from fastapi import Depends, HTTPException, status # type: ignore
from sqlmodel import Session, select # type: ignore
from service1.settings import ALGORITHM, SECRET_KEY # type: ignore
from typing import Annotated # type: ignore
from jose import JWTError, jwt # type: ignore
from service1.services import * # type: ignore
from service1.models import * # type: ignore
from service1 import settings # type: ignore
# from service1.db import db_session
# from aiokafka import AIOKafkaProducer
# import service1.user_pb2 as user_pb2


async def signup_user(user: UserCreate, db: Session, producer: Annotated[AIOKafkaProducer, Depends(produce_message)]) -> User:
    """
    Create a new user.
    Args:
        user (UserCreate): The user data.
        db (Session): The database session.
    Returns:
        User: The user object.
    """
    search_user_by_email = db.exec(select(User).where(User.email == user.email)).first()
    if search_user_by_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Email id already registered")
    
    search_user_by_username = db.exec(select(User).where(User.username == user.username)).first()
    if search_user_by_username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Try Different username")
    
    hashed_password = get_password_hash(user.password)

    new_user = User(id = uuid4(), username=user.username, email=user.email, password=hashed_password, role=user.role)
    add_consumer_to_kong(new_user.username)
    user_data = user_pb2.User(username=new_user.username, email=new_user.email)
    serialized_user = user_data.SerializeToString()
    await producer.send_and_wait(settings.KAFKA_PRODUCER_TOPIC, serialized_user)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
