import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# DEĞİŞKENLERİ ZORLA OKU - HATA VARSA DUR
try:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    WEBHOOK_URL = os.environ["WEBHOOK_URL"]
    logger.info(f"Token bulundu: {BOT_TOKEN[:8]}...")
    logger.info(f"Webhook: {WEBHOOK_URL}")
except KeyError as e:
    logger.error(f"EKSIK DEGISKEN: {e}")
    logger.error("Railway Variables'a BOT_TOKEN ve WEBHOOK_URL ekle!")
    sys.exit(1)

PORT = int(os.environ.get("PORT", "8080"))
DATA = {"users": {}, "msgs": 0}

app = Flask(__name__)

@app.route('/')
def home():
    return "XenithNet Online"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, BOT.bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(BOT.process_update(update))
        loop.close()
    except Exception as e:
        logger.error(f"Webhook hata: {e}")
    return "OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    uid = str(u.id)
    if uid not in DATA["users"]:
        DATA["users"][uid] = {"name": u.first_name, "bal": 0, "rank": "Vatandas"}
    k = DATA["users"][uid]
    txt = f"⚡ *XENITHNET*\n\n🏰 {k['name']}\n💰 {k['bal']} XNC\n🎖 {k['rank']}\n\n/hizmetler - Hizmetler"
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Hizmetler", callback_data="hizmetler")]])
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=btn)

async def hizmetler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮 Ghost Gaming\n💻 Code Arsenal\n🛡 Phantom Shield\n📱 App Forge")

async def buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "hizmetler":
        await q.edit_message_text("🎮 Ghost Gaming\n💻 Code Arsenal\n🛡 Phantom Shield\n📱 App Forge")

BOT = None

async def main():
    global BOT
    BOT = Application.builder().token(BOT_TOKEN).build()
    BOT.add_handler(CommandHandler("start", start))
    BOT.add_handler(CommandHandler("hizmetler", hizmetler))
    BOT.add_handler(CallbackQueryHandler(buton))
    
    webhook_url = f"{WEBHOOK_URL}/webhook"
    await BOT.bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Webhook kuruldu: {webhook_url}")
    
    cmds = [BotCommand("start", "Baslat"), BotCommand("hizmetler", "Hizmetler")]
    await BOT.bot.set_my_commands(cmds)
    logger.info("✅ BOT HAZIR! Telegram'da /start yaz!")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    logger.info(f"🌐 Port: {PORT}")
    app.run(host="0.0.0.0", port=PORT)
