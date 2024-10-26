from sqlmodel import SQLModel, Field, create_engine , Relationship
from typing import Optional,List
from pydantic import BaseModel

class Product(SQLModel,table=True):
    product_id: Optional[int] = Field(default=None, primary_key=True)
    product_name: str
    product_price: int
    product_quantity: int
    product_category: str
    images: List["ProductImage"] = Relationship(back_populates="product")
    
class ProductImage(SQLModel,table=True):
    image_id: Optional[int] = Field(default=None, primary_key=True)
    image_url: str
    image_name: str
    product_id: Optional[int] = Field(foreign_key="product.product_id")
    product: Optional["Product"] = Relationship(back_populates="images")

class ProductAdd(BaseModel):
    product_name: str
    product_price: int
    product_quantity: int
    product_category: str
    
    
class UpdateProductImage(BaseModel):
    image_url:str
    image_name:str
    product_id:int

