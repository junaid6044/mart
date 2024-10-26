from fastapi import FastAPI,Depends,HTTPException
from contextlib import asynccontextmanager
from app.db import create_table
from app.image_routes import router2
from app.rout import router
from app.kafka import kafka_consumer
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifspan event is started")
    print("table creating....")
    create_table()
    print("creating table succesfully")
    task = asyncio.create_task(kafka_consumer('product_topic','broker:19092'))
    task2 = asyncio.create_task(kafka_consumer("product_image",'broker:19092'))
    yield
    
    
app = FastAPI(lifespan=lifespan,
               title="FastAPI Product Service",
               description="This is a FastAPI Product Service",
               version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "welcome to the product Service"}

app.include_router(router=router)
app.include_router(router=router2)

