# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select, Sequence # type: ignore
from fastapi import FastAPI, Depends # type: ignore
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer # type: ignore
import json


class Order (SQLModel):
    id: Optional[int] = Field(default=None)
    username: str
    product_id: int
    product_name: str
    product_price: int

# class Todo(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     content: str = Field(index=True)


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

#engine = create_engine(
#    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
#)


def create_db_and_tables()->None: # type: ignore
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# @asynccontextmanager
# async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
#     print("Creating tables..")
#     # create_db_and_tables()
    yield

app = FastAPI()

# app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
#     version="0.0.1",
#     servers=[
#         {
#             "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
#             "description": "Development Server"
#         }
#         ])

# def get_session():
#     with Session(engine) as session:
#         yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/create_order")
async def create_order(order: Order):
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    orderJSON=json.dumps(order.__dict__).encode('utf-8')
    print("orderJSON")
    print(orderJSON)
    try:
        # Produce message
        await producer.send_and_wait("order", orderJSON)
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

    return orderJSON


@app.get("/read_order")
async def read_order():
    consumer = AIOKafkaConsumer('order',bootstrap_servers='broker:19092', group_id="order_consumer")
    # Get cluster layout and initial topic/partition leadership information
    await consumer.start()
    try:
        # Produce message
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        # Wait for all pending messages to be delivered or expire.
        await consumer.stop()

    return {"data": consumer}

# @app.post("/todos/", response_model=Todo)
# def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)])->Todo:
#         session.add(todo)
#         session.commit()
#         session.refresh(todo)
#         return todo


# @app.get("/todos/", response_model=list[Todo])
# def read_todos(session: Annotated[Session, Depends(get_session)]):
#         todos = session.exec(select(Todo)).all()
#         return todos
