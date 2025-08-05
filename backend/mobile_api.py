"""
TV Panel Mobile API
Dedykowane API dla aplikacji mobilnej z uproszczonymi endpointami i responsywnymi danymi.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import os
import jwt
import logging
from enum import Enum

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Mobile API Router
mobile_router = APIRouter(prefix="/api/mobile/v1", tags=["Mobile API"])

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "tv-panel-secret-key-2024")
ALGORITHM = "HS256"
security = HTTPBearer()

# ============ MOBILE MODELS ============

class MobileLoginRequest(BaseModel):
    username: str
    password: str
    device_id: Optional[str] = None
    device_name: Optional[str] = None

class MobileAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user_info: Dict[str, Any]

class ClientStatus(str, Enum):
    active = "active"
    expiring_soon = "expiring_soon"
    expired = "expired"
    suspended = "suspended"

class MobileClient(BaseModel):
    id: str
    name: str
    status: ClientStatus
    days_left: Optional[int]
    expires_date: date
    panel_name: Optional[str] = None
    app_name: Optional[str] = None
    contact_value: Optional[str] = None
    created_at: datetime
    last_updated: datetime

class MobileClientDetail(MobileClient):
    login: Optional[str] = None
    password: Optional[str] = None
    mac: Optional[str] = None
    key_value: Optional[str] = None
    telegram_id: Optional[int] = None
    notes: Optional[str] = None
    line_id: Optional[str] = None

class MobileDashboard(BaseModel):
    total_clients: int
    active_clients: int
    expiring_soon: int
    expired_clients: int
    today_expirations: int
    weekly_stats: Dict[str, int]
    recent_clients: List[MobileClient]
    urgent_notifications: List[Dict[str, Any]]

class MobileNotification(BaseModel):
    id: str
    type: str  # "expiry_warning", "new_client", "system_alert"
    title: str
    message: str
    priority: str  # "high", "medium", "low"
    created_at: datetime
    read: bool = False
    action_url: Optional[str] = None

class QuickActionRequest(BaseModel):
    action: str  # "extend_license", "send_reminder", "suspend_client"
    client_id: str
    parameters: Optional[Dict[str, Any]] = None

class MobileStats(BaseModel):
    period: str
    revenue: float
    new_clients: int
    churned_clients: int
    growth_rate: float

class ClientFilter(BaseModel):
    status: Optional[ClientStatus] = None
    panel_id: Optional[str] = None
    app_id: Optional[str] = None
    expires_in_days: Optional[int] = None
    search_term: Optional[str] = None

# ============ AUTH FUNCTIONS ============

async def get_current_mobile_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current mobile user from JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("admin_id")
        if admin_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        admin = await db.admins.find_one({"id": admin_id})
        if admin is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return admin
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def create_mobile_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token for mobile app"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days for mobile
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def enrich_mobile_client(client: dict) -> dict:
    """Enrich client data for mobile display"""
    # Calculate days left
    if client.get('expires_date'):
        today = date.today()
        if isinstance(client['expires_date'], datetime):
            expires_date = client['expires_date'].date()
        else:
            expires_date = client['expires_date']
        
        days_left = (expires_date - today).days
        client['days_left'] = days_left
        
        # Update status based on expiry
        if days_left < 0:
            client['status'] = ClientStatus.expired
        elif days_left <= 7:
            client['status'] = ClientStatus.expiring_soon
        else:
            client['status'] = ClientStatus.active
    
    # Get related data
    if client.get('panel_id'):
        panel = await db.panels.find_one({"id": client['panel_id']})
        if panel:
            client['panel_name'] = panel['name']
    
    if client.get('app_id'):
        app = await db.apps.find_one({"id": client['app_id']})
        if app:
            client['app_name'] = app['name']
    
    client['last_updated'] = client.get('updated_at', client.get('created_at'))
    
    return client

# ============ MOBILE API ENDPOINTS ============

@mobile_router.post("/auth/login", response_model=MobileAuthResponse)
async def mobile_login(login_request: MobileLoginRequest):
    """Mobile app login with device registration"""
    
    # Verify credentials
    from server import verify_password
    admin = await db.admins.find_one({"username": login_request.username})
    if not admin or not verify_password(login_request.password, admin["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Create tokens
    token_data = {"admin_id": admin["id"], "username": admin["username"]}
    access_token = create_mobile_jwt_token(token_data, timedelta(days=7))
    refresh_token = create_mobile_jwt_token({"admin_id": admin["id"], "type": "refresh"}, timedelta(days=30))
    
    # Register/update device if provided
    if login_request.device_id:
        device_info = {
            "device_id": login_request.device_id,
            "device_name": login_request.device_name or "Mobile App",
            "last_login": datetime.utcnow(),
            "admin_id": admin["id"]
        }
        await db.mobile_devices.replace_one(
            {"device_id": login_request.device_id},
            device_info,
            upsert=True
        )
    
    return MobileAuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=7 * 24 * 60 * 60,  # 7 days in seconds
        user_info={
            "id": admin["id"],
            "username": admin["username"],
            "last_login": datetime.utcnow().isoformat()
        }
    )

@mobile_router.get("/dashboard", response_model=MobileDashboard)
async def get_mobile_dashboard(current_user = Depends(get_current_mobile_user)):
    """Get mobile dashboard with key metrics"""
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Basic counts
    total_clients = await db.clients.count_documents({})
    active_clients = await db.clients.count_documents({"status": "active"})
    expiring_soon = await db.clients.count_documents({"status": "expiring_soon"})
    expired_clients = await db.clients.count_documents({"status": "expired"})
    
    # Today's expirations
    today_expirations = await db.clients.count_documents({
        "expires_date": {
            "$gte": datetime.combine(today, datetime.min.time()),
            "$lt": datetime.combine(tomorrow, datetime.min.time())
        }
    })
    
    # Weekly stats
    weekly_new = await db.clients.count_documents({
        "created_at": {"$gte": datetime.combine(week_ago, datetime.min.time())}
    })
    
    weekly_expired = await db.clients.count_documents({
        "expires_date": {
            "$gte": datetime.combine(week_ago, datetime.min.time()),
            "$lt": datetime.combine(today, datetime.max.time())
        }
    })
    
    weekly_stats = {
        "new_clients": weekly_new,
        "expired_clients": weekly_expired,
        "net_growth": weekly_new - weekly_expired
    }
    
    # Recent clients (last 5)
    recent_clients_data = await db.clients.find().sort("created_at", -1).limit(5).to_list(5)
    recent_clients = []
    
    for client in recent_clients_data:
        enriched = await enrich_mobile_client(client)
        recent_clients.append(MobileClient(**enriched))
    
    # Urgent notifications
    urgent_notifications = []
    
    # Clients expiring today
    if today_expirations > 0:
        urgent_notifications.append({
            "type": "expiry_alert",
            "title": "Licencje wygasają dzisiaj!",
            "message": f"{today_expirations} klientów ma wygasające licencje",
            "priority": "high",
            "action_url": "/clients?filter=expiring_today"
        })
    
    # High number of expired clients
    if expired_clients > 10:
        urgent_notifications.append({
            "type": "expired_alert",
            "title": "Dużo wygasłych licencji",
            "message": f"{expired_clients} klientów ma wygasłe licencje",
            "priority": "medium",
            "action_url": "/clients?filter=expired"
        })
    
    return MobileDashboard(
        total_clients=total_clients,
        active_clients=active_clients,
        expiring_soon=expiring_soon,
        expired_clients=expired_clients,
        today_expirations=today_expirations,
        weekly_stats=weekly_stats,
        recent_clients=recent_clients,
        urgent_notifications=urgent_notifications
    )

@mobile_router.get("/clients", response_model=List[MobileClient])
async def get_mobile_clients(
    status: Optional[ClientStatus] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    search: Optional[str] = Query(None),
    current_user = Depends(get_current_mobile_user)
):
    """Get clients list optimized for mobile"""
    
    # Build query
    query = {}
    
    if status:
        if status == ClientStatus.expiring_soon:
            # Clients expiring in next 7 days
            today = datetime.now().date()
            week_from_now = today + timedelta(days=7)
            query["expires_date"] = {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lte": datetime.combine(week_from_now, datetime.max.time())
            }
        elif status == ClientStatus.expired:
            # Expired clients
            today = datetime.now().date()
            query["expires_date"] = {"$lt": datetime.combine(today, datetime.min.time())}
        else:
            query["status"] = status.value
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"login": {"$regex": search, "$options": "i"}},
            {"contact_value": {"$regex": search, "$options": "i"}},
            {"mac": {"$regex": search, "$options": "i"}}
        ]
    
    # Get clients
    clients_data = await db.clients.find(query).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    clients = []
    for client in clients_data:
        enriched = await enrich_mobile_client(client)
        clients.append(MobileClient(**enriched))
    
    return clients

@mobile_router.get("/clients/{client_id}", response_model=MobileClientDetail)
async def get_mobile_client_detail(client_id: str, current_user = Depends(get_current_mobile_user)):
    """Get detailed client information"""
    
    client = await db.clients.find_one({"id": client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    enriched = await enrich_mobile_client(client)
    return MobileClientDetail(**enriched)

@mobile_router.post("/clients/{client_id}/quick-action")
async def perform_quick_action(
    client_id: str, 
    action_request: QuickActionRequest,
    current_user = Depends(get_current_mobile_user)
):
    """Perform quick actions on client"""
    
    client = await db.clients.find_one({"id": client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    action = action_request.action
    parameters = action_request.parameters or {}
    
    if action == "extend_license":
        # Extend license by specified days (default 30)
        days = parameters.get("days", 30)
        current_expiry = client.get('expires_date')
        
        if isinstance(current_expiry, datetime):
            current_expiry = current_expiry.date()
        
        if current_expiry and current_expiry > date.today():
            new_expiry = current_expiry + timedelta(days=days)
        else:
            new_expiry = date.today() + timedelta(days=days)
        
        await db.clients.update_one(
            {"id": client_id},
            {
                "$set": {
                    "expires_date": datetime.combine(new_expiry, datetime.min.time()),
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": f"Licencja przedłużona o {days} dni", "new_expiry": new_expiry.isoformat()}
    
    elif action == "suspend_client":
        # Suspend client
        await db.clients.update_one(
            {"id": client_id},
            {
                "$set": {
                    "status": "suspended",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Klient zawieszony"}
    
    elif action == "activate_client":
        # Activate client
        await db.clients.update_one(
            {"id": client_id},
            {
                "$set": {
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Klient aktywowany"}
    
    else:
        raise HTTPException(status_code=400, detail="Unknown action")

@mobile_router.get("/stats/overview")
async def get_mobile_stats_overview(
    period: str = Query("week", regex="^(week|month|quarter)$"),
    current_user = Depends(get_current_mobile_user)
):
    """Get stats overview for different periods"""
    
    now = datetime.now()
    
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:  # quarter
        start_date = now - timedelta(days=90)
    
    # New clients in period
    new_clients = await db.clients.count_documents({
        "created_at": {"$gte": start_date}
    })
    
    # Expired clients in period
    expired_clients = await db.clients.count_documents({
        "expires_date": {
            "$gte": start_date,
            "$lte": now
        }
    })
    
    # Revenue calculation (30 PLN per active client)
    active_clients = await db.clients.count_documents({"status": "active"})
    estimated_revenue = active_clients * 30.0
    
    # Growth rate
    total_at_start = await db.clients.count_documents({
        "created_at": {"$lte": start_date}
    })
    
    growth_rate = (new_clients / total_at_start * 100) if total_at_start > 0 else 0
    
    return MobileStats(
        period=period,
        revenue=estimated_revenue,
        new_clients=new_clients,
        churned_clients=expired_clients,
        growth_rate=round(growth_rate, 2)
    )

@mobile_router.get("/notifications", response_model=List[MobileNotification])
async def get_mobile_notifications(
    limit: int = Query(20, le=50),
    unread_only: bool = Query(False),
    current_user = Depends(get_current_mobile_user)
):
    """Get mobile notifications"""
    
    # This is a simplified version - in production, you'd store notifications in DB
    notifications = []
    
    # Generate notifications based on current system state
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # Expiring today
    expiring_today = await db.clients.count_documents({
        "expires_date": {
            "$gte": datetime.combine(today, datetime.min.time()),
            "$lt": datetime.combine(tomorrow, datetime.min.time())
        }
    })
    
    if expiring_today > 0:
        notifications.append(MobileNotification(
            id=f"expiry_today_{today.isoformat()}",
            type="expiry_warning",
            title="Licencje wygasają dzisiaj",
            message=f"{expiring_today} klientów ma wygasające dzisiaj licencje",
            priority="high",
            created_at=datetime.utcnow(),
            action_url="/clients?filter=expiring_today"
        ))
    
    # New clients this week
    week_ago = today - timedelta(days=7)
    new_this_week = await db.clients.count_documents({
        "created_at": {"$gte": datetime.combine(week_ago, datetime.min.time())}
    })
    
    if new_this_week > 0:
        notifications.append(MobileNotification(
            id=f"new_clients_{week_ago.isoformat()}",
            type="new_client",
            title="Nowi klienci w tym tygodniu",
            message=f"Dodano {new_this_week} nowych klientów",
            priority="medium",
            created_at=datetime.utcnow(),
            action_url="/clients?filter=recent"
        ))
    
    return notifications[:limit]

@mobile_router.get("/search")
async def mobile_search(
    query: str = Query(..., min_length=2),
    type: Optional[str] = Query("all", regex="^(all|clients|panels|apps)$"),
    limit: int = Query(10, le=20),
    current_user = Depends(get_current_mobile_user)
):
    """Universal search for mobile app"""
    
    results = {"clients": [], "panels": [], "apps": []}
    
    if type in ["all", "clients"]:
        # Search clients
        clients = await db.clients.find({
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"login": {"$regex": query, "$options": "i"}},
                {"contact_value": {"$regex": query, "$options": "i"}},
                {"mac": {"$regex": query, "$options": "i"}}
            ]
        }).limit(limit).to_list(limit)
        
        for client in clients:
            enriched = await enrich_mobile_client(client)
            results["clients"].append({
                "id": client["id"],
                "name": client["name"],
                "status": enriched["status"],
                "type": "client"
            })
    
    if type in ["all", "panels"]:
        # Search panels
        panels = await db.panels.find({
            "name": {"$regex": query, "$options": "i"}
        }).limit(limit).to_list(limit)
        
        for panel in panels:
            results["panels"].append({
                "id": panel["id"],
                "name": panel["name"],
                "type": "panel"
            })
    
    if type in ["all", "apps"]:
        # Search apps
        apps = await db.apps.find({
            "name": {"$regex": query, "$options": "i"}
        }).limit(limit).to_list(limit)
        
        for app in apps:
            results["apps"].append({
                "id": app["id"],
                "name": app["name"],
                "type": "app"
            })
    
    return results

@mobile_router.get("/health")
async def mobile_health_check():
    """Health check endpoint for mobile app"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "api": "mobile"
    }