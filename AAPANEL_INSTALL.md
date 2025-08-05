# TV Panel SQL - Instalacja na aaPanel

## 📋 Instrukcja dla aaPanel VPS

### Wymagania
- VPS z zainstalowanym aaPanel
- Python 3.8+
- Node.js 16+
- MySQL (dostępny w aaPanel)
- Domena: `licencja.kdrebranding.xyz`

## 🚀 Instalacja (15 minut)

### 1. Przygotowanie w aaPanel

#### A. Utwórz stronę w aaPanel
1. Zaloguj się do aaPanel
2. **Website** → **Add site**
3. **Domain:** `licencja.kdrebranding.xyz`
4. **Path:** `/www/wwwroot/licencja.kdrebranding.xyz`
5. **PHP Version:** Nie potrzebne (używamy Python)
6. Kliknij **Submit**

#### B. Utwórz bazę danych MySQL
1. **Database** → **MySQL** → **Add database**
2. **Database name:** `tv_panel`
3. **Username:** `tv_panel_user`
4. **Password:** `[wygeneruj silne hasło]`
5. Zapisz dane - będą potrzebne później!

### 2. Upload plików

#### Przez aaPanel File Manager
1. **File** → **File Manager**
2. Przejdź do `/www/wwwroot/licencja.kdrebranding.xyz/`
3. Upload `tv-panel-aapanel.zip`
4. Rozpakuj archiwum
5. Usuń plik zip

#### Lub przez SSH/FTP
```bash
# Upload przez SCP
scp tv-panel-aapanel.zip root@your-server:/www/wwwroot/licencja.kdrebranding.xyz/

# SSH do serwera
ssh root@your-server
cd /www/wwwroot/licencja.kdrebranding.xyz/
unzip tv-panel-aapanel.zip
rm tv-panel-aapanel.zip
```

### 3. Konfiguracja

#### A. Edytuj backend/.env
```bash
nano /www/wwwroot/licencja.kdrebranding.xyz/backend/.env
```

Zaktualizuj dane MySQL:
```env
DB_HOST=localhost
DB_USER=tv_panel_user
DB_PASSWORD=[twoje_hasło_z_aapanel]
DB_DATABASE=tv_panel
DATABASE_URL=mysql+pymysql://tv_panel_user:[hasło]@localhost/tv_panel

SECRET_KEY=[wygeneruj_długi_losowy_klucz]
```

#### B. Zaimportuj bazę danych
W aaPanel:
1. **Database** → **phpMyAdmin**
2. Wybierz bazę `tv_panel`
3. **Import** → Wybierz plik `database_mysql.sql`
4. Kliknij **Go**

### 4. Instalacja zależności

```bash
# Przejdź do katalogu
cd /www/wwwroot/licencja.kdrebranding.xyz/

# Backend - Python
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend - Node.js
cd ../frontend
npm install
npm run build
```

### 5. Uruchomienie serwisów

#### A. Utwórz procesory w aaPanel

**Backend Process:**
1. **App Store** → **Installed** → **Supervisor Manager**
2. **Add** → **Program**
3. **Name:** `tv-panel-backend`
4. **Run User:** `www`
5. **Run Directory:** `/www/wwwroot/licencja.kdrebranding.xyz/backend`
6. **Start Command:** `/www/wwwroot/licencja.kdrebrending.xyz/backend/venv/bin/python sql_server.py`
7. **Save**

**Frontend Process (opcjonalnie - dla development):**
1. **Add** → **Program**
2. **Name:** `tv-panel-frontend`
3. **Run User:** `www`
4. **Run Directory:** `/www/wwwroot/licencja.kdrebranding.xyz/frontend`
5. **Start Command:** `npm start`
6. **Save**

### 6. Konfiguracja Nginx w aaPanel

1. **Website** → **Site List**
2. Kliknij **Settings** przy `licencja.kdrebranding.xyz`
3. **Config File** → Edytuj nginx config:

```nginx
server {
    listen 80;
    server_name licencja.kdrebranding.xyz;
    root /www/wwwroot/licencja.kdrebranding.xyz/frontend/build;
    index index.html;

    # Frontend (React build)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

4. **Save** → **Reload Nginx**

### 7. SSL Certificate (aaPanel)

1. **Website** → **Site List**
2. **SSL** przy domenie
3. **Let's Encrypt** → **Apply**
4. Poczekaj na wygenerowanie certyfikatu

### 8. Start aplikacji

W **Supervisor Manager**:
1. Kliknij **Start** przy `tv-panel-backend`
2. Sprawdź status - powinien być **RUNNING**

## 🌐 Dostęp

- **URL:** `https://licencja.kdrebranding.xyz`
- **Login:** `admin`
- **Hasło:** `admin123`

## 🔧 Zarządzanie przez aaPanel

### Logi aplikacji
1. **Supervisor Manager**
2. Kliknij **Log** przy procesie
3. **View** → Zobacz logi

### Restart serwisów
1. **Supervisor Manager**
2. **Restart** przy procesie

### Backup
1. **Backup** w aaPanel
2. Dodaj katalog: `/www/wwwroot/licencja.kdrebranding.xyz`
3. Backup bazy: **Database** → **Backup**

### Monitor zasobów
1. **Monitor** → **Resource**
2. Sprawdź CPU/RAM używane przez procesy

## 🔒 Bezpieczeństwo

### Firewall aaPanel
1. **Security** → **Firewall**
2. Otwórz porty: 80, 443, 8001
3. **SSH** → Zmień domyślny port

### SSL Auto-renewal
1. **Website** → **SSL**
2. **Auto Renew** → **Enable**

## 📊 Funkcjonalności

✅ **Dashboard z statystykami**  
✅ **136 przykładowych klientów**  
✅ **Import CSV** (twój plik klienci.csv)  
✅ **Export CSV**  
✅ **Bot Telegram** (skonfigurowany)  
✅ **Kolumna "Za ile dni wygasa"**  
✅ **Edycja inline**  
✅ **Responsywny design**  

## 🆘 Troubleshooting

### Backend nie startuje
1. **Supervisor Manager** → **Log**
2. Sprawdź błędy w logach
3. Sprawdź połączenie MySQL w `.env`

### Frontend nie ładuje się
1. Sprawdź czy nginx config jest poprawny
2. **Website** → **Log** → Sprawdź error log
3. Sprawdź czy build został utworzony: `frontend/build/`

### Problem z bazą danych
1. **Database** → **phpMyAdmin**
2. Sprawdź czy tabele zostały utworzone
3. Test connection: **Database** → **MySQL** → **Root Password**

### Porty zajęte
1. **Monitor** → **Process**
2. Sprawdź co używa portu 8001
3. W razie potrzeby zmień port w `sql_server.py`

## 📁 Struktura plików

```
/www/wwwroot/licencja.kdrebranding.xyz/
├── backend/              # Python FastAPI
│   ├── venv/            # Virtual environment
│   ├── sql_server.py    # Main server
│   └── .env             # Configuration
├── frontend/            # React app
│   ├── build/           # Production build
│   └── src/             # Source code
├── database_mysql.sql   # Database schema
└── README_AAPANEL.md    # This file
```

## 🎉 Gotowe!

Po wykonaniu wszystkich kroków:
1. Backend działa na porcie 8001
2. Frontend (build) jest serwowany przez nginx
3. Aplikacja dostępna pod: `https://licencja.kdrebranding.xyz`
4. Wszystko zarządzane przez aaPanel

---

**💡 Wskazówka:** Używaj aaPanel do monitorowania, backupów i zarządzania. To jest najbezpieczniejszy sposób na tym typie hostingu.