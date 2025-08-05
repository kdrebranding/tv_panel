#!/bin/bash

# TV Panel SQL - Automatyczne pobieranie z GitHub i instalacja na aaPanel
# Autor: Assistant AI
# Destination: /www/wwwroot/licencja.kdrebranding.xyz

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
GITHUB_USER="kdrebranding"
REPO_NAME="tv_panel"
DOMAIN="licencja.kdrebranding.xyz"
INSTALL_PATH="/www/wwwroot/$DOMAIN"
GITHUB_URL="https://github.com/$GITHUB_USER/$REPO_NAME"
RAW_URL="https://raw.githubusercontent.com/$GITHUB_USER/$REPO_NAME/main"

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

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

log "🚀 TV Panel SQL - Auto Install from GitHub"
log "Repository: $GITHUB_URL"
log "Installing to: $INSTALL_PATH"

# Check if destination directory exists
if [ ! -d "$INSTALL_PATH" ]; then
    error "Directory $INSTALL_PATH does not exist. Please create the site in aaPanel first!"
fi

# Go to install directory
cd "$INSTALL_PATH"

# Check if we have wget or curl
if command -v wget &> /dev/null; then
    DOWNLOADER="wget -O"
elif command -v curl &> /dev/null; then
    DOWNLOADER="curl -L -o"
else
    error "Neither wget nor curl found. Please install one of them."
fi

log "📥 Downloading TV Panel SQL from GitHub..."

# Download the main ZIP file
log "Downloading repository archive..."
if command -v wget &> /dev/null; then
    wget -O tv_panel.zip "$GITHUB_URL/archive/refs/heads/main.zip"
else
    curl -L -o tv_panel.zip "$GITHUB_URL/archive/refs/heads/main.zip"
fi

# Extract the archive
log "Extracting files..."
unzip -q tv_panel.zip
mv tv_panel-main/* . 2>/dev/null || mv tv_panel-main/.* . 2>/dev/null || true
rmdir tv_panel-main 2>/dev/null || true
rm tv_panel.zip

# Set proper permissions
chown -R www:www "$INSTALL_PATH" 2>/dev/null || chown -R apache:apache "$INSTALL_PATH" 2>/dev/null || chown -R www-data:www-data "$INSTALL_PATH"

log "✅ Files downloaded successfully!"

# Check if we have the setup script
if [ -f "aapanel_setup.sh" ]; then
    log "🔧 Running automatic setup..."
    chmod +x aapanel_setup.sh
    ./aapanel_setup.sh
else
    warn "Setup script not found. Running manual setup..."
    
    # Manual basic setup
    log "Creating basic directory structure..."
    mkdir -p backend frontend scripts logs backups
    
    # Set up backend if requirements.txt exists
    if [ -f "backend/requirements.txt" ]; then
        log "Setting up Python backend..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create default .env if it doesn't exist
        if [ ! -f ".env" ]; then
            cat > .env << EOF
# Environment Configuration
ENVIRONMENT=production

# Database Configuration - UPDATE THESE VALUES
DB_HOST=localhost
DB_USER=tv_panel_user
DB_PASSWORD=CHANGE_THIS_PASSWORD
DB_DATABASE=tv_panel
DATABASE_URL=mysql+pymysql://tv_panel_user:CHANGE_THIS_PASSWORD@localhost/tv_panel

# Security & Authentication
SECRET_KEY=CHANGE_THIS_TO_RANDOM_32_CHARS_MIN_$(date +%s)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7749306488:AAGYYIf-VLe8XWp0tMyh26qoBbBJ-h_uc4A
REMINDER_TELEGRAM_TOKEN=8102053260:AAFR9UwSWTvJ3FWi7Ng5iK1yv-m9Qv8AuRE
ADMIN_USER_ID=6852054255
ADMIN_IDS=6852054255,987654321
REMINDER_HOUR=20
REMINDER_API_KEY=tajnyklucz
WHATSAPP_ADMIN_NUMBER=447451221136

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=
EMAIL_PASS=
ADMIN_EMAILS=admin@$DOMAIN
EOF
        fi
        cd ..
    fi
    
    # Set up frontend if package.json exists
    if [ -f "frontend/package.json" ]; then
        log "Setting up React frontend..."
        cd frontend
        
        # Create .env if it doesn't exist
        if [ ! -f ".env" ]; then
            cat > .env << EOF
REACT_APP_BACKEND_URL=https://$DOMAIN
EOF
        fi
        
        # Install dependencies and build
        npm install
        npm run build
        cd ..
    fi
fi

# Create quick management scripts
log "Creating management scripts..."

cat > start.sh << 'EOF'
#!/bin/bash
cd /www/wwwroot/licencja.kdrebranding.xyz/backend
source venv/bin/activate
python sql_server.py
EOF

cat > status.sh << 'EOF'
#!/bin/bash
echo "=== TV Panel Status ==="
echo "Backend process:"
ps aux | grep "sql_server.py" | grep -v grep || echo "Backend not running"
echo ""
echo "Port 8001:"
netstat -tlnp | grep :8001 || echo "Port 8001 not in use"
echo ""
echo "Files:"
ls -la /www/wwwroot/licencja.kdrebranding.xyz/backend/sql_server.py && echo "Backend files: OK" || echo "Backend files: MISSING"
ls -la /www/wwwroot/licencja.kdrebranding.xyz/frontend/build/index.html && echo "Frontend build: OK" || echo "Frontend build: MISSING"
EOF

chmod +x start.sh status.sh

# Set final permissions
chown -R www:www "$INSTALL_PATH" 2>/dev/null || chown -R apache:apache "$INSTALL_PATH" 2>/dev/null || chown -R www-data:www-data "$INSTALL_PATH"

log "✅ Installation completed!"
echo
echo -e "${BLUE}📋 Next Steps:${NC}"
echo
echo -e "${YELLOW}1. Configure MySQL Database in aaPanel:${NC}"
echo "   - Database → Add database"
echo "   - Name: tv_panel"
echo "   - User: tv_panel_user"
echo "   - Password: [save it!]"
echo
echo -e "${YELLOW}2. Import Database:${NC}"
echo "   - Database → phpMyAdmin"
echo "   - Select tv_panel database"
echo "   - Import → database_mysql.sql"
echo
echo -e "${YELLOW}3. Update Configuration:${NC}"
echo "   - Edit: $INSTALL_PATH/backend/.env"
echo "   - Update DB_PASSWORD with your MySQL password"
echo
echo -e "${YELLOW}4. Configure Nginx:${NC}"
echo "   - Website → Settings → Config File"
echo "   - Add proxy configuration for /api → http://127.0.0.1:8001"
echo
echo -e "${YELLOW}5. Setup Process Manager:${NC}"
echo "   - App Store → Supervisor Manager"
echo "   - Add program: tv-panel-backend"
echo "   - Command: $INSTALL_PATH/start.sh"
echo
echo -e "${GREEN}🌐 Access: https://$DOMAIN${NC}"
echo -e "${GREEN}👤 Login: admin / admin123${NC}"
echo
echo -e "${BLUE}Quick Commands:${NC}"
echo "   ./start.sh    - Start backend manually"
echo "   ./status.sh   - Check system status"
echo
echo -e "${RED}⚠️  Don't forget to:${NC}"
echo "   - Update database password in backend/.env"
echo "   - Configure nginx proxy for /api"
echo "   - Add backend process to Supervisor"
echo "   - Enable SSL certificate"

log "🎉 TV Panel SQL installed from GitHub!"