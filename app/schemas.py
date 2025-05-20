# app/schemas.py
from pydantic import BaseModel, EmailStr

# Auth
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True
