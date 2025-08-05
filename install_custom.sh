#!/bin/bash

# TV Panel SQL - Installation Script for Custom Path
# Installing to: /www/wwwroot/licencja.kdrebranding.xyz

set -e

echo "🚀 TV Panel SQL - Installation to /www/wwwroot/licencja.kdrebranding.xyz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_PATH="/www/wwwroot/licencja.kdrebranding.xyz"
DOMAIN="licencja.kdrebranding.xyz"

# Log function
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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

# Detect OS
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    error "Cannot detect OS version"
fi

log "Detected OS: $OS $VER"
log "Installing to: $INSTALL_PATH"
log "Domain: $DOMAIN"

# Install system dependencies
log "Installing system dependencies..."

if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt update
    apt install -y python3 python3-pip python3-venv nodejs npm mysql-server supervisor curl wget unzip
    
    # Install yarn
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
    apt update && apt install -y yarn
    
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
    yum update -y
    yum install -y python3 python3-pip nodejs npm mysql-server supervisor curl wget unzip
    
    # Install yarn
    curl -sL https://rpm.nodesource.com/setup_16.x | bash -
    npm install -g yarn
else
    error "Unsupported OS: $OS"
fi

# Create application directory
log "Creating application directory..."
mkdir -p "$INSTALL_PATH"
mkdir -p "$INSTALL_PATH/backend"
mkdir -p "$INSTALL_PATH/frontend"
mkdir -p "$INSTALL_PATH/scripts"
mkdir -p "$INSTALL_PATH/backups"
mkdir -p "$INSTALL_PATH/logs"

