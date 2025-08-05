#!/bin/bash

# TV Panel SQL - aaPanel Setup Script
# For domain: licencja.kdrebranding.xyz
# Path: /www/wwwroot/licencja.kdrebranding.xyz

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN="licencja.kdrebranding.xyz"
INSTALL_PATH="/www/wwwroot/$DOMAIN"
WEB_USER="www"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if we're in the correct directory
if [ ! -d "$INSTALL_PATH" ]; then
    error "Directory $INSTALL_PATH does not exist. Please create the site in aaPanel first."
fi

log "🚀 TV Panel SQL - aaPanel Setup for $DOMAIN"
log "Install path: $INSTALL_PATH"

# Check if aaPanel is installed
if [ ! -d "/www/server" ]; then
    warn "aaPanel not detected. This script is designed for aaPanel systems."
fi

# Install system dependencies if needed
log "Checking system dependencies..."

# Python 3 and pip
if ! command -v python3 &> /dev/null; then
    log "Installing Python 3..."
    yum install -y python3 python3-pip 2>/dev/null || apt-get install -y python3 python3-pip
fi

# Node.js and npm
if ! command -v node &> /dev/null; then
    log "Installing Node.js..."
    # Try to install via aaPanel first
    if [ -f "/www/server/nodejs/bin/node" ]; then
        ln -sf /www/server/nodejs/bin/node /usr/local/bin/node
        ln -sf /www/server/nodejs/bin/npm /usr/local/bin/npm
    else
        curl -sL https://rpm.nodesource.com/setup_16.x | bash - 2>/dev/null || curl -sL https://deb.nodesource.com/setup_16.x | bash -
        yum install -y nodejs 2>/dev/null || apt-get install -y nodejs
    fi
fi

# Go to install directory
cd "$INSTALL_PATH"

# Create directory structure
log "Creating directory structure..."
mkdir -p backend frontend logs backups scripts

# Set proper ownership
chown -R $WEB_USER:$WEB_USER "$INSTALL_PATH"

# Setup backend
if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
    log "Setting up Python backend..."
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip and install requirements
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create default .env if it doesn't exist
    if [ ! -f ".env" ]; then
        log "Creating default .env file..."
        cat > .env << EOF
# Environment Configuration
ENVIRONMENT=production

# Database Configuration - UPDATE THESE VALUES IN aaPanel
DB_HOST=localhost
DB_USER=tv_panel_user
DB_PASSWORD=CHANGE_THIS_PASSWORD
DB_DATABASE=tv_panel
DATABASE_URL=mysql+pymysql://tv_panel_user:CHANGE_THIS_PASSWORD@localhost/tv_panel

# Security & Authentication
SECRET_KEY=CHANGE_THIS_TO_RANDOM_32_CHARS_MIN_aapanel_$(date +%s)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7749306488:AAGYYIf-VLe8XWp0tMyh26qoBbBJ-h_uc4A
REMINDER_TELEGRAM_TOKEN=8102053260:AAFR9UwSWTvJ3FWi7Ng5iK1yv-m9Qv8AuRE
ADMIN_USER_ID=6852054255
ADMIN_IDS=6852054255,987654321
REMINDER_HOUR=20
REMINDER_API_KEY=tajnyklucz
WHATSAPP_ADMIN_NUMBER=447451221136

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=
EMAIL_PASS=
ADMIN_EMAILS=admin@$DOMAIN
EOF
    fi
    
    cd ..
fi

# Setup frontend
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    log "Setting up React frontend..."
    cd frontend
    
    # Create default .env if it doesn't exist
    if [ ! -f ".env" ]; then
        cat > .env << EOF
REACT_APP_BACKEND_URL=https://$DOMAIN
EOF
    fi
    
    # Install dependencies
    npm install
    
    # Build for production
    log "Building frontend for production..."
    npm run build
    
    cd ..
fi

# Create management scripts
log "Creating management scripts..."

# Start script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd /www/wwwroot/licencja.kdrebranding.xyz/backend
source venv/bin/activate
python sql_server.py
EOF

# Stop script  
cat > stop_backend.sh << 'EOF'
#!/bin/bash
pkill -f "python sql_server.py"
EOF

# Status script
cat > status.sh << 'EOF'
#!/bin/bash
echo "=== TV Panel Status ==="
echo "Backend process:"
ps aux | grep "sql_server.py" | grep -v grep || echo "Backend not running"
echo ""
echo "Port 8001 usage:"
netstat -tlnp | grep :8001 || echo "Port 8001 not in use"
echo ""
echo "Recent backend logs:"
tail -n 10 /www/wwwroot/licencja.kdrebranding.xyz/logs/backend.log 2>/dev/null || echo "No backend logs found"
EOF

