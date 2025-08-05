# TV Panel SQL - Szybki Start na VPS

## 📦 Co otrzymujesz

- `tv-panel-deployment.tar.gz` - Kompletna aplikacja (240KB)
- `DEPLOYMENT_GUIDE.md` - Szczegółowa instrukcja  
- `database_mysql.sql` - Schema MySQL z przykładowymi danymi
- Automatyczne skrypty instalacyjne

## 🚀 Szybka instalacja (5 minut)

### 1. Upload na VPS
```bash
# Upload pliku na VPS
scp tv-panel-deployment.tar.gz user@your-vps-ip:/home/user/

# Połącz się z VPS
ssh user@your-vps-ip

# Rozpakuj
cd /home/user
tar -xzf tv-panel-deployment.tar.gz
cd tv-panel
```

### 2. Uruchom instalację
```bash
# Nadaj uprawnienia
chmod +x install.sh

# Uruchom jako root
sudo ./install.sh
```

### 3. Skonfiguruj MySQL
```bash
# Zabezpiecz MySQL
sudo mysql_secure_installation

# Utwórz bazę danych
sudo mysql -u root -p < database_mysql.sql
```

### 4. Konfiguracja
Edytuj `/opt/tv-panel/backend/.env`:
```bash
# Zmień hasło bazy danych
DB_PASSWORD=twoje_nowe_haslo_mysql

# Zmień klucz bezpieczeństwa  
SECRET_KEY=wygeneruj_losowy_klucz_32_znaki

# Opcjonalnie - dane bota Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_USER_ID=your_telegram_id
```

### 5. Start aplikacji
```bash
# Uruchom serwisy
sudo systemctl start tv-panel-backend tv-panel-frontend

# Sprawdź status
sudo systemctl status tv-panel-backend tv-panel-frontend
```

## 🌐 Dostęp

- **URL:** `http://your-vps-ip:3000`
- **Login:** `admin`
- **Hasło:** `admin123`

## ⚡ Co działa od razu

✅ **136 klientów z przykładowymi danymi**  
✅ **Wszystkie sekcje:** Klienci, Panele, Aplikacje, FAQ, itd.  
✅ **Filtrowanie:** Aktywni, wygasający, przeterminowani  
✅ **Import CSV:** Gotowy do użycia z Twoim plikiem  
✅ **Export CSV:** Klienci, panele  
✅ **Bot Telegram:** Skonfigurowany (wymaga tokena)  
✅ **Kolumna "Za ile dni wygasa"** z kolorowaniem  
✅ **Edycja inline:** Kliknij i edytuj  
✅ **Responsywny design:** Działa na mobile  

## 🔧 Zarządzanie

```bash
# Restart serwisów
sudo systemctl restart tv-panel-backend tv-panel-frontend

# Logi
sudo journalctl -fu tv-panel-backend
sudo journalctl -fu tv-panel-frontend

# Backup
/opt/tv-panel/scripts/backup.sh

# Restore  
/opt/tv-panel/scripts/restore.sh
```

## 🔒 Bezpieczeństwo

1. **Zmień hasło administratora** po pierwszym logowaniu
2. **Zmień hasło MySQL** w `.env`
3. **Wygeneruj nowy SECRET_KEY**
4. **Ustaw firewall:**
   ```bash
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443  
   sudo ufw enable
   ```

## 📊 Funkcjonalności

### Dashboard z klikalnymi statystykami
- **136 Wszyscy klienci** → Lista wszystkich
- **69 Aktywni klienci** → Tylko aktywni  
- **2 Wygasający wkrótce** → Wymagają odnowienia
- **67 Wygasłe licencje** → Przeterminowane

### Import CSV
- Kompatybilny z Twoim plikiem `klienci (5).csv`
- Automatyczne mapowanie pól
- Raport importu z błędami
- Aktualizacja statystyk

### Bot Telegram
- Powiadomienia o wygasających licencjach
- Integracja z klientami (Telegram ID)
- Konfiguracja przez `.env`

## 🆘 Wsparcie

**Problemy?** Sprawdź:
1. `sudo systemctl status tv-panel-*`
2. `sudo journalctl -fu tv-panel-backend`
3. Połączenie MySQL: `mysql -u tv_panel_user -p tv_panel`
4. Porty: `netstat -tlnp | grep :3000`

## 📁 Struktura plików

```
/opt/tv-panel/
├── backend/          # Python FastAPI
├── frontend/         # React aplikacja  
├── scripts/          # Backup/restore
└── backups/          # Automatyczne backupy
```

**🎉 Gotowe! Aplikacja TV Panel SQL działa na Twoim VPS!**

---

*Czas instalacji: ~5 minut*  
*Wymagania: Ubuntu 20.04+, 2GB RAM, MySQL*