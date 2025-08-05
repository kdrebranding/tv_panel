#!/usr/bin/env python3
"""
TV Panel Telegram Bot
Wysyła automatyczne powiadomienia o wygasających licencjach i zarządza komunikacją z klientami.
"""

import asyncio
import os
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json
from motor.motor_asyncio import AsyncIOMotorClient
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
ADMIN_CHAT_IDS = [int(x.strip()) for x in os.getenv('ADMIN_CHAT_IDS', '').split(',') if x.strip()]
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TVPanelBot:
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("clients", self.clients_command))
        self.application.add_handler(CommandHandler("expiring", self.expiring_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context):
        """Handle /start command"""
        user_id = update.effective_user.id
        welcome_text = f"""
🤖 **Witaj w TV Panel Bot!**

📺 Jestem botem zarządzającym systemem IPTV.

**Dostępne komendy:**
/status - Status systemu
/clients - Lista klientów  
/expiring - Wygasające licencje
/stats - Statystyki
/help - Pomoc

👤 Twój ID: `{user_id}`
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 Statystyki", callback_data="stats")],
            [InlineKeyboardButton("⚠️ Wygasające", callback_data="expiring")],
            [InlineKeyboardButton("👥 Klienci", callback_data="clients")],
            [InlineKeyboardButton("❓ Pomoc", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context):
        """Handle /status command"""
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Brak uprawnień administracyjnych.")
            return
        
        try:
            # Get system stats
            total_clients = await db.clients.count_documents({})
            active_count = await db.clients.count_documents({"status": "active"})
            expiring_count = await db.clients.count_documents({"status": "expiring_soon"})
            expired_count = await db.clients.count_documents({"status": "expired"})
            
            status_text = f"""
🟢 **Status Systemu TV Panel**

📊 **Statystyki:**
• Wszyscy klienci: {total_clients}
• Aktywni: {active_count} ✅
• Wygasające wkrótce: {expiring_count} ⚠️
• Wygasłe: {expired_count} ❌

⏰ Ostatnie sprawdzenie: {datetime.now().strftime('%H:%M:%S')}
"""
            
            await update.message.reply_text(status_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text("❌ Błąd podczas pobierania statusu systemu.")
    
    async def clients_command(self, update: Update, context):
        """Handle /clients command"""
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Brak uprawnień administracyjnych.")
            return
        
        try:
            # Get recent clients
            clients = await db.clients.find().sort("created_at", -1).limit(10).to_list(10)
            
            if not clients:
                await update.message.reply_text("📭 Brak klientów w systemie.")
                return
            
            clients_text = "👥 **Ostatnio dodani klienci:**\n\n"
            
            for client in clients:
                status_emoji = self.get_status_emoji(client.get('status', 'active'))
                expires_date = client.get('expires_date')
                expires_str = expires_date.strftime('%d.%m.%Y') if expires_date else 'Brak'
                
                clients_text += f"{status_emoji} **{client.get('name', 'Bez nazwy')}**\n"
                clients_text += f"   📅 Wygasa: {expires_str}\n"
                clients_text += f"   📱 Panel: {client.get('panel_name', 'Brak')}\n\n"
            
            await update.message.reply_text(clients_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in clients command: {e}")
            await update.message.reply_text("❌ Błąd podczas pobierania listy klientów.")
    
    async def expiring_command(self, update: Update, context):
        """Handle /expiring command"""
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Brak uprawnień administracyjnych.")
            return
        
        try:
            today = datetime.now().date()
            week_from_now = today + timedelta(days=7)
            
            # Get expiring clients
            expiring_clients = await db.clients.find({
                "expires_date": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lte": datetime.combine(week_from_now, datetime.max.time())
                }
            }).sort("expires_date", 1).to_list(20)
            
            if not expiring_clients:
                await update.message.reply_text("✅ Brak wygasających licencji w najbliższym tygodniu!")
                return
            
            expiring_text = "⚠️ **Wygasające licencje (7 dni):**\n\n"
            
            for client in expiring_clients:
                expires_date = client.get('expires_date')
                if expires_date:
                    days_left = (expires_date.date() - today).days
                    urgency_emoji = "🔴" if days_left <= 1 else "🟡" if days_left <= 3 else "🟠"
                    
                    expiring_text += f"{urgency_emoji} **{client.get('name', 'Bez nazwy')}**\n"
                    expiring_text += f"   ⏰ Za {days_left} dni ({expires_date.strftime('%d.%m')})\n"
                    expiring_text += f"   📞 {client.get('contact_value', 'Brak kontaktu')}\n\n"
            
            # Add action buttons
            keyboard = [
                [InlineKeyboardButton("📧 Wyślij przypomnienia", callback_data="send_reminders")],
                [InlineKeyboardButton("🔄 Odśwież listę", callback_data="expiring")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(expiring_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in expiring command: {e}")
            await update.message.reply_text("❌ Błąd podczas pobierania wygasających licencji.")
    
    async def stats_command(self, update: Update, context):
        """Handle /stats command with detailed analytics"""
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Brak uprawnień administracyjnych.")
            return
        
        try:
            # Basic stats
            total_clients = await db.clients.count_documents({})
            active_count = await db.clients.count_documents({"status": "active"})
            expiring_count = await db.clients.count_documents({"status": "expiring_soon"})
            expired_count = await db.clients.count_documents({"status": "expired"})
            
            # Panel stats
            panels = await db.panels.find().to_list(None)
            panel_stats = {}
            for panel in panels:
                count = await db.clients.count_documents({"panel_id": panel["id"]})
                panel_stats[panel["name"]] = count
            
            # App stats
            apps = await db.apps.find().to_list(None)
            app_stats = {}
            for app in apps:
                count = await db.clients.count_documents({"app_id": app["id"]})
                app_stats[app["name"]] = count
            
            # This month's new clients
            first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_this_month = await db.clients.count_documents({
                "created_at": {"$gte": first_day_month}
            })
            
            stats_text = f"""
📊 **Szczegółowe Statystyki TV Panel**

**🔢 Podstawowe:**
• Wszyscy klienci: {total_clients}
• Aktywni: {active_count} ✅
• Wygasające wkrótce: {expiring_count} ⚠️
• Wygasłe: {expired_count} ❌
• Nowi w tym miesiącu: {new_this_month} 🆕

**📺 Top Panele:**
"""
            
            # Add panel stats
            for panel_name, count in sorted(panel_stats.items(), key=lambda x: x[1], reverse=True)[:3]:
                stats_text += f"• {panel_name}: {count}\n"
            
            stats_text += "\n**📱 Top Aplikacje:**\n"
            
            # Add app stats
            for app_name, count in sorted(app_stats.items(), key=lambda x: x[1], reverse=True)[:3]:
                stats_text += f"• {app_name}: {count}\n"
            
            stats_text += f"\n⏰ Wygenerowano: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await update.message.reply_text("❌ Błąd podczas generowania statystyk.")
    
    async def help_command(self, update: Update, context):
        """Handle /help command"""
        help_text = """
🤖 **TV Panel Bot - Pomoc**

**👨‍💼 Komendy administratora:**
/start - Menu główne
/status - Status systemu
/clients - Lista klientów
/expiring - Wygasające licencje
/stats - Szczegółowe statystyki
/help - Ta pomoc

**🔔 Automatyczne funkcje:**
• Codzienne powiadomienia o wygasających licencjach
• Alerty o nowych klientach
• Raporty tygodniowe
• Monitoring systemu

**📞 Kontakt:**
W razie problemów skontaktuj się z administratorem systemu.

🔧 Bot działa 24/7 i monitoruje system TV Panel.
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "stats":
            await self.stats_command(update, context)
        elif query.data == "expiring":
            await self.expiring_command(update, context)
        elif query.data == "clients":
            await self.clients_command(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "send_reminders":
            await self.send_expiry_reminders(query)
    
    async def handle_message(self, update: Update, context):
        """Handle text messages"""
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Brak uprawnień. Użyj /start aby rozpocząć.")
            return
        
        text = update.message.text.lower()
        
        if "status" in text or "statystyki" in text:
            await self.stats_command(update, context)
        elif "klienci" in text or "clients" in text:
            await self.clients_command(update, context)
        elif "wygasające" in text or "expiring" in text:
            await self.expiring_command(update, context)
        else:
            await update.message.reply_text("❓ Nie rozumiem. Użyj /help aby zobaczyć dostępne komendy.")
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in ADMIN_CHAT_IDS or not ADMIN_CHAT_IDS  # If no admins set, allow all
    
    def get_status_emoji(self, status: str) -> str:
        """Get emoji for client status"""
        status_emojis = {
            "active": "✅",
            "expiring_soon": "⚠️",
            "expired": "❌",
            "suspended": "⏸️"
        }
        return status_emojis.get(status, "❓")
    
    async def send_expiry_reminders(self, query):
        """Send reminders to expiring clients"""
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # Get clients expiring soon
            expiring_clients = await db.clients.find({
                "expires_date": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lte": datetime.combine(tomorrow, datetime.max.time())
                },
                "telegram_id": {"$exists": True, "$ne": None}
            }).to_list(50)
            
            sent_count = 0
            for client in expiring_clients:
                if client.get('telegram_id'):
                    try:
                        reminder_text = f"""
🔔 **Przypomnienie o wygasającej licencji**

Witaj {client.get('name', 'Kliencie')}!

⚠️ Twoja licencja IPTV wygasa już jutro ({client['expires_date'].strftime('%d.%m.%Y')}).

🔄 Aby kontynuować oglądanie, skontaktuj się z nami w celu przedłużenia subskrypcji.

📞 Kontakt: [Twój kontakt]
"""
                        
                        await self.bot.send_message(
                            chat_id=client['telegram_id'],
                            text=reminder_text,
                            parse_mode='Markdown'
                        )
                        sent_count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to send reminder to {client.get('name')}: {e}")
            
            result_text = f"📧 Wysłano {sent_count} przypomnień do klientów."
            await query.edit_message_text(result_text)
            
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")
            await query.edit_message_text("❌ Błąd podczas wysyłania przypomnień.")
    
    async def daily_notifications(self):
        """Send daily notifications to admins"""
        try:
            if not ADMIN_CHAT_IDS:
                return
            
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # Get expiring today and tomorrow
            expiring_today = await db.clients.count_documents({
                "expires_date": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lte": datetime.combine(today, datetime.max.time())
                }
            })
            
            expiring_tomorrow = await db.clients.count_documents({
                "expires_date": {
                    "$gte": datetime.combine(tomorrow, datetime.min.time()),
                    "$lte": datetime.combine(tomorrow, datetime.max.time())
                }
            })
            
            if expiring_today > 0 or expiring_tomorrow > 0:
                notification_text = f"""
🌅 **Codzienny Raport TV Panel**
📅 {today.strftime('%d.%m.%Y')}

⚠️ **Licencje wygasające:**
• Dzisiaj: {expiring_today}
• Jutro: {expiring_tomorrow}

🔗 Sprawdź szczegóły: /expiring
"""
                
                for admin_id in ADMIN_CHAT_IDS:
                    try:
                        await self.bot.send_message(
                            chat_id=admin_id,
                            text=notification_text,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Failed to send daily notification to admin {admin_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in daily notifications: {e}")
    
    async def weekly_report(self):
        """Send weekly report to admins"""
        try:
            if not ADMIN_CHAT_IDS:
                return
            
            # Get stats for the past week
            week_ago = datetime.now() - timedelta(days=7)
            
            new_clients_week = await db.clients.count_documents({
                "created_at": {"$gte": week_ago}
            })
            
            expired_this_week = await db.clients.count_documents({
                "expires_date": {
                    "$gte": week_ago,
                    "$lte": datetime.now()
                }
            })
            
            total_clients = await db.clients.count_documents({})
            active_clients = await db.clients.count_documents({"status": "active"})
            
            report_text = f"""
📊 **Tygodniowy Raport TV Panel**
📅 {(datetime.now() - timedelta(days=7)).strftime('%d.%m')} - {datetime.now().strftime('%d.%m.%Y')}

**📈 Statystyki tygodnia:**
• Nowi klienci: {new_clients_week}
• Wygasłe licencje: {expired_this_week}
• Łączna liczba klientów: {total_clients}
• Aktywni klienci: {active_clients}

**📊 Wskaźnik retencji:** {(active_clients/total_clients*100):.1f}%

🔍 Sprawdź szczegóły: /stats
"""
            
            for admin_id in ADMIN_CHAT_IDS:
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=report_text,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Failed to send weekly report to admin {admin_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in weekly report: {e}")
    
    async def start_scheduler(self):
        """Start scheduled tasks"""
        while True:
            try:
                now = datetime.now()
                
                # Daily notifications at 9:00 AM
                if now.hour == 9 and now.minute == 0:
                    await self.daily_notifications()
                
                # Weekly report on Monday at 10:00 AM
                if now.weekday() == 0 and now.hour == 10 and now.minute == 0:
                    await self.weekly_report()
                
                # Wait 60 seconds before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)
    
    def run(self):
        """Run the bot"""
        logger.info("Starting TV Panel Telegram Bot...")
        
        # Start scheduler in background
        asyncio.create_task(self.start_scheduler())
        
        # Start the bot
        self.application.run_polling()

# Initialize and run bot
if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables!")
        exit(1)
    
    bot = TVPanelBot(TELEGRAM_BOT_TOKEN)
    bot.run()