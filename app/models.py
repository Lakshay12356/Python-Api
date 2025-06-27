import uuid
from sqlalchemy import Column, String, Float, Date, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    products = relationship("Product", back_populates="user", cascade="all, delete")
    documents = relationship("Document", back_populates="user", cascade="all, delete")

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
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

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="products")

class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)

    deliveries = relationship("Delivery", back_populates="partner", cascade="all, delete")

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    partner_id = Column(UUID(as_uuid=True), ForeignKey("delivery_partners.id"), nullable=False)
    address = Column(String, nullable=False)

    status = Column(String, nullable=False, default="intransit")
    created_at = Column(Date, default=datetime.utcnow)

    product = relationship("Product")
    partner = relationship("DeliveryPartner", back_populates="deliveries")

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(Date, default=datetime.utcnow)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="documents")