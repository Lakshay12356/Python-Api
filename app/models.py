from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    products = relationship("Product", back_populates="user", cascade="all, delete")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(String)
    batch_number = Column(String)
    product_name = Column(String)
    product_code = Column(String, unique=True)
    category = Column(String)
    brand = Column(String)
    purchase_price = Column(Float)
    listing_price = Column(Float)
    units = Column(Integer)
    date_of_purchase = Column(Date)
    dead_stock = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="products")