"""
TV Panel SQL Server
FastAPI server with MySQL/SQLAlchemy backend and comprehensive CRUD operations.
"""

from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import os
import bcrypt
import jwt
from jwt import PyJWTError
import logging
import json
import csv
import io
from dotenv import load_dotenv
from pathlib import Path

# Import database models
from database import *

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# FastAPI app
app = FastAPI(title="TV Panel SQL API", description="IPTV Client Management System with SQL")
api_router = APIRouter(prefix="/api")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "tv-panel-sql-secret-key-2024")
ALGORITHM = "HS256"
security = HTTPBearer()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ PYDANTIC MODELS ============

class AdminResponse(BaseModel):
    id: int
    login: str
    email: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime

class PanelResponse(BaseModel):
    id: int
    name: str
    url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

class PanelCreate(BaseModel):
    name: str
    url: Optional[str] = None
    description: Optional[str] = None

class AppResponse(BaseModel):
    id: int
    name: str
    url: Optional[str] = None
    package_name: Optional[str] = None
    app_code: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

class AppCreate(BaseModel):
    name: str
    url: Optional[str] = None
    package_name: Optional[str] = None
    app_code: Optional[str] = None
    description: Optional[str] = None

class ContactTypeResponse(BaseModel):
    id: int
    name: str
    url_pattern: Optional[str] = None
    description: Optional[str] = None

class ContactTypeCreate(BaseModel):
    name: str
    url_pattern: Optional[str] = None
    description: Optional[str] = None

class ClientResponse(BaseModel):
    id: int
    line_id: Optional[str] = None
    name: str
    expires_date: Optional[date] = None
    login: Optional[str] = None
    password: Optional[str] = None
    mac: Optional[str] = None
    key_value: Optional[str] = None
    contact_value: Optional[str] = None
    telegram_id: Optional[int] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    # Relationships
    panel_name: Optional[str] = None
    app_name: Optional[str] = None
    contact_type_name: Optional[str] = None
    days_left: Optional[int] = None

class ClientCreate(BaseModel):
    line_id: Optional[str] = None
    name: str
    subscription_period: int  # days
    panel_id: Optional[int] = None
    login: Optional[str] = None
    password: Optional[str] = None
    app_id: Optional[int] = None
    mac: Optional[str] = None
    key_value: Optional[str] = None
    contact_type_id: Optional[int] = None
    contact_value: Optional[str] = None
    telegram_id: Optional[int] = None
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    line_id: Optional[str] = None
    name: Optional[str] = None
    expires_date: Optional[date] = None
    panel_id: Optional[int] = None
    login: Optional[str] = None
    password: Optional[str] = None
    app_id: Optional[int] = None
    mac: Optional[str] = None
    key_value: Optional[str] = None
    contact_type_id: Optional[int] = None
    contact_value: Optional[str] = None
    telegram_id: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class PaymentMethodResponse(BaseModel):
    id: int
    method_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    fee_percentage: float
    instructions: Optional[str] = None
    icon: Optional[str] = None

class PaymentMethodCreate(BaseModel):
    method_id: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    fee_percentage: float = 0.0
    min_amount: float = 0.0
    max_amount: Optional[float] = None
    instructions: Optional[str] = None
    icon: Optional[str] = None

class PricingConfigResponse(BaseModel):
    id: int
    service_type: str
    price: float
    currency: str
    duration_days: int
    is_active: bool
    discount_percentage: float
    description: Optional[str] = None

class PricingConfigCreate(BaseModel):
    service_type: str
    price: float
    currency: str = 'PLN'
    duration_days: int
    is_active: bool = True
    discount_percentage: float = 0.0
    description: Optional[str] = None
    features: Optional[str] = None

class QuestionCreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None
    is_active: bool = True

class QuestionResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: Optional[str] = None
    is_active: bool

class SmartTVAppResponse(BaseModel):
    id: int
    name: str
    platform: Optional[str] = None
    download_url: Optional[str] = None
    instructions: Optional[str] = None
    version: Optional[str] = None
    is_active: bool
    icon: Optional[str] = None
    requirements: Optional[str] = None

