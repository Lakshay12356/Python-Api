from sqlalchemy.orm import Session
from uuid import UUID
import uuid
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from fastapi import UploadFile
from .models import Document

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Product
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, user_id: UUID):
    return db.query(models.Product).filter(models.Product.user_id == user_id).all()

def get_product(db: Session, product_id: UUID):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: UUID, updated_product: schemas.ProductCreate):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return None
    for key, value in updated_product.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: UUID):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()

def update_dead_stock_status(db: Session):
    six_months_ago = datetime.utcnow().date() - timedelta(days=180)

    outdated_products = db.query(models.Product).filter(
        models.Product.date_of_purchase < six_months_ago,
        models.Product.dead_stock == False
    ).all()

    for product in outdated_products:
        product.dead_stock = True

    db.commit()
    return len(outdated_products)

# Delivery Partner
def create_delivery_partner(db: Session, partner: schemas.DeliveryPartnerCreate):
    db_partner = models.DeliveryPartner(name=partner.name)
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return db_partner

def get_all_partners(db: Session):
    return db.query(models.DeliveryPartner).all()

# Delivery
def create_delivery(db: Session, delivery: schemas.DeliveryCreate):
    product = db.query(models.Product).filter(models.Product.product_code == delivery.product_code).first()
    if not product:
        raise ValueError("Product not found")

    if delivery.quantity > product.units:
        raise ValueError("Not enough units in stock")

    partner = db.query(models.DeliveryPartner).filter(models.DeliveryPartner.name == delivery.partner_name).first()
    if not partner:
        raise ValueError("Delivery partner not found")

    product.units -= delivery.quantity

    new_delivery = models.Delivery(
        product_id=product.id,
        quantity=delivery.quantity,
        partner_id=partner.id,
        address=delivery.address,
        status="intransit",
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)

    return schemas.Delivery(
        id=new_delivery.id,
        product_code=product.product_code,
        partner_name=partner.name,
        quantity=new_delivery.quantity,
        address=new_delivery.address,
        status=new_delivery.status,
        created_at=new_delivery.created_at,
    )

def get_all_deliveries(db: Session):
    deliveries = db.query(models.Delivery).all()
    results = []

    for d in deliveries:
        product = db.query(models.Product).filter(models.Product.id == d.product_id).first()
        partner = db.query(models.DeliveryPartner).filter(models.DeliveryPartner.id == d.partner_id).first()

        results.append(schemas.Delivery(
            id=d.id,
            product_code=product.product_code,
            partner_name=partner.name,
            quantity=d.quantity,
            address=d.address,
            status=d.status,
            created_at=d.created_at
        ))

    return results

def auto_cancel_stale_deliveries(db: Session):
    six_days_ago = datetime.utcnow().date() - timedelta(days=6)
    
    stale_deliveries = db.query(models.Delivery).filter(
        models.Delivery.created_at < six_days_ago,
        models.Delivery.status != "delivered",
        models.Delivery.status != "cancelled"
    ).all()

    for d in stale_deliveries:
        d.status = "cancelled"
        # Optional: Restore product quantity
        product = db.query(models.Product).filter(models.Product.id == d.product_id).first()
        if product:
            product.units += d.quantity

    db.commit()
    return len(stale_deliveries)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_document(db: Session, user_id: UUID, file: UploadFile):
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    new_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    doc = Document(
        id=file_id,
        filename=file.filename,
        file_type=file.content_type,
        file_path=file_path,
        user_id=user_id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_documents_by_user(db: Session, user_id: UUID):
    return db.query(Document).filter(Document.user_id == user_id).all()
