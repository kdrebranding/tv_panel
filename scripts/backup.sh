#!/bin/bash

# TV Panel SQL - Backup Script
# This script creates backups of database and application files

set -e

# Configuration
BACKUP_DIR="/opt/tv-panel/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="tv_panel"
DB_USER="tv_panel_user"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting TV Panel backup..."

# Database backup
log "Backing up database..."
read -s -p "Enter MySQL password for $DB_USER: " DB_PASS
echo

mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_DIR/database_$DATE.sql"
if [ $? -eq 0 ]; then
    log "Database backup completed: database_$DATE.sql"
else
    error "Database backup failed"
fi

# Application files backup
log "Backing up application files..."
tar -czf "$BACKUP_DIR/app_files_$DATE.tar.gz" \
    --exclude="$BACKUP_DIR" \
    --exclude="/opt/tv-panel/backend/venv" \
    --exclude="/opt/tv-panel/frontend/node_modules" \
    --exclude="/opt/tv-panel/frontend/build" \
    /opt/tv-panel

if [ $? -eq 0 ]; then
    log "Application files backup completed: app_files_$DATE.tar.gz"
else
    error "Application files backup failed"
fi

# Configuration backup
log "Backing up configuration files..."
mkdir -p "$BACKUP_DIR/config_$DATE"
cp /opt/tv-panel/backend/.env "$BACKUP_DIR/config_$DATE/"
cp /opt/tv-panel/frontend/.env "$BACKUP_DIR/config_$DATE/"
cp /etc/nginx/sites-available/tv-panel "$BACKUP_DIR/config_$DATE/" 2>/dev/null || true
cp /etc/systemd/system/tv-panel-*.service "$BACKUP_DIR/config_$DATE/" 2>/dev/null || true

tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "$BACKUP_DIR" "config_$DATE"
rm -rf "$BACKUP_DIR/config_$DATE"

# Cleanup old backups (keep last 7 days)
log "Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

# Show backup summary
log "Backup completed successfully!"
echo
echo "Backup files created:"
ls -lh "$BACKUP_DIR"/*_$DATE.*

# Calculate total backup size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo
echo "Total backup directory size: $TOTAL_SIZE"
echo "Backup location: $BACKUP_DIR"