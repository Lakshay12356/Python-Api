from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from uuid import UUID
from fastapi import status
from . import models, schemas, crud
from .database import engine, SessionLocal
from .auth import verify_password, create_token, SECRET_KEY, ALGORITHM

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = crud.get_user_by_email(db, email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    crud.create_user(db, user)
    return {"msg": "User created successfully"}

@app.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(data={"sub": user.email, "username": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductBase, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product_data = schemas.ProductCreate(**product.dict(), user_id=current_user.id)
    return crud.create_product(db, product_data)

@app.get("/products/", response_model=list[schemas.Product])
def get_all_products(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.get_products(db, user_id=current_user.id)

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: UUID, updated: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.update_product(db, product_id, updated)

@app.delete("/products/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    crud.delete_product(db, product_id)
    return {"msg": "Deleted successfully"}

@app.get("/check-dead-stock")
def check_dead_stock(db: Session = Depends(get_db)):
    updated_count = crud.update_dead_stock_status(db)
    return {"updated": updated_count}

@app.post("/delivery-partners/", response_model=schemas.DeliveryPartner)
def create_partner(partner: schemas.DeliveryPartnerCreate, db: Session = Depends(get_db)):
    return crud.create_delivery_partner(db, partner)

@app.get("/delivery-partners/", response_model=list[schemas.DeliveryPartner])
def list_partners(db: Session = Depends(get_db)):
    return crud.get_all_partners(db)

@app.post("/deliveries/", response_model=schemas.Delivery, status_code=status.HTTP_201_CREATED)
def create_delivery(delivery: schemas.DeliveryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return crud.create_delivery(db, delivery)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/deliveries/", response_model=list[schemas.Delivery])
def list_deliveries(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.get_all_deliveries(db)
