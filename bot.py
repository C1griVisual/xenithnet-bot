import os
import json
import logging
import asyncio
from datetime import datetime
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BU KISIM ÖNEMLİ: Değişkenleri DOĞRUDAN al
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PORT = int(os.environ.get("PORT", 8080))

veriler = {"kullanicilar": {}, "mesaj_sayisi": 0}

app = Flask(__name__)

@app.route('/')
def ana_sayfa():
    return "XenithNet Bot Running"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), telegram_bot.bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_bot.process_update(update))
        loop.close()
    except Exception as e:
        logger.error(f"Hata: {e}")
    return "OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kullanici = update.effective_user
    uid = str(kullanici.id)
    
    if uid not in veriler["kullanicilar"]:
        veriler["kullanicilar"][uid] = {
            "ad": kullanici.first_name,
            "kullanici_adi": kullanici.username or "yok",
            "rutbe": "Vatandas",
            "bakiye": 0,
            "katilim": datetime.now().isoformat()
        }
    
    k = veriler["kullanicilar"][uid]
    mesaj = f"⚡ *XENITHNET IMPARATORLUGU*\n\n🏰 Hos geldin *{k['ad']}*!\n🎖 Rutbe: *{k['rutbe']}*\n💰 Bakiye: *{k['bakiye']} XNC*\n\n/hizmetler - Hizmetler\n/bakiye - Bakiye"
    
    tuslar = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Hizmetler", callback_data="hizmetler"),
         InlineKeyboardButton("💰 Bakiye", callback_data="bakiye")],
        [InlineKeyboardButton("🏰 Hakkinda", callback_data="hakkinda")]
    ])
    veriler["mesaj_sayisi"] += 1
    await update.message.reply_text(mesaj, parse_mode=ParseMode.MARKDOWN, reply_markup=tuslar)

async def hizmetler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = """🛒 *HIZMETLER*\n\n🎮 Ghost Gaming\n💻 Code Arsenal\n🛡 Phantom Shield\n📱 App Forge"""
    await update.message.reply_text(mesaj, parse_mode=ParseMode.MARKDOWN)

async def bakiye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    k = veriler["kullanicilar"].get(uid)
    if k:
        mesaj = f"💰 Bakiye: *{k['bakiye']} XNC*\n🎖 Rutbe: *{k['rutbe']}*"
    else:
        mesaj = "/start ile kaydol"
    await update.message.reply_text(mesaj, parse_mode=ParseMode.MARKDOWN)

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = f"📊 Uye: {len(veriler['kullanicilar'])}\n💬 Mesaj: {veriler['mesaj_sayisi']}\n🟢 Aktif"
    await update.message.reply_text(mesaj)

async def buton_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorgu = update.callback_query
    await sorgu.answer()
    veri = sorgu.data
    
    if veri == "hizmetler":
        await hizmetler(update, context)
    elif veri == "bakiye":
        await bakiye(update, context)
    elif veri == "hakkinda":
        mesaj = "🏰 XenithNet Imparatorlugu\n⚡ Dijital cag"
        tus = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="geri")]])
        await sorgu.edit_message_text(mesaj, reply_markup=tus)
    elif veri == "geri":
        uid = str(sorgu.from_user.id)
        k = veriler["kullanicilar"].get(uid, {"rutbe": "Vatandas", "bakiye": 0})
        mesaj = f"🏰 Ana Menu\n🎖 {k['rutbe']}\n💰 {k['bakiye']} XNC"
        tus = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Hizmetler", callback_data="hizmetler"),
             InlineKeyboardButton("💰 Bakiye", callback_data="bakiye")],
            [InlineKeyboardButton("🏰 Hakkinda", callback_data="hakkinda")]
        ])
        await sorgu.edit_message_text(mesaj, reply_markup=tus)

telegram_bot = None

async def main():
    global telegram_bot
    logger.info(f"Token: {BOT_TOKEN[:10]}... Webhook: {WEBHOOK_URL}")
    
    telegram_bot = Application.builder().token(BOT_TOKEN).build()
    telegram_bot.add_handler(CommandHandler("start", start))
    telegram_bot.add_handler(CommandHandler("hizmetler", hizmetler))
    telegram_bot.add_handler(CommandHandler("bakiye", bakiye))
    telegram_bot.add_handler(CommandHandler("istatistik", istatistik))
    telegram_bot.add_handler(CallbackQueryHandler(buton_isleyici))
    
    await telegram_bot.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    
    commands = [
        BotCommand("start", "Imparatorluga katil"),
        BotCommand("hizmetler", "Hizmetler"),
        BotCommand("bakiye", "Bakiye"),
        BotCommand("istatistik", "Istatistik"),
    ]
    await telegram_bot.bot.set_my_commands(commands)
    logger.info("✅ Bot hazir!")

if __name__ == "__main__":
    logger.info("Baslatiliyor...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    
    logger.info(f"Web sunucu: Port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