# Copy application files
log "Copying application files..."
cp -r backend/* "$INSTALL_PATH/backend/"
cp -r frontend/* "$INSTALL_PATH/frontend/"
cp -r scripts/* "$INSTALL_PATH/scripts/"
cp init_database.py "$INSTALL_PATH/"
cp database_mysql.sql "$INSTALL_PATH/"

# Set permissions
chmod +x "$INSTALL_PATH/scripts"/*.sh
chmod +x "$INSTALL_PATH/init_database.py"

# Determine web user (www-data for Ubuntu/Debian, apache for CentOS)
WEB_USER="www-data"
if [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
    WEB_USER="apache"
fi

chown -R $WEB_USER:$WEB_USER "$INSTALL_PATH"

# Setup Python virtual environment
log "Setting up Python virtual environment..."
cd "$INSTALL_PATH/backend"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
log "Installing Node.js dependencies..."
cd "$INSTALL_PATH/frontend"
yarn install

# Create systemd services
log "Creating systemd services..."

# Backend service
cat > /etc/systemd/system/tv-panel-backend.service << EOF
[Unit]
Description=TV Panel Backend (licencja.kdrebranding.xyz)
After=network.target mysql.service

[Service]
Type=simple
User=$WEB_USER
WorkingDirectory=$INSTALL_PATH/backend
Environment=PATH=$INSTALL_PATH/backend/venv/bin
ExecStart=$INSTALL_PATH/backend/venv/bin/python sql_server.py
Restart=always
RestartSec=3
StandardOutput=append:$INSTALL_PATH/logs/backend.log
StandardError=append:$INSTALL_PATH/logs/backend_error.log

[Install]
WantedBy=multi-user.target
EOF

# Frontend service  
cat > /etc/systemd/system/tv-panel-frontend.service << EOF
[Unit]
Description=TV Panel Frontend (licencja.kdrebranding.xyz)
After=network.target

[Service]
Type=simple
User=$WEB_USER
WorkingDirectory=$INSTALL_PATH/frontend
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=PORT=3000
ExecStart=/usr/bin/yarn start
Restart=always
RestartSec=3
StandardOutput=append:$INSTALL_PATH/logs/frontend.log
StandardError=append:$INSTALL_PATH/logs/frontend_error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Setup MySQL service
log "Setting up MySQL service..."
systemctl enable mysql
systemctl start mysql

# Create default .env files
log "Creating configuration files..."

# Backend .env
cat > "$INSTALL_PATH/backend/.env" << EOF
# Environment Configuration
ENVIRONMENT=production

# Database Configuration - UPDATE THESE VALUES
DB_HOST=localhost
DB_USER=tv_panel_user
DB_PASSWORD=CHANGE_THIS_PASSWORD
DB_DATABASE=tv_panel
DATABASE_URL=mysql+pymysql://tv_panel_user:CHANGE_THIS_PASSWORD@localhost/tv_panel

# Security & Authentication
SECRET_KEY=CHANGE_THIS_TO_RANDOM_32_CHARS_MIN

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=
EMAIL_PASS=
ADMIN_EMAILS=admin@$DOMAIN

# Telegram Bot Configuration (optional)
TELEGRAM_BOT_TOKEN=7749306488:AAGYYIf-VLe8XWp0tMyh26qoBbBJ-h_uc4A
REMINDER_TELEGRAM_TOKEN=8102053260:AAFR9UwSWTvJ3FWi7Ng5iK1yv-m9Qv8AuRE
ADMIN_USER_ID=6852054255
ADMIN_IDS=6852054255,987654321
REMINDER_HOUR=20
REMINDER_API_KEY=tajnyklucz
WHATSAPP_ADMIN_NUMBER=447451221136
EOF

# Frontend .env
cat > "$INSTALL_PATH/frontend/.env" << EOF
REACT_APP_BACKEND_URL=https://$DOMAIN
EOF

# Set proper ownership
chown -R $WEB_USER:$WEB_USER "$INSTALL_PATH"

# Create nginx configuration
log "Creating Nginx configuration..."
if command -v nginx &> /dev/null; then
    cat > /etc/nginx/sites-available/$DOMAIN << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Frontend (React build files)
    location / {
        root $INSTALL_PATH/frontend/build;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
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

    # Enable site
    ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
fi

# Create database initialization script
cat > "$INSTALL_PATH/setup_database.sh" << EOF
#!/bin/bash
echo "Setting up database for $DOMAIN..."
mysql -u root -p << MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS tv_panel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'tv_panel_user'@'localhost' IDENTIFIED BY 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON tv_panel.* TO 'tv_panel_user'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

cd $INSTALL_PATH
mysql -u tv_panel_user -p tv_panel < database_mysql.sql
EOF

chmod +x "$INSTALL_PATH/setup_database.sh"

# Update backup script paths
sed -i "s|/opt/tv-panel|$INSTALL_PATH|g" "$INSTALL_PATH/scripts/backup.sh"
sed -i "s|/opt/tv-panel|$INSTALL_PATH|g" "$INSTALL_PATH/scripts/restore.sh"

# Create management script
cat > "$INSTALL_PATH/manage.sh" << EOF
#!/bin/bash
# TV Panel Management Script for $DOMAIN

case "\$1" in
    start)
        echo "Starting TV Panel services..."
        systemctl start tv-panel-backend tv-panel-frontend
        ;;
    stop)
        echo "Stopping TV Panel services..."
        systemctl stop tv-panel-backend tv-panel-frontend
        ;;
    restart)
        echo "Restarting TV Panel services..."
        systemctl restart tv-panel-backend tv-panel-frontend
        ;;
    status)
        echo "TV Panel Services Status:"
        systemctl status tv-panel-backend tv-panel-frontend
        ;;
    logs)
        echo "Recent logs:"
        echo "=== Backend Logs ==="
        tail -n 50 $INSTALL_PATH/logs/backend.log
        echo ""
        echo "=== Frontend Logs ==="
        tail -n 50 $INSTALL_PATH/logs/frontend.log
        ;;
    backup)
        echo "Creating backup..."
        $INSTALL_PATH/scripts/backup.sh
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs|backup}"
        exit 1
        ;;
esac
EOF

chmod +x "$INSTALL_PATH/manage.sh"

# Enable services but don't start yet
systemctl enable tv-panel-backend tv-panel-frontend

log "✅ Installation completed successfully!"
echo
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "${YELLOW}1.${NC} Configure MySQL database:"
echo "   sudo mysql_secure_installation"
echo "   cd $INSTALL_PATH && sudo ./setup_database.sh"
echo
echo -e "${YELLOW}2.${NC} Update configuration files:"
echo "   Edit: $INSTALL_PATH/backend/.env"
echo "   Edit: $INSTALL_PATH/frontend/.env"
echo
echo -e "${YELLOW}3.${NC} Build frontend for production:"
echo "   cd $INSTALL_PATH/frontend && yarn build"
echo
echo -e "${YELLOW}4.${NC} Start services:"
echo "   sudo systemctl start tv-panel-backend tv-panel-frontend"
echo "   # OR use: sudo $INSTALL_PATH/manage.sh start"
echo
echo -e "${YELLOW}5.${NC} Check status:"
echo "   sudo $INSTALL_PATH/manage.sh status"
echo
echo -e "${YELLOW}6.${NC} Access application:"
echo "   https://$DOMAIN"
echo "   Default login: admin / admin123"
echo
echo -e "${GREEN}🚀 TV Panel SQL is ready for $DOMAIN!${NC}"
echo -e "${RED}⚠️  Remember to change default passwords and secure your server!${NC}"
echo
echo -e "${BLUE}Management commands:${NC}"
echo "   sudo $INSTALL_PATH/manage.sh {start|stop|restart|status|logs|backup}"