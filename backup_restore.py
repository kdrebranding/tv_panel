#!/usr/bin/env python3
"""
TV Panel Backup & Restore System
Automatyczny system tworzenia kopii zapasowych i przywracania danych.
"""

import os
import json
import asyncio
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional
import argparse
import logging
from dotenv import load_dotenv
import subprocess
import schedule
import time
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

# MongoDB connection
MONGO_URL = os.environ['MONGO_URL']
client = AsyncIOMotorClient(MONGO_URL)
db = client[os.environ['DB_NAME']]

# Configuration
BACKUP_DIR = Path(__file__).parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# Email configuration for notifications
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASS = os.getenv('EMAIL_PASS', '')
ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', '').split(',')

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_restore.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupRestoreManager:
    
    def __init__(self):
        self.collections = [
            'admins', 'clients', 'panels', 'apps', 
            'contact_types', 'settings'
        ]
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create full system backup"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = backup_name or f"tv_panel_backup_{timestamp}"
        backup_path = BACKUP_DIR / backup_name
        backup_path.mkdir(exist_ok=True)
        
        logger.info(f"🔄 Rozpoczynam tworzenie kopii zapasowej: {backup_name}")
        
        # Backup metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "collections": self.collections,
            "total_documents": 0,
            "backup_type": "full"
        }
        
        try:
            # Backup each collection
            for collection_name in self.collections:
                collection = db[collection_name]
                documents = await collection.find().to_list(None)
                
                # Save collection data
                collection_file = backup_path / f"{collection_name}.json"
                with open(collection_file, 'w', encoding='utf-8') as f:
                    json.dump(documents, f, indent=2, default=str, ensure_ascii=False)
                
                metadata["total_documents"] += len(documents)
                logger.info(f"   ✅ {collection_name}: {len(documents)} dokumentów")
            
            # Save metadata
            metadata_file = backup_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Create ZIP archive
            zip_path = f"{backup_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in backup_path.rglob('*'):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(backup_path))
            
            # Remove uncompressed directory
            shutil.rmtree(backup_path)
            
            # Calculate file size
            file_size = os.path.getsize(zip_path) / 1024 / 1024  # MB
            
            logger.info(f"✅ Kopia zapasowa utworzona: {zip_path}")
            logger.info(f"   📊 Dokumentów: {metadata['total_documents']}")
            logger.info(f"   💾 Rozmiar: {file_size:.2f} MB")
            
            # Send notification
            await self.send_backup_notification(backup_name, metadata['total_documents'], file_size)
            
            return zip_path
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas tworzenia kopii zapasowej: {e}")
            raise
    
    async def restore_backup(self, backup_file: str, confirm: bool = False) -> bool:
        """Restore system from backup"""
        
        if not confirm:
            logger.warning("⚠️ UWAGA: Przywracanie danych usunie wszystkie istniejące dane!")
            logger.warning("⚠️ Użyj parametru --confirm aby potwierdzić operację.")
            return False
        
        backup_path = Path(backup_file)
        if not backup_path.exists():
            logger.error(f"❌ Plik kopii zapasowej nie istnieje: {backup_file}")
            return False
        
        logger.info(f"🔄 Rozpoczynam przywracanie z kopii: {backup_file}")
        
        try:
            # Extract ZIP file
            extract_dir = BACKUP_DIR / "temp_restore"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Read metadata
            metadata_file = extract_dir / "metadata.json"
            if not metadata_file.exists():
                logger.error("❌ Brak pliku metadata.json w kopii zapasowej")
                return False
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"   📅 Data kopii: {metadata['created_at']}")
            logger.info(f"   📊 Dokumentów: {metadata['total_documents']}")
            
            # Clear existing data
            logger.info("🗑️ Usuwam istniejące dane...")
            for collection_name in self.collections:
                await db[collection_name].delete_many({})
                logger.info(f"   🗑️ Wyczyszczono: {collection_name}")
            
            # Restore each collection
            restored_count = 0
            for collection_name in metadata['collections']:
                collection_file = extract_dir / f"{collection_name}.json"
                
                if collection_file.exists():
                    with open(collection_file, 'r', encoding='utf-8') as f:
                        documents = json.load(f)
                    
                    if documents:
                        # Convert string dates back to datetime objects
                        for doc in documents:
                            for key, value in doc.items():
                                if key.endswith('_at') or key.endswith('_date'):
                                    try:
                                        if isinstance(value, str):
                                            doc[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    except:
                                        pass  # Keep original value if conversion fails
                        
                        await db[collection_name].insert_many(documents)
                        restored_count += len(documents)
                        logger.info(f"   ✅ {collection_name}: {len(documents)} dokumentów")
            
            # Cleanup
            shutil.rmtree(extract_dir)
            
            logger.info(f"✅ Przywracanie zakończone pomyślnie!")
            logger.info(f"   📊 Przywrócono: {restored_count} dokumentów")
            
            # Send notification
            await self.send_restore_notification(backup_file, restored_count)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas przywracania: {e}")
            return False
    
    async def list_backups(self) -> List[Dict]:
        """List all available backups"""
        
        backups = []
        
        for backup_file in BACKUP_DIR.glob("*.zip"):
            try:
                # Try to extract metadata
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    if 'metadata.json' in zipf.namelist():
                        metadata_content = zipf.read('metadata.json')
                        metadata = json.loads(metadata_content.decode('utf-8'))
                        
                        backups.append({
                            "filename": backup_file.name,
                            "filepath": str(backup_file),
                            "created_at": metadata.get('created_at', 'Unknown'),
                            "total_documents": metadata.get('total_documents', 0),
                            "size_mb": round(backup_file.stat().st_size / 1024 / 1024, 2),
                            "collections": metadata.get('collections', [])
                        })
            
            except Exception as e:
                logger.warning(f"⚠️ Nie można odczytać kopii zapasowej {backup_file.name}: {e}")
                
                # Add basic info even if metadata is corrupted
                backups.append({
                    "filename": backup_file.name,
                    "filepath": str(backup_file),
                    "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    "total_documents": "Unknown",
                    "size_mb": round(backup_file.stat().st_size / 1024 / 1024, 2),
                    "collections": [],
                    "status": "corrupted_metadata"
                })
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    async def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10):
        """Remove old backup files"""
        
        logger.info(f"🧹 Rozpoczynam czyszczenie starych kopii zapasowych...")
        logger.info(f"   📅 Zachowuję kopie z ostatnich {keep_days} dni")
        logger.info(f"   🔢 Zachowuję maksymalnie {keep_count} najnowszych kopii")
        
        backups = await self.list_backups()
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Keep recent backups and limit total count
        backups_to_keep = []
        backups_to_remove = []
        
        for backup in backups:
            try:
                backup_date = datetime.fromisoformat(backup['created_at'].replace('Z', '+00:00'))
                
                # Keep if within date range or in top N
                if backup_date > cutoff_date or len(backups_to_keep) < keep_count:
                    backups_to_keep.append(backup)
                else:
                    backups_to_remove.append(backup)
                    
            except Exception:
                # If date parsing fails, keep the backup to be safe
                backups_to_keep.append(backup)
        
        # Remove old backups
        removed_count = 0
        freed_space = 0
        
        for backup in backups_to_remove:
            try:
                backup_path = Path(backup['filepath'])
                if backup_path.exists():
                    freed_space += backup_path.stat().st_size
                    backup_path.unlink()
                    removed_count += 1
                    logger.info(f"   🗑️ Usunięto: {backup['filename']}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Nie można usunąć {backup['filename']}: {e}")
        
        freed_space_mb = freed_space / 1024 / 1024
        
        logger.info(f"✅ Czyszczenie zakończone!")
        logger.info(f"   🗑️ Usunięto kopii: {removed_count}")
        logger.info(f"   💾 Zwolniono miejsca: {freed_space_mb:.2f} MB")
        logger.info(f"   📦 Zachowane kopie: {len(backups_to_keep)}")
    
    async def verify_backup(self, backup_file: str) -> Dict:
        """Verify backup integrity"""
        
        logger.info(f"🔍 Weryfikuję kopię zapasową: {backup_file}")
        
        verification_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "collections": {},
            "total_documents": 0
        }
        
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                verification_result["errors"].append("Plik kopii zapasowej nie istnieje")
                return verification_result
            
            # Check if ZIP is valid
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Test ZIP integrity
                bad_files = zipf.testzip()
                if bad_files:
                    verification_result["errors"].append(f"Uszkodzone pliki w archiwum: {bad_files}")
                    return verification_result
                
                # Check metadata
                if 'metadata.json' not in zipf.namelist():
                    verification_result["errors"].append("Brak pliku metadata.json")
                    return verification_result
                
                # Read and validate metadata
                metadata_content = zipf.read('metadata.json')
                metadata = json.loads(metadata_content.decode('utf-8'))
                
                required_fields = ['created_at', 'collections', 'total_documents']
                for field in required_fields:
                    if field not in metadata:
                        verification_result["errors"].append(f"Brak wymaganego pola w metadata: {field}")
                
                # Check each collection file
                for collection_name in metadata.get('collections', []):
                    collection_file = f"{collection_name}.json"
                    
                    if collection_file not in zipf.namelist():
                        verification_result["errors"].append(f"Brak pliku kolekcji: {collection_file}")
                        continue
                    
                    try:
                        # Validate JSON structure
                        collection_content = zipf.read(collection_file)
                        collection_data = json.loads(collection_content.decode('utf-8'))
                        
                        verification_result["collections"][collection_name] = {
                            "documents": len(collection_data),
                            "valid": True
                        }
                        
                        verification_result["total_documents"] += len(collection_data)
                        
                    except json.JSONDecodeError as e:
                        verification_result["errors"].append(f"Nieprawidłowy JSON w {collection_file}: {e}")
                        verification_result["collections"][collection_name] = {
                            "documents": 0,
                            "valid": False,
                            "error": str(e)
                        }
                
                # Check if document counts match metadata
                if verification_result["total_documents"] != metadata.get('total_documents', 0):
                    verification_result["warnings"].append(
                        f"Liczba dokumentów nie zgadza się z metadata: "
                        f"znaleziono {verification_result['total_documents']}, "
                        f"oczekiwano {metadata.get('total_documents', 0)}"
                    )
                
                # If no errors, backup is valid
                verification_result["valid"] = len(verification_result["errors"]) == 0
        
        except Exception as e:
            verification_result["errors"].append(f"Błąd podczas weryfikacji: {e}")
        
        # Log results
        if verification_result["valid"]:
            logger.info("✅ Kopia zapasowa jest prawidłowa")
            logger.info(f"   📊 Dokumentów: {verification_result['total_documents']}")
            logger.info(f"   📁 Kolekcji: {len(verification_result['collections'])}")
        else:
            logger.error("❌ Kopia zapasowa zawiera błędy:")
            for error in verification_result["errors"]:
                logger.error(f"   - {error}")
        
        if verification_result["warnings"]:
            for warning in verification_result["warnings"]:
                logger.warning(f"⚠️ {warning}")
        
        return verification_result
    
    async def send_backup_notification(self, backup_name: str, doc_count: int, size_mb: float):
        """Send email notification about successful backup"""
        
        if not EMAIL_USER or not ADMIN_EMAILS or not ADMIN_EMAILS[0]:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = ', '.join(ADMIN_EMAILS)
            msg['Subject'] = f"TV Panel - Kopia zapasowa utworzona: {backup_name}"
            
            body = f"""
Kopia zapasowa systemu TV Panel została pomyślnie utworzona.

📋 Szczegóły:
• Nazwa: {backup_name}
• Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
• Dokumentów: {doc_count}
• Rozmiar: {size_mb:.2f} MB

System TV Panel
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, ADMIN_EMAILS, text)
            server.quit()
            
            logger.info("📧 Powiadomienie email wysłane")
            
        except Exception as e:
            logger.warning(f"⚠️ Nie można wysłać powiadomienia email: {e}")
    
    async def send_restore_notification(self, backup_file: str, doc_count: int):
        """Send email notification about restore operation"""
        
        if not EMAIL_USER or not ADMIN_EMAILS or not ADMIN_EMAILS[0]:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = ', '.join(ADMIN_EMAILS)
            msg['Subject'] = f"TV Panel - Dane przywrócone z kopii zapasowej"
            
            body = f"""
