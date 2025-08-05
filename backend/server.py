from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import os
import uuid
import bcrypt
import jwt
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# FastAPI app
app = FastAPI(title="TV Panel API", description="IPTV Client Management System")
api_router = APIRouter(prefix="/api")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "tv-panel-secret-key-2024")
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

# ============ MODELS ============
class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AdminCreate(BaseModel):
    username: str
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

class Panel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PanelCreate(BaseModel):
    name: str
    url: Optional[str] = None
    description: Optional[str] = None

class App(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AppCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ContactType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url_pattern: str  # e.g., "https://wa.me/{contact}"
    icon: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContactTypeCreate(BaseModel):
    name: str
    url_pattern: str
    icon: Optional[str] = None

class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    expires_date: date
    panel_id: Optional[str] = None
    panel_name: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    app_id: Optional[str] = None
    app_name: Optional[str] = None
    mac: Optional[str] = None
    key_value: Optional[str] = None
    contact_type_id: Optional[str] = None
    contact_type_name: Optional[str] = None
    contact_value: Optional[str] = None
    telegram_id: Optional[int] = None
    notes: Optional[str] = None
    line_id: Optional[str] = None
    status: str = "active"  # active, expired, suspended
    days_left: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ClientCreate(BaseModel):
    name: str
    subscription_period: int  # days
    panel_id: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    app_id: Optional[str] = None
    mac: Optional[str] = None
    key_value: Optional[str] = None
    contact_type_id: Optional[str] = None
    contact_value: Optional[str] = None
    telegram_id: Optional[int] = None
    notes: Optional[str] = None
    line_id: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    expires_date: Optional[date] = None
    panel_id: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    app_id: Optional[str] = None
    mac: Optional[str] = None
    key_value: Optional[str] = None
    contact_type_id: Optional[str] = None
    contact_value: Optional[str] = None
    telegram_id: Optional[int] = None
    notes: Optional[str] = None
    line_id: Optional[str] = None
    status: Optional[str] = None

class Settings(BaseModel):
    default_expiry_days: int = 30
    default_panel_id: Optional[str] = None
    default_app_id: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    reminder_hour: int = 10
    reminder_minute: int = 0

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
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    admin_id = payload.get("admin_id")
    if admin_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    admin = await db.admins.find_one({"id": admin_id})
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    
    return admin

# ============ HELPER FUNCTIONS ============
async def calculate_days_left(expires_date: date) -> int:
    today = date.today()
    delta = expires_date - today
    return delta.days

async def enrich_client_data(client: dict) -> dict:
    """Enrich client data with related information"""
    # Calculate days left
    if client.get('expires_date'):
        client['days_left'] = await calculate_days_left(client['expires_date'])
        
        # Update status based on expiry
        if client['days_left'] < 0:
            client['status'] = 'expired'
        elif client['days_left'] <= 7:
            client['status'] = 'expiring_soon'
        else:
            client['status'] = 'active'
    
    # Get panel name
    if client.get('panel_id'):
        panel = await db.panels.find_one({"id": client['panel_id']})
        if panel:
            client['panel_name'] = panel['name']
    
    # Get app name
    if client.get('app_id'):
        app = await db.apps.find_one({"id": client['app_id']})
        if app:
            client['app_name'] = app['name']
    
    # Get contact type name
    if client.get('contact_type_id'):
        contact_type = await db.contact_types.find_one({"id": client['contact_type_id']})
        if contact_type:
            client['contact_type_name'] = contact_type['name']
    
    return client

# ============ API ENDPOINTS ============

# Authentication
@api_router.post("/auth/login")
async def login(admin_data: AdminLogin):
    admin = await db.admins.find_one({"username": admin_data.username})
    if not admin or not verify_password(admin_data.password, admin["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token_data = {"admin_id": admin["id"], "username": admin["username"]}
    token = create_jwt_token(token_data)
    
    return {"access_token": token, "token_type": "bearer", "admin": {"id": admin["id"], "username": admin["username"]}}

@api_router.post("/auth/register")
async def register(admin_data: AdminCreate):
    # Check if admin already exists
    existing_admin = await db.admins.find_one({"username": admin_data.username})
    if existing_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists")
    
    # Create new admin
    admin = Admin(
        username=admin_data.username,
        password_hash=hash_password(admin_data.password)
    )
    
    await db.admins.insert_one(admin.dict())
    return {"message": "Admin created successfully"}

# Clients
@api_router.get("/clients", response_model=List[Client])
async def get_clients(
    search: Optional[str] = None,
    expiry_filter: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_admin = Depends(get_current_admin)
):
    query = {}
    
    # Search filter
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"login": {"$regex": search, "$options": "i"}},
            {"mac": {"$regex": search, "$options": "i"}},
            {"line_id": {"$regex": search, "$options": "i"}},
            {"contact_value": {"$regex": search, "$options": "i"}}
        ]
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get clients
    cursor = db.clients.find(query)
    
    # Sort
    sort_direction = -1 if sort_order == "desc" else 1
    cursor = cursor.sort(sort_by, sort_direction).skip(skip).limit(limit)
    
    clients = await cursor.to_list(length=limit)
    
    # Enrich client data
    enriched_clients = []
    for client in clients:
        enriched_client = await enrich_client_data(client)
        enriched_clients.append(enriched_client)
    
    # Apply expiry filter after enrichment
    if expiry_filter:
        filtered_clients = []
        for client in enriched_clients:
            if expiry_filter == "expired" and client.get('status') == 'expired':
                filtered_clients.append(client)
            elif expiry_filter == "expiring_soon" and client.get('status') == 'expiring_soon':
                filtered_clients.append(client)
            elif expiry_filter == "active" and client.get('status') == 'active':
                filtered_clients.append(client)
        enriched_clients = filtered_clients
    
    return enriched_clients

@api_router.post("/clients", response_model=Client)
async def create_client(client_data: ClientCreate, current_admin = Depends(get_current_admin)):
    # Calculate expiry date
    expires_date = date.today() + timedelta(days=client_data.subscription_period)
    
    client = Client(
        **client_data.dict(exclude={"subscription_period"}),
        expires_date=expires_date
    )
    
    await db.clients.insert_one(client.dict())
    
    # Enrich and return
    enriched_client = await enrich_client_data(client.dict())
    return enriched_client

@api_router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str, current_admin = Depends(get_current_admin)):
    client = await db.clients.find_one({"id": client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    enriched_client = await enrich_client_data(client)
    return enriched_client

@api_router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client_data: ClientUpdate, current_admin = Depends(get_current_admin)):
    # Find existing client
    existing_client = await db.clients.find_one({"id": client_id})
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update fields
    update_data = client_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await db.clients.update_one({"id": client_id}, {"$set": update_data})
    
    # Get updated client
    updated_client = await db.clients.find_one({"id": client_id})
    enriched_client = await enrich_client_data(updated_client)
    return enriched_client

@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: str, current_admin = Depends(get_current_admin)):
    result = await db.clients.delete_one({"id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return {"message": "Client deleted successfully"}

# Panels
@api_router.get("/panels", response_model=List[Panel])
async def get_panels(current_admin = Depends(get_current_admin)):
    panels = await db.panels.find().to_list(length=None)
    return panels

@api_router.post("/panels", response_model=Panel)
async def create_panel(panel_data: PanelCreate, current_admin = Depends(get_current_admin)):
    panel = Panel(**panel_data.dict())
    await db.panels.insert_one(panel.dict())
    return panel

# Apps
@api_router.get("/apps", response_model=List[App])
async def get_apps(current_admin = Depends(get_current_admin)):
    apps = await db.apps.find().to_list(length=None)
    return apps

@api_router.post("/apps", response_model=App)
async def create_app(app_data: AppCreate, current_admin = Depends(get_current_admin)):
    app = App(**app_data.dict())
    await db.apps.insert_one(app.dict())
    return app

# Contact Types
@api_router.get("/contact-types", response_model=List[ContactType])
async def get_contact_types(current_admin = Depends(get_current_admin)):
    contact_types = await db.contact_types.find().to_list(length=None)
    return contact_types

@api_router.post("/contact-types", response_model=ContactType)
async def create_contact_type(contact_type_data: ContactTypeCreate, current_admin = Depends(get_current_admin)):
    contact_type = ContactType(**contact_type_data.dict())
    await db.contact_types.insert_one(contact_type.dict())
    return contact_type

# Settings
@api_router.get("/settings")
async def get_settings(current_admin = Depends(get_current_admin)):
    settings = await db.settings.find_one({}) or {}
    return settings

@api_router.put("/settings")
async def update_settings(settings_data: dict, current_admin = Depends(get_current_admin)):
    await db.settings.replace_one({}, settings_data, upsert=True)
    return {"message": "Settings updated successfully"}

# Dashboard Stats
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_admin = Depends(get_current_admin)):
    total_clients = await db.clients.count_documents({})
    
    # Count by status
    today = date.today()
    
    active_count = await db.clients.count_documents({
        "expires_date": {"$gt": today + timedelta(days=7)}
    })
    
    expiring_soon_count = await db.clients.count_documents({
        "expires_date": {
            "$gte": today,
            "$lte": today + timedelta(days=7)
        }
    })
    
    expired_count = await db.clients.count_documents({
        "expires_date": {"$lt": today}
    })
    
    return {
        "total_clients": total_clients,
        "active_clients": active_count,
        "expiring_soon": expiring_soon_count,
        "expired_clients": expired_count,
    }

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
    return {"message": "TV Panel API is running", "version": "1.0.0"}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()