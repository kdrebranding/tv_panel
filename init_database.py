#!/usr/bin/env python3
"""
TV Panel Database Initialization Script
Creates initial data and sample records for the TV Panel system.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date, timedelta
import bcrypt
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def init_database():
    """Initialize the database with sample data"""
    
    print("🚀 Inicjalizacja bazy danych TV Panel...")
    
    # Clear existing data (optional - uncomment if you want to reset)
    # await db.admins.delete_many({})
    # await db.panels.delete_many({})
    # await db.apps.delete_many({})
    # await db.contact_types.delete_many({})
    # await db.clients.delete_many({})
    # await db.settings.delete_many({})
    
    # 1. Create admin user
    print("👤 Tworzenie administratora...")
    admin_exists = await db.admins.find_one({"username": "admin"})
    if not admin_exists:
        admin = {
            "id": "admin-1",
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "created_at": datetime.utcnow()
        }
        await db.admins.insert_one(admin)
        print("   ✅ Administrator utworzony (login: admin, hasło: admin123)")
    else:
        print("   ⚠️ Administrator już istnieje")
    
    # 2. Create IPTV Panels
    print("📺 Tworzenie paneli IPTV...")
    panels = [
        {
            "id": "panel-1",
            "name": "Smart IPTV Panel",
            "url": "http://smartiptv.example.com",
            "description": "Panel główny Smart IPTV",
            "created_at": datetime.utcnow()
        },
        {
            "id": "panel-2", 
            "name": "TiviMate Premium",
            "url": "http://tivimate.example.com",
            "description": "Panel TiviMate Premium",
            "created_at": datetime.utcnow()
        },
        {
            "id": "panel-3",
            "name": "Perfect Player",
            "url": "http://perfectplayer.example.com", 
            "description": "Panel Perfect Player",
            "created_at": datetime.utcnow()
        }
    ]
    
    for panel in panels:
        exists = await db.panels.find_one({"id": panel["id"]})
        if not exists:
            await db.panels.insert_one(panel)
            print(f"   ✅ Panel: {panel['name']}")
    
    # 3. Create IPTV Apps
    print("📱 Tworzenie aplikacji IPTV...")
    apps = [
        {
            "id": "app-1",
            "name": "Smart IPTV",
            "description": "Aplikacja Smart IPTV dla Smart TV",
            "created_at": datetime.utcnow()
        },
        {
            "id": "app-2",
            "name": "TiviMate",
            "description": "Zaawansowany odtwarzacz IPTV",
            "created_at": datetime.utcnow()
        },
        {
            "id": "app-3", 
            "name": "Perfect Player IPTV",
            "description": "Perfect Player dla Android",
            "created_at": datetime.utcnow()
        },
        {
            "id": "app-4",
            "name": "VLC Media Player",
            "description": "VLC z obsługą IPTV",
            "created_at": datetime.utcnow()
        },
        {
            "id": "app-5",
            "name": "Kodi",
            "description": "Kodi z dodatkami IPTV",
            "created_at": datetime.utcnow()
        }
    ]
    
    for app in apps:
        exists = await db.apps.find_one({"id": app["id"]})
        if not exists:
            await db.apps.insert_one(app)
            print(f"   ✅ Aplikacja: {app['name']}")
    
    # 4. Create Contact Types
    print("📞 Tworzenie typów kontaktów...")
    contact_types = [
        {
            "id": "contact-1",
            "name": "WhatsApp",
            "url_pattern": "https://wa.me/{contact}",
            "icon": "📱",
            "created_at": datetime.utcnow()
        },
        {
            "id": "contact-2",
            "name": "Telegram",
            "url_pattern": "https://t.me/{contact}",
            "icon": "✈️",
            "created_at": datetime.utcnow()
        },
        {
            "id": "contact-3",
            "name": "Email",
            "url_pattern": "mailto:{contact}",
            "icon": "📧",
            "created_at": datetime.utcnow()
        },
        {
            "id": "contact-4",
            "name": "Telefon",
            "url_pattern": "tel:{contact}",
            "icon": "📞",
            "created_at": datetime.utcnow()
        }
    ]
    
    for contact_type in contact_types:
        exists = await db.contact_types.find_one({"id": contact_type["id"]})
        if not exists:
            await db.contact_types.insert_one(contact_type)
            print(f"   ✅ Typ kontaktu: {contact_type['name']}")
    
    # 5. Create Sample Clients
    print("👥 Tworzenie przykładowych klientów...")
    today = date.today()
    
    sample_clients = [
        {
            "id": "client-1",
            "name": "Jan Kowalski",
            "expires_date": datetime.combine(today + timedelta(days=45), datetime.min.time()),
            "panel_id": "panel-1",
            "login": "jankowalski",
            "password": "pass123",
            "app_id": "app-1",
            "mac": "00:1A:2B:3C:4D:5E",
            "key_value": "KEY-SMART-12345",
            "contact_type_id": "contact-1",
            "contact_value": "48123456789",
            "telegram_id": 123456789,
            "notes": "Klient premium, płaci regularnie",
            "line_id": "LINE001",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "client-2", 
            "name": "Anna Nowak",
            "expires_date": today + timedelta(days=5),
            "panel_id": "panel-2",
            "login": "annanowak",
            "password": "secure456",
            "app_id": "app-2",
            "mac": "00:2B:3C:4D:5E:6F",
            "key_value": "KEY-TIVI-67890",
            "contact_type_id": "contact-2",
            "contact_value": "annanowak",
            "telegram_id": 987654321,
            "notes": "Kończy się subskrypcja",
            "line_id": "LINE002", 
            "status": "expiring_soon",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "client-3",
            "name": "Piotr Wiśniewski", 
            "expires_date": today - timedelta(days=3),
            "panel_id": "panel-1",
            "login": "piotrw",
            "password": "oldpass789",
            "app_id": "app-3",
            "mac": "00:3C:4D:5E:6F:7A",
            "key_value": "KEY-PERFECT-11111",
            "contact_type_id": "contact-1",
            "contact_value": "48987654321",
            "notes": "Subskrypcja wygasła - do kontaktu",
            "line_id": "LINE003",
            "status": "expired",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "client-4",
            "name": "Mariusz Kowalczyk",
            "expires_date": today + timedelta(days=90),
            "panel_id": "panel-2",
            "login": "mariuszk",
            "password": "newpass321", 
            "app_id": "app-4",
            "mac": "00:4D:5E:6F:7A:8B",
            "key_value": "KEY-VLC-22222",
            "contact_type_id": "contact-3",
            "contact_value": "mariusz@example.com",
            "notes": "Nowy klient, 3 miesięczna subskrypcja",
            "line_id": "LINE004",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "client-5",
            "name": "Katarzyna Zielińska",
            "expires_date": today + timedelta(days=15),
            "panel_id": "panel-3",
            "login": "kzielinska", 
            "password": "kasia2024",
            "app_id": "app-5",
            "mac": "00:5E:6F:7A:8B:9C",
            "key_value": "KEY-KODI-33333",
            "contact_type_id": "contact-4",
            "contact_value": "48111222333",
            "notes": "Używa Kodi z dodatkami",
            "line_id": "LINE005",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    for client in sample_clients:
        exists = await db.clients.find_one({"id": client["id"]})
        if not exists:
            await db.clients.insert_one(client)
            print(f"   ✅ Klient: {client['name']} ({client['status']})")
    
    # 6. Create Settings
    print("⚙️ Tworzenie ustawień systemowych...")
    settings = {
        "default_expiry_days": 30,
        "default_panel_id": "panel-1",
        "default_app_id": "app-1",
        "telegram_bot_token": "",
        "reminder_hour": 10,
        "reminder_minute": 0,
        "company_name": "TV Panel Pro",
        "contact_email": "admin@tvpanel.com",
        "auto_renewal": False,
        "notification_days": [7, 3, 1]  # Notify 7, 3, and 1 days before expiry
    }
    
    await db.settings.replace_one({}, settings, upsert=True)
    print("   ✅ Ustawienia systemowe zapisane")
    
    # 7. Create indexes for better performance
    print("🔍 Tworzenie indeksów bazodanowych...")
    await db.clients.create_index("expires_date")
    await db.clients.create_index("status")
    await db.clients.create_index("panel_id")
    await db.clients.create_index("app_id")
    await db.clients.create_index([("name", "text"), ("login", "text"), ("mac", "text")])
    print("   ✅ Indeksy utworzone")
    
    print("\n🎉 Inicjalizacja zakończona pomyślnie!")
    print("\n📋 Podsumowanie:")
    
    # Count records
    admin_count = await db.admins.count_documents({})
    panel_count = await db.panels.count_documents({})
    app_count = await db.apps.count_documents({})
    contact_type_count = await db.contact_types.count_documents({})
    client_count = await db.clients.count_documents({})
    
    print(f"   👤 Administratorzy: {admin_count}")
    print(f"   📺 Panele IPTV: {panel_count}")
    print(f"   📱 Aplikacje: {app_count}")
    print(f"   📞 Typy kontaktów: {contact_type_count}")
    print(f"   👥 Klienci: {client_count}")
    
    print("\n🚀 System gotowy do użycia!")
    print("   🌐 Frontend: http://localhost:3000")
    print("   🔧 Backend API: http://localhost:8001")
    print("   👤 Login: admin")
    print("   🔑 Hasło: admin123")

if __name__ == "__main__":
    asyncio.run(init_database())