# TV Panel SQL - Deployment Guide dla VPS

## Wymagania systemowe

- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Python 3.8+
- Node.js 16+
- MySQL 8.0+ / MariaDB 10.6+
- Nginx (opcjonalnie)
- 2GB RAM minimum
- 10GB przestrzeni dyskowej

## Szybka instalacja (Ubuntu/Debian)

### 1. Przygotowanie systemu
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm mysql-server nginx supervisor git curl

# Install yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update && sudo apt install yarn

# Start services
sudo systemctl enable mysql nginx supervisor
sudo systemctl start mysql nginx supervisor
```

### 2. Konfiguracja MySQL
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

W MySQL wykonaj:
```sql
CREATE DATABASE tv_panel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tv_panel_user'@'localhost' IDENTIFIED BY 'twoje_bezpieczne_haslo';
GRANT ALL PRIVILEGES ON tv_panel.* TO 'tv_panel_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Deploy aplikacji
```bash
# Upload files to VPS (przykład z scp)
scp -r tv-panel-deployment.tar.gz user@your-vps-ip:/home/user/

# Na VPS
cd /home/user
tar -xzf tv-panel-deployment.tar.gz
cd tv-panel

# Make install script executable
chmod +x install.sh

# Run installation
sudo ./install.sh
```

### 4. Konfiguracja zmiennych środowiskowych

Edytuj `/opt/tv-panel/backend/.env`:
```bash
# Database Configuration
DB_HOST=localhost
DB_USER=tv_panel_user
DB_PASSWORD=twoje_bezpieczne_haslo
DB_DATABASE=tv_panel
DATABASE_URL=mysql+pymysql://tv_panel_user:twoje_bezpieczne_haslo@localhost/tv_panel

# Security
SECRET_KEY=wygeneruj_silny_klucz_32_znaki_min

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
REMINDER_TELEGRAM_TOKEN=your_reminder_token
ADMIN_USER_ID=your_telegram_id
ADMIN_IDS=your_telegram_id,other_admin_id
WHATSAPP_ADMIN_NUMBER=your_whatsapp_number

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
ADMIN_EMAILS=admin@yourdomain.com
```

Edytuj `/opt/tv-panel/frontend/.env`:
```bash
REACT_APP_BACKEND_URL=https://your-domain.com
```

### 5. Inicjalizacja bazy danych
```bash
cd /opt/tv-panel/backend
python3 init_database.py
```

### 6. Start serwisów
```bash
sudo systemctl restart tv-panel-backend tv-panel-frontend
sudo systemctl enable tv-panel-backend tv-panel-frontend

# Check status
sudo systemctl status tv-panel-backend tv-panel-frontend
```

### 7. Konfiguracja Nginx (opcjonalna)

Edytuj `/etc/nginx/sites-available/tv-panel`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-I p $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/tv-panel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL Certificate (opcjonalne)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Dostęp do aplikacji

- **URL:** http://your-vps-ip:3000 lub https://your-domain.com
- **Login:** admin
- **Hasło:** admin123

**WAŻNE:** Zmień hasło administratora po pierwszym logowaniu!

## Zarządzanie serwisami

```bash
# Restart services
sudo systemctl restart tv-panel-backend tv-panel-frontend

# View logs
sudo journalctl -fu tv-panel-backend
sudo journalctl -fu tv-panel-frontend

# Stop/Start
sudo systemctl stop tv-panel-backend
sudo systemctl start tv-panel-backend
```

## Backup

```bash
# Backup database
mysqldump -u tv_panel_user -p tv_panel > tv_panel_backup_$(date +%Y%m%d).sql

# Backup application files
tar -czf tv_panel_files_backup_$(date +%Y%m%d).tar.gz /opt/tv-panel
```

## Troubleshooting

### Backend nie startuje
```bash
sudo journalctl -fu tv-panel-backend
cd /opt/tv-panel/backend
python3 sql_server.py  # Test manual start
```

### Frontend nie startuje
```bash
sudo journalctl -fu tv-panel-frontend
cd /opt/tv-panel/frontend
yarn start  # Test manual start
```

### Database connection error
- Sprawdź dane w `/opt/tv-panel/backend/.env`
- Test connection: `mysql -u tv_panel_user -p tv_panel`

### Port conflicts
- Backend: 8001
- Frontend: 3000
- Sprawdź czy porty są wolne: `netstat -tlnp | grep :8001`

## Security Notes

1. Zmień domyślne hasło administratora
2. Ustaw firewall (ufw):
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```
3. Regularnie aktualizuj system
4. Używaj SSL certyfikatów
5. Backup regularnie bazy danych

## Support

W przypadku problemów sprawdź:
- Logi systemowe: `sudo journalctl -f`
- Status serwisów: `sudo systemctl status tv-panel-*`
- Połączenie z bazą danych
- Porty i firewall

Aplikacja działa na portach:
- Backend: 8001
- Frontend: 3000
- MySQL: 3306