#!/bin/bash

# TV Panel SQL - Installation Script for VPS
# This script installs and configures the TV Panel application

set -e

echo "🚀 TV Panel SQL - VPS Installation Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
mkdir -p /opt/tv-panel
chown -R www-data:www-data /opt/tv-panel 2>/dev/null || chown -R nobody:nobody /opt/tv-panel

# Copy application files
log "Copying application files..."
cp -r backend /opt/tv-panel/
cp -r frontend /opt/tv-panel/
cp -r scripts /opt/tv-panel/
cp init_database.py /opt/tv-panel/
cp supervisord.conf /opt/tv-panel/

# Set permissions
chmod +x /opt/tv-panel/scripts/*.sh
chmod +x /opt/tv-panel/init_database.py

# Setup Python virtual environment
log "Setting up Python virtual environment..."
cd /opt/tv-panel/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
log "Installing Node.js dependencies..."
cd /opt/tv-panel/frontend
yarn install
yarn build

# Create systemd services
log "Creating systemd services..."

# Backend service
cat > /etc/systemd/system/tv-panel-backend.service << EOF
[Unit]
Description=TV Panel Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tv-panel/backend
Environment=PATH=/opt/tv-panel/backend/venv/bin
ExecStart=/opt/tv-panel/backend/venv/bin/python sql_server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
cat > /etc/systemd/system/tv-panel-frontend.service << EOF
[Unit]
Description=TV Panel Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tv-panel/frontend
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/yarn start
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Setup MySQL service
log "Setting up MySQL service..."
systemctl enable mysql
systemctl start mysql

# Create default .env files if they don't exist
log "Creating default configuration files..."

# Backend .env
if [ ! -f /opt/tv-panel/backend/.env ]; then
    cat > /opt/tv-panel/backend/.env << EOF
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
ADMIN_EMAILS=admin@yourdomain.com

# Telegram Bot Configuration (optional)
TELEGRAM_BOT_TOKEN=
REMINDER_TELEGRAM_TOKEN=
ADMIN_USER_ID=
ADMIN_IDS=
REMINDER_HOUR=20
REMINDER_API_KEY=
WHATSAPP_ADMIN_NUMBER=
EOF
fi

# Frontend .env
if [ ! -f /opt/tv-panel/frontend/.env ]; then
    cat > /opt/tv-panel/frontend/.env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
EOF
fi

# Set proper ownership
chown -R www-data:www-data /opt/tv-panel 2>/dev/null || chown -R nobody:nobody /opt/tv-panel

# Create nginx configuration
log "Creating Nginx configuration..."
if command -v nginx &> /dev/null; then
    cat > /etc/nginx/sites-available/tv-panel << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
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
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/tv-panel /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl reload nginx
fi

# Create database initialization script
cat > /opt/tv-panel/setup_database.sh << EOF
#!/bin/bash
echo "Setting up database..."
mysql -u root -p << MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS tv_panel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'tv_panel_user'@'localhost' IDENTIFIED BY 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON tv_panel.* TO 'tv_panel_user'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

cd /opt/tv-panel
python3 init_database.py
EOF

chmod +x /opt/tv-panel/setup_database.sh

# Enable services but don't start yet
systemctl enable tv-panel-backend tv-panel-frontend

log "✅ Installation completed successfully!"
echo
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "${YELLOW}1.${NC} Configure MySQL database:"
echo "   sudo mysql_secure_installation"
echo "   cd /opt/tv-panel && sudo ./setup_database.sh"
echo
echo -e "${YELLOW}2.${NC} Update configuration files:"
echo "   Edit: /opt/tv-panel/backend/.env"
echo "   Edit: /opt/tv-panel/frontend/.env"
echo
echo -e "${YELLOW}3.${NC} Start services:"
echo "   sudo systemctl start tv-panel-backend tv-panel-frontend"
echo
echo -e "${YELLOW}4.${NC} Check status:"
echo "   sudo systemctl status tv-panel-backend tv-panel-frontend"
echo
echo -e "${YELLOW}5.${NC} Access application:"
echo "   http://your-server-ip:3000"
echo "   Default login: admin / admin123"
echo
echo -e "${GREEN}🚀 TV Panel SQL is ready to use!${NC}"
echo -e "${RED}⚠️  Remember to change default passwords and secure your server!${NC}"