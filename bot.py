import os
import sys
import logging
import asyncio
from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# DEĞİŞKENLERİ YUMUŞAK OKU
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    logger.error("BOT_TOKEN bulunamadi! Render Environment Variables'a ekle.")
    sys.exit(1)

if not WEBHOOK_URL:
    logger.error("WEBHOOK_URL bulunamadi!")
    sys.exit(1)

logger.info(f"Token baslangic: {BOT_TOKEN[:8]}...")
logger.info(f"Webhook URL: {WEBHOOK_URL}")
logger.info(f"Port: {PORT}")

app = Flask(__name__)

@app.route('/')
def home():
    return "XenithNet Bot Running"

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
    user = update.effective_user
    await update.message.reply_text(
        f"⚡ *XENITHNET IMPARATORLUGU*\n\n🏰 Hos geldin *{user.first_name}*!\n\n/hizmetler - Hizmetler",
        parse_mode=ParseMode.MARKDOWN
    )

async def hizmetler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 *HIZMETLER*\n\n🎮 Ghost Gaming\n💻 Code Arsenal\n🛡 Phantom Shield\n📱 App Forge",
        parse_mode=ParseMode.MARKDOWN
    )

BOT = None

async def main():
    global BOT
    BOT = Application.builder().token(BOT_TOKEN).build()
    BOT.add_handler(CommandHandler("start", start))
    BOT.add_handler(CommandHandler("hizmetler", hizmetler))
    
    await BOT.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    logger.info("✅ Webhook kuruldu!")
    
    await BOT.bot.set_my_commands([
        BotCommand("start", "Imparatorluga katil"),
        BotCommand("hizmetler", "Hizmetler"),
    ])
    logger.info("✅ BOT HAZIR! Telegramda /start yaz!")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    logger.info(f"🌐 Sunucu baslatiliyor... Port: {PORT}")
    app.run(host="0.0.0.0", port=PORT)
