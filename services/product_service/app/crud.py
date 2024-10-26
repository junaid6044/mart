from typing import Annotated
from sqlmodel import Session,select
from fastapi import Depends,HTTPException,status
from sqlalchemy.exc import SQLAlchemyError
from app.scehma import Product,ProductAdd # type: ignore
from app.db import get_session # type: ignore
from app.product_pb2 import Products  # type: ignore
from app.kafka import kafka_producer # type: ignore
from aiokafka import AIOKafkaProducer # type: ignore


async def add_product(data:Annotated[ProductAdd,Depends()],
                      session:Annotated[Session,Depends(get_session)],
                      producer:Annotated[AIOKafkaProducer,Depends(kafka_producer)]):
    new_product = Product(product_name=data.product_name,product_price=data.product_price,product_category=data.product_category,
                          product_quantity=data.product_quantity)
    product_data = Products(product_name=data.product_name,product_price=data.product_price,product_category=data.product_category,
                          product_quantity=data.product_quantity)
    serailized = product_data.SerializeToString()
    await producer.send('product_topic',serailized)
    
    try:
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"adding product error: {e}"
        )
        
    return {
        "Product Created Succesfully" : new_product
    }


async def get_products(session:Annotated[Session,Depends(get_session)]):
    try:
        products = session.exec(select(Product)).all()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting products error: {e}"
        )
    return {
        "Products" : products
    }
    
    
async def get_product_by_id(id:int,session:Annotated[Session,Depends(get_session)]):
    try:
        product = session.exec(select(Product).where(Product.product_id == id)).one()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"getting product error: {e}"
        )
    return {
        "Product" : product
    }


async def update_product(id:int,data:ProductAdd,session:Annotated[Session,Depends(get_session)]):
    try:
        product = session.exec(select(Product).where(Product.product_id == id)).one()
        product.product_name = data.product_name
        product.product_price = data.product_price
        product.product_quantity = data.product_quantity
        product.product_category = data.product_category
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"updating product error: {e}"
        )
    return {
        "Product" : product
    }
    
async def delete_product(id:int,session:Annotated[Session,Depends(get_session)]):
    try:
        product = session.exec(select(Product).where(Product.product_id == id)).one()
        session.delete(product)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"deleting product error: {e}"
        )
    return {
        f"product with id {id} deleted succesfully"
    }
