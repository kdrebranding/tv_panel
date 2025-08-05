# TV Panel SQL - aaPanel Szybki Start ⚡

## 📦 Pliki dla aaPanel VPS

- `tv-panel-aapanel.zip` (267KB) - Do upload przez aaPanel File Manager
- `tv-panel-aapanel.tar.gz` (237KB) - Do upload przez SSH/SCP
- `AAPANEL_INSTALL.md` - Szczegółowa instrukcja

## 🚀 Instalacja w 10 minut

### 1. aaPanel - Utwórz stronę
1. **Website** → **Add site**
2. **Domain:** `licencja.kdrebranding.xyz`
3. **Submit**

### 2. aaPanel - Utwórz bazę MySQL
1. **Database** → **Add database**
2. **Name:** `tv_panel`
3. **User:** `tv_panel_user`
4. **Password:** `[zapisz hasło!]`

### 3. Upload plików
**Opcja A - File Manager:**
1. **File** → **File Manager**
2. Idź do `/www/wwwroot/licencja.kdrebranding.xyz/`
3. Upload `tv-panel-aapanel.zip`
4. **Extract** (rozpakuj)
5. Usuń plik ZIP

**Opcja B - SSH:**
```bash
scp tv-panel-aapanel.tar.gz root@server:/www/wwwroot/licencja.kdrebranding.xyz/
ssh root@server
cd /www/wwwroot/licencja.kdrebranding.xyz/
tar -xzf tv-panel-aapanel.tar.gz
```

### 4. Automatyczna instalacja
```bash
cd /www/wwwroot/licencja.kdrebranding.xyz/
chmod +x aapanel_setup.sh
./aapanel_setup.sh
```

### 5. Konfiguracja
**Edytuj `backend/.env`:**
```
DB_PASSWORD=[twoje_hasło_mysql]
SECRET_KEY=[wygeneruj_długi_klucz]
```

### 6. Import bazy danych
**W aaPanel:**
1. **Database** → **phpMyAdmin**
2. Wybierz `tv_panel`
3. **Import** → `database_mysql.sql`
4. **Go**

### 7. Nginx Config
**Website** → **Settings** → **Config File:**
```nginx
server {
    listen 80;
    server_name licencja.kdrebranding.xyz;
    root /www/wwwroot/licencja.kdrebranding.xyz/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 8. Supervisor (Process Manager)
**App Store** → **Supervisor Manager** → **Add:**
- **Name:** `tv-panel-backend`
- **User:** `www`
- **Directory:** `/www/wwwroot/licencja..../backend`
- **Command:** `/www/wwwroot/licencja..../backend/venv/bin/python sql_server.py`
- **Start**

### 9. SSL Certificate
**Website** → **SSL** → **Let's Encrypt** → **Apply**

## 🌐 Gotowe!

**URL:** `https://licencja.kdrebranding.xyz`
**Login:** `admin` / `admin123`

## ✨ Co działa od razu:

✅ **136 klientów** z przykładowymi danymi  
✅ **Dashboard** z klikalnymi statystykami  
✅ **Import CSV** - gotowy na twój plik  
✅ **Kolumna "Za ile dni wygasa"** z kolorowaniem  
✅ **Bot Telegram** - skonfigurowany  
✅ **Edycja inline** - kliknij i edytuj  
✅ **Responsywny design**  

## 🔧 Zarządzanie w aaPanel

### Logi
**Supervisor Manager** → **Log** → **View**

### Restart
**Supervisor Manager** → **Restart**

### Backup
**Backup** → Dodaj katalog aplikacji + Database backup

### Monitor
**Monitor** → Sprawdź zasoby procesów

## 🔒 Bezpieczeństwo

1. **Zmień hasło admina** po pierwszym logowaniu
2. **Firewall** → Otwórz porty 80, 443, 8001
3. **SSL Auto-renewal** → Enable
4. **SSH** → Zmień domyślny port

## 📊 Funkcje specjalne

### Klikalne statystyki Dashboard
- **136 Wszyscy klienci** → Pełna lista
- **69 Aktywni** → Tylko aktywni
- **2 Wygasający** → Wymagają odnowienia  
- **67 Wygasłe** → Przeterminowane

### Import CSV
- Kompatybilny z twoim plikiem `klienci (5).csv`
- Automatyczne mapowanie wszystkich pól
- Raport importu z szczegółami

### Bot Telegram
- Powiadomienia o wygasających licencjach
- Status: Aktywny (token skonfigurowany)
- Integracja z klientami przez Telegram ID

## 🆘 Problemy?

### Backend nie startuje
1. **Supervisor** → **Log**
2. Sprawdź hasło MySQL w `.env`
3. Test: `cd backend && source venv/bin/activate && python sql_server.py`

### Frontend nie ładuje
1. Sprawdź nginx config
2. **Website** → **Log**
3. Sprawdź czy `frontend/build/` istnieje

### Baza danych
1. **phpMyAdmin** → Sprawdź tabele
2. Test connection w **Database**

## 📁 Struktura aaPanel

```
/www/wwwroot/licencja.kdrebranding.xyz/
├── backend/
│   ├── venv/              # Python env
│   ├── sql_server.py      # Main server
│   └── .env               # Config
├── frontend/
│   ├── build/             # Production files
│   └── src/               # Source code
├── database_mysql.sql     # Database schema
└── AAPANEL_INSTALL.md     # Full guide
```

---

**⏱️ Czas instalacji: ~10 minut**  
**💾 Rozmiar: 267KB**  
**🖥️ Wymagania: aaPanel + MySQL + Python3 + Node.js**

🎉 **TV Panel SQL gotowy na aaPanel!**