Dane systemu TV Panel zostały przywrócone z kopii zapasowej.

📋 Szczegóły:
• Plik kopii: {Path(backup_file).name}
• Data przywrócenia: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
• Przywróconych dokumentów: {doc_count}

⚠️ UWAGA: Wszystkie poprzednie dane zostały zastąpione.

System TV Panel
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, ADMIN_EMAILS, text)
            server.quit()
            
            logger.info("📧 Powiadomienie o przywróceniu wysłane")
            
        except Exception as e:
            logger.warning(f"⚠️ Nie można wysłać powiadomienia email: {e}")

# Scheduler for automatic backups
class BackupScheduler:
    
    def __init__(self, backup_manager: BackupRestoreManager):
        self.backup_manager = backup_manager
    
    def schedule_daily_backup(self, time_str: str = "02:00"):
        """Schedule daily backup at specified time"""
        schedule.every().day.at(time_str).do(self.run_scheduled_backup)
        logger.info(f"📅 Zaplanowano codzienne kopie zapasowe na {time_str}")
    
    def schedule_weekly_cleanup(self, day: str = "sunday", time_str: str = "03:00"):
        """Schedule weekly cleanup of old backups"""
        getattr(schedule.every(), day).at(time_str).do(self.run_scheduled_cleanup)
        logger.info(f"🧹 Zaplanowano tygodniowe czyszczenie na {day} o {time_str}")
    
    def run_scheduled_backup(self):
        """Run scheduled backup"""
        try:
            asyncio.run(self.backup_manager.create_backup())
        except Exception as e:
            logger.error(f"❌ Błąd podczas zaplanowanej kopii zapasowej: {e}")
    
    def run_scheduled_cleanup(self):
        """Run scheduled cleanup"""
        try:
            asyncio.run(self.backup_manager.cleanup_old_backups())
        except Exception as e:
            logger.error(f"❌ Błąd podczas zaplanowanego czyszczenia: {e}")
    
    def start_scheduler(self):
        """Start the backup scheduler"""
        logger.info("🔄 Uruchamiam scheduler kopii zapasowych...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# CLI Interface
async def main():
    parser = argparse.ArgumentParser(description="TV Panel Backup & Restore System")
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup', 'verify', 'scheduler'])
    parser.add_argument('--file', '-f', help='Backup file path (for restore/verify)')
    parser.add_argument('--name', '-n', help='Backup name (for backup)')
    parser.add_argument('--confirm', action='store_true', help='Confirm destructive operations')
    parser.add_argument('--keep-days', type=int, default=30, help='Days to keep backups (for cleanup)')
    parser.add_argument('--keep-count', type=int, default=10, help='Number of backups to keep (for cleanup)')
    
    args = parser.parse_args()
    
    backup_manager = BackupRestoreManager()
    
    if args.action == 'backup':
        await backup_manager.create_backup(args.name)
    
    elif args.action == 'restore':
        if not args.file:
            logger.error("❌ Musisz podać plik kopii zapasowej (--file)")
            return
        await backup_manager.restore_backup(args.file, args.confirm)
    
    elif args.action == 'list':
        backups = await backup_manager.list_backups()
        
        if not backups:
            logger.info("📭 Brak kopii zapasowych")
            return
        
        logger.info(f"📦 Znalezione kopie zapasowe ({len(backups)}):")
        logger.info("-" * 80)
        
        for backup in backups:
            logger.info(f"📁 {backup['filename']}")
            logger.info(f"   📅 Utworzono: {backup['created_at']}")
            logger.info(f"   📊 Dokumentów: {backup['total_documents']}")
            logger.info(f"   💾 Rozmiar: {backup['size_mb']} MB")
            logger.info(f"   📁 Ścieżka: {backup['filepath']}")
            if backup.get('status'):
                logger.info(f"   ⚠️ Status: {backup['status']}")
            logger.info("")
    
    elif args.action == 'cleanup':
        await backup_manager.cleanup_old_backups(args.keep_days, args.keep_count)
    
    elif args.action == 'verify':
        if not args.file:
            logger.error("❌ Musisz podać plik kopii zapasowej (--file)")
            return
        await backup_manager.verify_backup(args.file)
    
    elif args.action == 'scheduler':
        scheduler = BackupScheduler(backup_manager)
        scheduler.schedule_daily_backup("02:00")  # Daily at 2 AM
        scheduler.schedule_weekly_cleanup("sunday", "03:00")  # Sunday at 3 AM
        
        logger.info("⚡ Scheduler uruchomiony. Naciśnij Ctrl+C aby zatrzymać.")
        try:
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler zatrzymany")

if __name__ == "__main__":
    asyncio.run(main())