# Make scripts executable
chmod +x start_backend.sh stop_backend.sh status.sh

# Create supervisor config for aaPanel
log "Creating supervisor configuration..."
mkdir -p /www/server/panel/pyproject/supervisor/config

cat > /www/server/panel/pyproject/supervisor/config/tv-panel-backend.conf << EOF
[program:tv-panel-backend]
command=$INSTALL_PATH/backend/venv/bin/python sql_server.py
directory=$INSTALL_PATH/backend
user=$WEB_USER
autostart=true
autorestart=true
startsecs=3
startretries=3
stdout_logfile=$INSTALL_PATH/logs/backend.log
stderr_logfile=$INSTALL_PATH/logs/backend_error.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=5
environment=PATH="$INSTALL_PATH/backend/venv/bin"
EOF

# Create nginx configuration template
log "Creating nginx configuration template..."
cat > nginx_config_template.txt << EOF
# Add this to your nginx site configuration in aaPanel:

server {
    listen 80;
    server_name $DOMAIN;
    root $INSTALL_PATH/frontend/build;
    index index.html;

    # Frontend (React build)
    location / {
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Logs
    access_log $INSTALL_PATH/logs/nginx_access.log;
    error_log $INSTALL_PATH/logs/nginx_error.log;
}
EOF

# Create database import script
if [ -f "database_mysql.sql" ]; then
    log "Creating database import script..."
    cat > import_database.sh << EOF
#!/bin/bash
echo "Importing database to MySQL..."
echo "Make sure you have created database 'tv_panel' and user 'tv_panel_user' in aaPanel first!"
echo ""
read -p "MySQL root password: " -s MYSQL_ROOT_PASS
echo ""
read -p "tv_panel_user password: " -s DB_PASS
echo ""

# Import the database
mysql -u root -p\$MYSQL_ROOT_PASS tv_panel < $INSTALL_PATH/database_mysql.sql

echo "Database imported successfully!"
echo "Don't forget to update backend/.env with the correct database password!"
EOF
    chmod +x import_database.sh
fi

# Set final permissions
chown -R $WEB_USER:$WEB_USER "$INSTALL_PATH"
chmod -R 755 "$INSTALL_PATH"

log "✅ aaPanel setup completed!"
echo
echo -e "${BLUE}📋 Next Steps in aaPanel:${NC}"
echo
echo -e "${YELLOW}1. Create MySQL Database:${NC}"
echo "   - Go to aaPanel → Database → Add database"
echo "   - Database name: tv_panel"
echo "   - Username: tv_panel_user"
echo "   - Save the password!"
echo
echo -e "${YELLOW}2. Import Database:${NC}"
echo "   - Use phpMyAdmin or run: ./import_database.sh"
echo
echo -e "${YELLOW}3. Update Configuration:${NC}"
echo "   - Edit: $INSTALL_PATH/backend/.env"
echo "   - Update DB_PASSWORD with your MySQL password"
echo
echo -e "${YELLOW}4. Configure Nginx:${NC}"
echo "   - aaPanel → Website → Settings → Config File"
echo "   - Copy configuration from: nginx_config_template.txt"
echo
echo -e "${YELLOW}5. Setup Supervisor (Process Manager):${NC}"
echo "   - aaPanel → App Store → Supervisor Manager"
echo "   - Add program: tv-panel-backend"
echo "   - Command: $INSTALL_PATH/start_backend.sh"
echo "   - Directory: $INSTALL_PATH/backend"
echo "   - User: $WEB_USER"
echo
echo -e "${YELLOW}6. SSL Certificate:${NC}"
echo "   - aaPanel → Website → SSL → Let's Encrypt"
echo
echo -e "${GREEN}🌐 Access: https://$DOMAIN${NC}"
echo -e "${GREEN}👤 Login: admin / admin123${NC}"
echo
echo -e "${BLUE}Management Commands:${NC}"
echo "   ./start_backend.sh   - Start backend"
echo "   ./stop_backend.sh    - Stop backend"
echo "   ./status.sh          - Check status"
echo
echo -e "${RED}⚠️  Remember to:${NC}"
echo "   - Change default admin password"
echo "   - Update .env with strong passwords"
echo "   - Enable SSL certificate"
echo "   - Configure firewall in aaPanel"