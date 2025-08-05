#!/bin/bash

# TV Panel SQL - Restore Script
# This script restores backups of database and application files

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

# Configuration
BACKUP_DIR="/opt/tv-panel/backups"
DB_NAME="tv_panel"
DB_USER="tv_panel_user"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    error "Backup directory not found: $BACKUP_DIR"
fi

# List available backups
echo "Available database backups:"
ls -la "$BACKUP_DIR"/database_*.sql 2>/dev/null || echo "No database backups found"

echo
echo "Available application backups:"
ls -la "$BACKUP_DIR"/app_files_*.tar.gz 2>/dev/null || echo "No application backups found"

echo
echo "Available configuration backups:"
ls -la "$BACKUP_DIR"/config_*.tar.gz 2>/dev/null || echo "No configuration backups found"

# Get user input
echo
read -p "Enter the date/time of backup to restore (YYYYMMDD_HHMMSS): " BACKUP_TIME

if [ -z "$BACKUP_TIME" ]; then
    error "Backup time is required"
fi

# Verify backup files exist
DB_BACKUP="$BACKUP_DIR/database_$BACKUP_TIME.sql"
APP_BACKUP="$BACKUP_DIR/app_files_$BACKUP_TIME.tar.gz"
CONFIG_BACKUP="$BACKUP_DIR/config_$BACKUP_TIME.tar.gz"

if [ ! -f "$DB_BACKUP" ]; then
    error "Database backup not found: $DB_BACKUP"
fi

# Confirmation
warn "This will restore the TV Panel to the state from $BACKUP_TIME"
warn "Current data will be overwritten!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Stop services
log "Stopping TV Panel services..."
systemctl stop tv-panel-backend tv-panel-frontend 2>/dev/null || true

# Database restore
log "Restoring database..."
read -s -p "Enter MySQL password for $DB_USER: " DB_PASS
echo

# Drop and recreate database
mysql -u "$DB_USER" -p"$DB_PASS" << EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE $DB_NAME;
EOF

# Restore database
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$DB_BACKUP"
if [ $? -eq 0 ]; then
    log "Database restored successfully"
else
    error "Database restore failed"
fi

# Application files restore
if [ -f "$APP_BACKUP" ]; then
    log "Restoring application files..."
    
    # Backup current .env files
    cp /opt/tv-panel/backend/.env /tmp/backend.env.backup 2>/dev/null || true
    cp /opt/tv-panel/frontend/.env /tmp/frontend.env.backup 2>/dev/null || true
    
    # Extract files
    cd /
    tar -xzf "$APP_BACKUP"
    
    # Restore .env files if they were backed up
    if [ -f /tmp/backend.env.backup ]; then
        cp /tmp/backend.env.backup /opt/tv-panel/backend/.env
        rm /tmp/backend.env.backup
    fi
    
    if [ -f /tmp/frontend.env.backup ]; then
        cp /tmp/frontend.env.backup /opt/tv-panel/frontend/.env
        rm /tmp/frontend.env.backup
    fi
    
    log "Application files restored successfully"
fi

# Configuration restore
if [ -f "$CONFIG_BACKUP" ]; then
    log "Restoring configuration files..."
    cd /tmp
    tar -xzf "$CONFIG_BACKUP"
    
    # Restore nginx config
    if [ -f /tmp/config_$BACKUP_TIME/tv-panel ]; then
        cp /tmp/config_$BACKUP_TIME/tv-panel /etc/nginx/sites-available/
        nginx -t && systemctl reload nginx
    fi
    
    # Restore systemd services
    cp /tmp/config_$BACKUP_TIME/tv-panel-*.service /etc/systemd/system/ 2>/dev/null || true
    systemctl daemon-reload
    
    # Cleanup
    rm -rf /tmp/config_$BACKUP_TIME
    
    log "Configuration files restored successfully"
fi

# Fix permissions
log "Fixing permissions..."
chown -R www-data:www-data /opt/tv-panel 2>/dev/null || chown -R nobody:nobody /opt/tv-panel

# Reinstall dependencies if needed
log "Installing dependencies..."
cd /opt/tv-panel/backend
source venv/bin/activate
pip install -r requirements.txt

cd /opt/tv-panel/frontend
yarn install

# Start services
log "Starting TV Panel services..."
systemctl start tv-panel-backend tv-panel-frontend

# Check status
sleep 5
if systemctl is-active --quiet tv-panel-backend && systemctl is-active --quiet tv-panel-frontend; then
    log "TV Panel services started successfully"
else
    warn "Some services may not have started properly. Check logs:"
    echo "sudo journalctl -fu tv-panel-backend"
    echo "sudo journalctl -fu tv-panel-frontend"
fi

log "Restore completed successfully!"
echo
echo "TV Panel has been restored to backup from: $BACKUP_TIME"
echo "Access: http://your-server-ip:3000"
echo "Default login: admin/admin123"