class SmartTVAppCreate(BaseModel):
    name: str
    platform: Optional[str] = None
    download_url: Optional[str] = None
    instructions: Optional[str] = None
    version: Optional[str] = None
    is_active: bool = True
    icon: Optional[str] = None
    requirements: Optional[str] = None

class SmartTVActivationResponse(BaseModel):
    id: int
    app_name: str
    activation_price: float
    currency: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class SmartTVActivationCreate(BaseModel):
    app_name: str
    activation_price: float
    currency: str = 'PLN'
    description: Optional[str] = None
    is_active: bool = True

class AndroidAppResponse(BaseModel):
    id: int
    name: str
    package_name: Optional[str] = None
    download_url: Optional[str] = None
    play_store_url: Optional[str] = None
    instructions: Optional[str] = None
    version: Optional[str] = None
    is_active: bool
    icon: Optional[str] = None
    minimum_android_version: Optional[str] = None
    file_size: Optional[str] = None

class AndroidAppCreate(BaseModel):
    name: str
    package_name: Optional[str] = None
    download_url: Optional[str] = None
    play_store_url: Optional[str] = None
    instructions: Optional[str] = None
    version: Optional[str] = None
    is_active: bool = True
    icon: Optional[str] = None
    minimum_android_version: Optional[str] = None
    file_size: Optional[str] = None

# ============ AUTH FUNCTIONS ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    admin_id = payload.get("admin_id")
    if admin_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    
    return admin

# ============ HELPER FUNCTIONS ============

def calculate_days_left(expires_date: date) -> int:
    today = date.today()
    delta = expires_date - today
    return delta.days

def enrich_client_response(client: Client, db: Session) -> ClientResponse:
    """Enrich client data with related information"""
    
    # Calculate days left and status
    days_left = None
    if client.expires_date:
        days_left = calculate_days_left(client.expires_date)
    
    # Get related data
    panel_name = None
    if client.panel_id:
        panel = db.query(Panel).filter(Panel.id == client.panel_id).first()
        panel_name = panel.name if panel else None
    
    app_name = None
    if client.app_id:
        app = db.query(App).filter(App.id == client.app_id).first()
        app_name = app.name if app else None
    
    contact_type_name = None
    if client.contact_type_id:
        contact_type = db.query(ContactType).filter(ContactType.id == client.contact_type_id).first()
        contact_type_name = contact_type.name if contact_type else None
    
    return ClientResponse(
        id=client.id,
        line_id=client.line_id,
        name=client.name,
        expires_date=client.expires_date,
        login=client.login,
        password=client.password,
        mac=client.mac,
        key_value=client.key_value,
        contact_value=client.contact_value,
        telegram_id=client.telegram_id,
        notes=client.notes,
        status=client.status,
        created_at=client.created_at,
        panel_name=panel_name,
        app_name=app_name,
        contact_type_name=contact_type_name,
        days_left=days_left
    )

# ============ API ENDPOINTS ============

