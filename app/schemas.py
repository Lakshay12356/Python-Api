from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from uuid import UUID

# Auth
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: UUID
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

# Products
class ProductBase(BaseModel):
    supplier_code: str
    batch_number: str
    product_name: str
    product_code: str
    category: str
    brand: str
    purchase_price: float
    listing_price: float
    units: int
    date_of_purchase: Optional[date] = None
    dead_stock: Optional[bool] = False

class ProductCreate(ProductBase):
    user_id: UUID

class Product(ProductBase):
    id: UUID

    class Config:
        orm_mode = True