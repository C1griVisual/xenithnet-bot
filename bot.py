import os
import json
import logging
import asyncio
from datetime import datetime
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Loglama
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Çevre değişkenleri
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))

# Veri dosyası
DATA_FILE = "/tmp/xenithnet_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}, "messages": 0}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

data = load_data()

# Flask uygulaması
app = Flask(__name__)

@app.route('/')
def home():
    return "XenithNet Bot Running"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_app.process_update(update))
        loop.close()
    except Exception as e:
        logger.error(f"Hata: {e}")
    return "OK"

# Bot komutları
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        uid = str(user.id)
        
        if uid not in data["users"]:
            data["users"][uid] = {
                "name": user.first_name,
                "username": user.username or "yok",
                "rank": "Vatandas",
                "balance": 0,
                "joined": datetime.now().strftime("%d.%m.%Y")
            }
            save_data(data)
        
        u = data["users"][uid]
        text = f"⚡ *XENITHNET IMPARATORLUGU*\n\n🏰 Hos geldin *{u['name']}*!\n🎖 Rutbe: *{u['rank']}*\n💰 Bakiye: *{u['balance']} XNC*\n\n/hizmetler - Hizmetler\n/bakiye - Bakiye"
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Hizmetler", callback_data="services"),
             InlineKeyboardButton("💰 Bakiye", callback_data="balance")]
        ])
        
        data["messages"] += 1
        save_data(data)
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=buttons)
    except Exception as e:
        logger.error(f"Start hatasi: {e}")

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🛒 *XENITHNET HIZMETLERI*

🎮 *Ghost Gaming*
• Basic - 500 XNC
• Pro - 2,500 XNC
• Ultimate - 5,000 XNC

💻 *Code Arsenal*
• Script - 1,000 XNC
• Exploit - 15,000 XNC

🛡 *Phantom Shield*
• Basic - 2,500 XNC
• Enterprise - 25,000 XNC

📱 *App Forge*
• Custom - 5,000 XNC
• Multi - 15,000 XNC
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    u = data["users"].get(uid)
    if u:
        text = f"💰 Bakiye: *{u['balance']} XNC*\n🎖 Rutbe: *{u['rank']}*"
    else:
        text = "/start ile kaydol"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"📊 Uye: {len(data['users'])}\n💬 Mesaj: {data['messages']}\n🟢 Aktif"
    await update.message.reply_text(text)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cmd = query.data
    
    if cmd == "services":
        await services(update, context)
    elif cmd == "balance":
        await balance(update, context)

# Bot başlatma
bot_app = None

async def main():
    global bot_app
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN bulunamadi!")
        return
    
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("hizmetler", services))
    bot_app.add_handler(CommandHandler("bakiye", balance))
    bot_app.add_handler(CommandHandler("istatistik", stats))
    bot_app.add_handler(CallbackQueryHandler(button_handler))
    
    if WEBHOOK_URL:
        await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        logger.info(f"Webhook kuruldu: {WEBHOOK_URL}/webhook")
    
    commands = [
        BotCommand("start", "Imparatorluga katil"),
        BotCommand("hizmetler", "Hizmetler"),
        BotCommand("bakiye", "Bakiye"),
        BotCommand("istatistik", "Istatistik"),
    ]
    await bot_app.bot.set_my_commands(commands)
    logger.info("Bot hazir!")

if __name__ == "__main__":
    logger.info("XenithNet baslatiliyor...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    
    logger.info(f"Web sunucu baslatiliyor (Port: {PORT})")
    app.run(host="0.0.0.0", port=PORT)
