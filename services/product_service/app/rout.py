from fastapi import APIRouter,Depends
from app.db import get_session
from app.scehma import ProductAdd
from app.crud import add_product,get_products,get_product_by_id,update_product,delete_product
from typing import Annotated
from sqlmodel import Session
from aiokafka import AIOKafkaProducer # type: ignore
from app.kafka import kafka_producer
router = APIRouter()


@router.post('/product/add')
async def product_add(product:Annotated[ProductAdd,Depends()],
                      session:Annotated[Session,Depends(get_session)],
                      producer:Annotated[AIOKafkaProducer,Depends(kafka_producer)]):
    products= await add_product(data=product,session=session,producer=producer)
    return products

@router.get('/product/get')
async def product_get(session:Annotated[Session,Depends(get_session)]):
    products= await get_products(session=session)
    return products

@router.get('/single/product/{id}')
async def product_get_by_id(id:int,session:Annotated[Session,Depends(get_session)]):
    products= await get_product_by_id(id=id,session=session)
    return products

@router.patch('/update/product/{id}')
async def product_update(id:int,product:Annotated[ProductAdd,Depends()],session:Annotated[Session,Depends(get_session)]):
    products= await update_product(id=id,data=product,session=session)
    return products

@router.delete('/delete/product/{id}')
async def product_delete(id:int,session:Annotated[Session,Depends(get_session)]):
    products= await delete_product(id=id,session=session)
    return {
        f"product with id {id} deleted succesfully"
    }
