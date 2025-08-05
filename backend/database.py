"""
TV Panel SQL Database Configuration
SQLAlchemy models for MySQL database with all tables from the provided schema.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, BigInteger, Enum, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_DATABASE', 'tv_panel')}")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============ MODELS ============

class Admin(Base):
    __tablename__ = "admin"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255))
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class Panel(Base):
    __tablename__ = "panels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(Integer, ForeignKey("admin.id"))
    
    # Relationships
    clients = relationship("Client", back_populates="panel")
    creator = relationship("Admin")

class App(Base):
    __tablename__ = "apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255))
    package_name = Column(String(255))  # Nazwa pakietu Android
    app_code = Column(Text)  # Kod aplikacji dla bota
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(Integer, ForeignKey("admin.id"))
    
    # Relationships
    clients = relationship("Client", back_populates="app")
    creator = relationship("Admin")

class ContactType(Base):
    __tablename__ = "contact_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    url_pattern = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(Integer, ForeignKey("admin.id"))
    
    # Relationships
    clients = relationship("Client", back_populates="contact_type")
    creator = relationship("Admin")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String(50))
    name = Column(String(255), nullable=False)
    expires_date = Column(Date)
    panel_id = Column(Integer, ForeignKey("panels.id"))
    login = Column(String(255), index=True)
    password = Column(String(255))
    app_id = Column(Integer, ForeignKey("apps.id"))
    mac = Column(String(50), index=True)
    key_value = Column(String(255))
    contact_type_id = Column(Integer, ForeignKey("contact_types.id"))
    contact_value = Column(String(255))
    telegram_id = Column(BigInteger, index=True)  # Ważne dla bota!
    telegram_username_display = Column(String(255))
    notes = Column(Text)
    status = Column(Enum('active', 'inactive', 'suspended'), default='active')
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(Integer, ForeignKey("admin.id"))
    telegram_username = Column(String(255))
    
    # Relationships
    panel = relationship("Panel", back_populates="clients")
    app = relationship("App", back_populates="clients")
    contact_type = relationship("ContactType", back_populates="clients")
    creator = relationship("Admin")
    links = relationship("ClientLink", back_populates="client", cascade="all, delete-orphan")

class ClientLink(Base):
    __tablename__ = "client_links"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    link_url = Column(String(500), nullable=False)
    link_title = Column(String(200), nullable=False)
    link_description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    created_by = Column(BigInteger)
    
    # Relationships
    client = relationship("Client", back_populates="links")

class HelperLink(Base):
    __tablename__ = "helper_links"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    description = Column(Text)
    category = Column(String(50), default='Inne')
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    created_by = Column(Integer, ForeignKey("admin.id"))
    
    # Relationships
    creator = relationship("Admin")

class PaymentOrder(Base):
    __tablename__ = "payment_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(20), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)
    payment_method_id = Column(String(50), nullable=False)
    status = Column(Enum('pending', 'paid', 'expired', 'cancelled'), default='pending', index=True)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    paid_at = Column(DateTime)
    admin_notes = Column(Text)

class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    category = Column(String(100))
    description = Column(Text)
    status = Column(Enum('open', 'in_progress', 'resolved', 'closed'), default='open')
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(50), unique=True, nullable=False)
    setting_value = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("admin.id"))
    action = Column(String(50), nullable=False, index=True)
    details = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.current_timestamp(), index=True)
    
    # Relationships
    user = relationship("Admin")

class TelegramUser(Base):
    __tablename__ = "telegram_users"
    
    telegram_id = Column(BigInteger, primary_key=True)
    login = Column(String(255), nullable=False)
    is_restricted = Column(Boolean, default=False)
    joined_date = Column(DateTime, default=func.current_timestamp())

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("admin.id"), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    last_activity = Column(DateTime, default=func.current_timestamp())
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    user = relationship("Admin")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum('info', 'warning', 'error', 'success'), default='info')
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    user_id = Column(Integer, ForeignKey("admin.id"))
    
    # Relationships
    user = relationship("Admin")

class BannedIP(Base):
    __tablename__ = "banned_ips"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, nullable=False)
    reason = Column(Text)
    banned_by = Column(Integer, ForeignKey("admin.id"))
    ban_time = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    admin = relationship("Admin")

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text)
    attempted_action = Column(String(50))
    status = Column(String(20))
    created_at = Column(DateTime, default=func.current_timestamp(), index=True)
    banned_until = Column(DateTime)

# ============ EXTENDED MODELS FOR JSON DATA ============

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    method_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    fee_percentage = Column(DECIMAL(5, 2), default=0.00)
    min_amount = Column(DECIMAL(10, 2), default=0.00)
    max_amount = Column(DECIMAL(10, 2))
    instructions = Column(Text)
    icon = Column(String(255))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class PricingConfig(Base):
    __tablename__ = "pricing_config"
    
    id = Column(Integer, primary_key=True, index=True)
    service_type = Column(String(100), nullable=False)  # monthly, quarterly, yearly
    price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(10), default='PLN')
    duration_days = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    discount_percentage = Column(DECIMAL(5, 2), default=0.00)
    description = Column(Text)
    features = Column(Text)  # JSON string with features
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class SmartTVApp(Base):
    __tablename__ = "smart_tv_apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(String(100))  # Samsung, LG, Android TV, etc.
    download_url = Column(String(500))
    instructions = Column(Text)
    version = Column(String(50))
    is_active = Column(Boolean, default=True)
    icon = Column(String(255))
    screenshots = Column(Text)  # JSON array of screenshot URLs
    requirements = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class AndroidApp(Base):
    __tablename__ = "android_apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    package_name = Column(String(255))
    download_url = Column(String(500))
    play_store_url = Column(String(500))
    instructions = Column(Text)
    version = Column(String(50))
    is_active = Column(Boolean, default=True)
    icon = Column(String(255))
    screenshots = Column(Text)  # JSON array of screenshot URLs
    minimum_android_version = Column(String(10))
    file_size = Column(String(20))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class SmartTVActivation(Base):
    __tablename__ = "smart_tv_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String(255), nullable=False)  # Nazwa aplikacji
    activation_price = Column(DECIMAL(10, 2), nullable=False)  # Cena za aktywację
    currency = Column(String(10), default='PLN')  # Waluta (PLN, EUR, USD)
    description = Column(Text)  # Opis aktywacji
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class ActivationRequest(Base):
    __tablename__ = "activation_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    request_type = Column(String(100), nullable=False)  # new_activation, renewal, etc.
    status = Column(Enum('pending', 'approved', 'rejected', 'completed'), default='pending')
    details = Column(Text)
    admin_notes = Column(Text)
    processed_by = Column(Integer, ForeignKey("admin.id"))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    processed_at = Column(DateTime)
    
    # Relationships
    processor = relationship("Admin")

# ============ DATABASE FUNCTIONS ============

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables"""
    Base.metadata.drop_all(bind=engine)

def init_database():
    """Initialize database with sample data"""
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin_exists = db.query(Admin).filter(Admin.login == "admin").first()
        
        if not admin_exists:
            # Create default admin
            import bcrypt
            
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin = Admin(
                login="admin",
                password=hashed_password,
                email="admin@tvpanel.com"
            )
            
            db.add(admin)
            db.commit()
            
            print("✅ Default admin created (login: admin, password: admin123)")
        
        # Create default settings if they don't exist
        default_settings = [
            ("default_expiry_days", "30"),
            ("company_name", "TV Panel Pro"),
            ("default_panel_id", "0"),
            ("default_app_id", "0"),
            ("enable_notifications", "1"),
            ("notification_email", "admin@tvpanel.com")
        ]
        
        for key, value in default_settings:
            setting_exists = db.query(Setting).filter(Setting.setting_key == key).first()
            if not setting_exists:
                setting = Setting(setting_key=key, setting_value=value)
                db.add(setting)
        
        db.commit()
        print("✅ Default settings created")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()