# Authentication
@api_router.post("/auth/login")
async def login(admin_data: dict, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.login == admin_data["username"]).first()
    if not admin or not verify_password(admin_data["password"], admin.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    token_data = {"admin_id": admin.id, "username": admin.login}
    token = create_jwt_token(token_data)
    
    return {
        "access_token": token, 
        "token_type": "bearer", 
        "admin": {"id": admin.id, "username": admin.login, "email": admin.email}
    }

@api_router.post("/auth/register")
async def register(admin_data: dict, db: Session = Depends(get_db)):
    # Check if admin already exists
    existing_admin = db.query(Admin).filter(Admin.login == admin_data["username"]).first()
    if existing_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists")
    
    # Create new admin
    admin = Admin(
        login=admin_data["username"],
        password=hash_password(admin_data["password"]),
        email=admin_data.get("email")
    )
    
    db.add(admin)
    db.commit()
    return {"message": "Admin created successfully"}

# Clients
@api_router.get("/clients", response_model=List[ClientResponse])
async def get_clients(
    search: Optional[str] = None,
    expiry_filter: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Client)
    
    # Search filter
    if search:
        query = query.filter(
            (Client.name.contains(search)) |
            (Client.login.contains(search)) |
            (Client.mac.contains(search)) |
            (Client.line_id.contains(search)) |
            (Client.contact_value.contains(search))
        )
    
    # Expiry filter
    if expiry_filter:
        today = date.today()
        if expiry_filter == "expired":
            query = query.filter(Client.expires_date < today)
        elif expiry_filter == "expiring_soon":
            week_from_now = today + timedelta(days=7)
            query = query.filter(Client.expires_date.between(today, week_from_now))
        elif expiry_filter == "active":
            query = query.filter(Client.expires_date >= today)
    
    # Sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Client, sort_by).desc())
    else:
        query = query.order_by(getattr(Client, sort_by))
    
    # Pagination
    offset = (page - 1) * limit
    clients = query.offset(offset).limit(limit).all()
    
    # Enrich client data
    enriched_clients = [enrich_client_response(client, db) for client in clients]
    
    return enriched_clients

@api_router.post("/clients", response_model=ClientResponse)
async def create_client(client_data: ClientCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Calculate expiry date
    expires_date = date.today() + timedelta(days=client_data.subscription_period)
    
    client = Client(
        line_id=client_data.line_id,
        name=client_data.name,
        expires_date=expires_date,
        panel_id=client_data.panel_id,
        login=client_data.login,
        password=client_data.password,
        app_id=client_data.app_id,
        mac=client_data.mac,
        key_value=client_data.key_value,
        contact_type_id=client_data.contact_type_id,
        contact_value=client_data.contact_value,
        telegram_id=client_data.telegram_id,
        notes=client_data.notes,
        created_by=current_admin.id
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return enrich_client_response(client, db)

@api_router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return enrich_client_response(client, db)

@api_router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: int, client_data: ClientUpdate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update fields
    update_data = client_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    
    client.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(client)
    
    return enrich_client_response(client, db)

@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: int, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    
    return {"message": "Client deleted successfully"}

# Panels
@api_router.get("/panels", response_model=List[PanelResponse])
async def get_panels(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    panels = db.query(Panel).all()
    return panels

@api_router.post("/panels", response_model=PanelResponse)
async def create_panel(panel_data: PanelCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    panel = Panel(**panel_data.dict(), created_by=current_admin.id)
    db.add(panel)
    db.commit()
    db.refresh(panel)
    return panel

@api_router.put("/panels/{panel_id}", response_model=PanelResponse)
async def update_panel(panel_id: int, panel_data: PanelCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    panel = db.query(Panel).filter(Panel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    for key, value in panel_data.dict().items():
        setattr(panel, key, value)
    
    panel.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(panel)
    return panel

@api_router.delete("/panels/{panel_id}")
async def delete_panel(panel_id: int, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    panel = db.query(Panel).filter(Panel.id == panel_id).first()
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    db.delete(panel)
    db.commit()
    return {"message": "Panel deleted successfully"}

# Apps
@api_router.get("/apps", response_model=List[AppResponse])
async def get_apps(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    apps = db.query(App).all()
    return apps

@api_router.post("/apps", response_model=AppResponse)
async def create_app(app_data: AppCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    app = App(**app_data.dict(), created_by=current_admin.id)
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@api_router.put("/apps/{app_id}", response_model=AppResponse)
async def update_app(app_id: int, app_data: AppCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    for key, value in app_data.dict().items():
        setattr(app, key, value)
    
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app

@api_router.delete("/apps/{app_id}")
async def delete_app(app_id: int, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    db.delete(app)
    db.commit()
    return {"message": "App deleted successfully"}

# Contact Types
@api_router.get("/contact-types", response_model=List[ContactTypeResponse])
async def get_contact_types(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    contact_types = db.query(ContactType).all()
    return contact_types

@api_router.post("/contact-types", response_model=ContactTypeResponse)
async def create_contact_type(contact_type_data: ContactTypeCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    contact_type = ContactType(**contact_type_data.dict(), created_by=current_admin.id)
    db.add(contact_type)
    db.commit()
    db.refresh(contact_type)
    return contact_type

@api_router.put("/contact-types/{contact_type_id}", response_model=ContactTypeResponse)
async def update_contact_type(contact_type_id: int, contact_type_data: ContactTypeCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    contact_type = db.query(ContactType).filter(ContactType.id == contact_type_id).first()
    if not contact_type:
        raise HTTPException(status_code=404, detail="Contact type not found")
    
    for key, value in contact_type_data.dict().items():
        setattr(contact_type, key, value)
    
    contact_type.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contact_type)
    return contact_type

@api_router.delete("/contact-types/{contact_type_id}")
async def delete_contact_type(contact_type_id: int, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    contact_type = db.query(ContactType).filter(ContactType.id == contact_type_id).first()
    if not contact_type:
        raise HTTPException(status_code=404, detail="Contact type not found")
    
    db.delete(contact_type)
    db.commit()
    return {"message": "Contact type deleted successfully"}

# Payment Methods
@api_router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    payment_methods = db.query(PaymentMethod).all()
    return payment_methods

@api_router.post("/payment-methods", response_model=PaymentMethodResponse)
async def create_payment_method(payment_method_data: PaymentMethodCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    payment_method = PaymentMethod(**payment_method_data.dict())
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    return payment_method

@api_router.put("/payment-methods/{method_id}")
async def update_payment_method(method_id: int, payment_method_data: PaymentMethodCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    for key, value in payment_method_data.dict().items():
        setattr(payment_method, key, value)
    
    payment_method.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(payment_method)
    return payment_method

@api_router.delete("/payment-methods/{method_id}")
async def delete_payment_method(method_id: int, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    db.delete(payment_method)
    db.commit()
    return {"message": "Payment method deleted successfully"}

# Pricing Config
@api_router.get("/pricing-config", response_model=List[PricingConfigResponse])
async def get_pricing_config(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    pricing_config = db.query(PricingConfig).all()
    return pricing_config

@api_router.post("/pricing-config", response_model=PricingConfigResponse)
async def create_pricing_config(pricing_data: PricingConfigCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    pricing = PricingConfig(**pricing_data.dict())
    db.add(pricing)
    db.commit()
    db.refresh(pricing)
    return pricing

@api_router.put("/pricing-config/{pricing_id}")
async def update_pricing_config(pricing_id: int, pricing_data: PricingConfigCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    pricing = db.query(PricingConfig).filter(PricingConfig.id == pricing_id).first()
    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing config not found")
    
    for key, value in pricing_data.dict().items():
        setattr(pricing, key, value)
    
    pricing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(pricing)
    return pricing

# Questions/FAQ
@api_router.get("/questions", response_model=List[QuestionResponse])
async def get_questions(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    questions = db.query(Question).all()
    return questions

@api_router.post("/questions", response_model=QuestionResponse)
async def create_question(question_data: QuestionCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    question = Question(**question_data.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@api_router.put("/questions/{question_id}")
async def update_question(question_id: int, question_data: QuestionCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    for key, value in question_data.dict().items():
        setattr(question, key, value)
    
    question.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(question)
    return question

# Smart TV Activations
@api_router.get("/smart-tv-activations", response_model=List[SmartTVActivationResponse])
async def get_smart_tv_activations(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    activations = db.query(SmartTVActivation).all()
    return activations

@api_router.post("/smart-tv-activations", response_model=SmartTVActivationResponse)
async def create_smart_tv_activation(activation_data: SmartTVActivationCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    activation = SmartTVActivation(**activation_data.dict())
    db.add(activation)
    db.commit()
    db.refresh(activation)
    return activation

@api_router.put("/smart-tv-activations/{activation_id}")
async def update_smart_tv_activation(activation_id: int, activation_data: SmartTVActivationCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    activation = db.query(SmartTVActivation).filter(SmartTVActivation.id == activation_id).first()
    if not activation:
        raise HTTPException(status_code=404, detail="Smart TV activation not found")
    
    for key, value in activation_data.dict().items():
        setattr(activation, key, value)
    
    activation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(activation)
    return activation

@api_router.delete("/smart-tv-activations/{activation_id}")
async def delete_smart_tv_activation(activation_id: int, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    activation = db.query(SmartTVActivation).filter(SmartTVActivation.id == activation_id).first()
    if not activation:
        raise HTTPException(status_code=404, detail="Smart TV activation not found")
    
    db.delete(activation)
    db.commit()
    return {"message": "Smart TV activation deleted successfully"}

# Smart TV Apps
@api_router.get("/smart-tv-apps", response_model=List[SmartTVAppResponse])
async def get_smart_tv_apps(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    apps = db.query(SmartTVApp).all()
    return apps

@api_router.post("/smart-tv-apps", response_model=SmartTVAppResponse)
async def create_smart_tv_app(app_data: SmartTVAppCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    app = SmartTVApp(**app_data.dict())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@api_router.put("/smart-tv-apps/{app_id}")
async def update_smart_tv_app(app_id: int, app_data: SmartTVAppCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    app = db.query(SmartTVApp).filter(SmartTVApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Smart TV app not found")
    
    for key, value in app_data.dict().items():
        setattr(app, key, value)
    
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app

# Android Apps
@api_router.get("/android-apps", response_model=List[AndroidAppResponse])
async def get_android_apps(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    apps = db.query(AndroidApp).all()
    return apps

@api_router.post("/android-apps", response_model=AndroidAppResponse)
async def create_android_app(app_data: AndroidAppCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    app = AndroidApp(**app_data.dict())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@api_router.put("/android-apps/{app_id}")
async def update_android_app(app_id: int, app_data: AndroidAppCreate, current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    app = db.query(AndroidApp).filter(AndroidApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Android app not found")
    
    for key, value in app_data.dict().items():
        setattr(app, key, value)
    
    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app

# Dashboard Stats
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    today = date.today()
    
    total_clients = db.query(Client).count()
    active_clients = db.query(Client).filter(Client.expires_date >= today).count()
    expired_clients = db.query(Client).filter(Client.expires_date < today).count()
    
    week_from_now = today + timedelta(days=7)
    expiring_soon = db.query(Client).filter(
        Client.expires_date.between(today, week_from_now)
    ).count()
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "expired_clients": expired_clients,
        "expiring_soon": expiring_soon,
    }

# JSON Import/Export
@api_router.post("/import-json/{table_name}")
async def import_json_data(
    table_name: str,
    file: UploadFile = File(...),
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Import JSON data into specified table"""
    
    try:
        content = await file.read()
        json_data = json.loads(content)
        
        # Import based on table name
        imported_count = 0
        
        if table_name == "payment_methods":
            for item in json_data:
                payment_method = PaymentMethod(**item)
                db.add(payment_method)
                imported_count += 1
        
        elif table_name == "pricing_config":
            for item in json_data:
                pricing = PricingConfig(**item)
                db.add(pricing)
                imported_count += 1
        
        elif table_name == "questions":
            for item in json_data:
                question = Question(**item)
                db.add(question)
                imported_count += 1
        
        elif table_name == "smart_tv_apps":
            for item in json_data:
                app = SmartTVApp(**item)
                db.add(app)
                imported_count += 1
        
        elif table_name == "android_apps":
            for item in json_data:
                app = AndroidApp(**item)
                db.add(app)
                imported_count += 1
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported table name")
        
        db.commit()
        
        return {"message": f"Successfully imported {imported_count} records into {table_name}"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@api_router.get("/export-csv/{table_name}")
async def export_csv_data(
    table_name: str,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Export table data to CSV"""
    
    try:
        # Query data based on table name
        if table_name == "clients":
            data = db.query(Client).all()
        elif table_name == "panels":
            data = db.query(Panel).all()
        elif table_name == "apps":
            data = db.query(App).all()
        else:
            raise HTTPException(status_code=400, detail="Unsupported table name")
        
        # Create CSV
        output = io.StringIO()
        if data:
            # Get column names from first record
            columns = [column.name for column in data[0].__table__.columns]
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            
            for row in data:
                row_dict = {column: getattr(row, column, '') for column in columns}
                writer.writerow(row_dict)
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={table_name}_export.csv"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Export failed: {str(e)}")

# Password Generator
@api_router.get("/generate-password")
async def generate_password(length: int = 8):
    import random
    import string
    
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return {"password": password}

# Include router
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "TV Panel SQL API is running", "version": "2.0.0", "database": "MySQL/MariaDB"}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)