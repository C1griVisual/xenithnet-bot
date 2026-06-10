# XenithNet 7/24 Telegram Bot
import os, json, logging, asyncio
from datetime import datetime
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('XenithNet')

BOT_TOKEN = os.environ.get("BOT_TOKEN", "TOKENINI_BURAYA_YAZ")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://senin-bot.railway.app")
PORT = int(os.environ.get("PORT", 8080))

veriler = {"kullanicilar": {}, "mesaj_sayisi": 0}

def kaydet():
    try:
        with open("veri.json", "w") as f:
            json.dump(veriler, f)
    except:
        pass

def yukle():
    global veriler
    try:
        with open("veri.json", "r") as f:
            veriler = json.load(f)
    except:
        pass

yukle()

app = Flask(__name__)

@app.route('/')
def ana_sayfa():
    return """<html><head><title>XenithNet</title></head>
    <body style="background:#0a0a0a;color:#00ff88;font-family:monospace;text-align:center;padding-top:100px;">
    <h1>⚡ XENITHNET BOT CALISIYOR</h1><p>7/24 Aktif</p></body></html>"""

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        asyncio.run(telegram_bot.process_update(
            Update.de_json(request.get_json(force=True), telegram_bot.bot)))
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
        kaydet()
    
    k = veriler["kullanicilar"][uid]
    mesaj = f"""
⚡ *XENITHNET IMPARATORLUGU* ⚡

🏰 Hos geldin *{k['ad']}*!
🎖 Rutbe: *{k['rutbe']}*
💰 Bakiye: *{k['bakiye']} XNC*
🌐 Bot 7/24 Bulutta Calisiyor!

🛒 /hizmetler - Hizmetleri gor
💰 /bakiye - Bakiye sorgula
📊 /istatistik - Bot durumu
"""
    tuslar = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Hizmetler", callback_data="hizmetler"),
         InlineKeyboardButton("💰 Bakiye", callback_data="bakiye")],
        [InlineKeyboardButton("🏰 Hakkinda", callback_data="hakkinda")]
    ])
    veriler["mesaj_sayisi"] += 1
    kaydet()
    await update.message.reply_text(mesaj, parse_mode=ParseMode.MARKDOWN, reply_markup=tuslar)

async def hizmetler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    veriler["mesaj_sayisi"] += 1
    kaydet()
    mesaj = """
🛒 *XENITHNET HIZMETLERI*

🎮 *Ghost Gaming*
• ESP/Aimbot Basic - 500 XNC
• Pro Suite - 2,500 XNC
• Ultimate Pack - 5,000 XNC

💻 *Code Arsenal*
• Basic Script - 1,000 XNC
• Exploit Kit - 15,000 XNC

🛡 *Phantom Shield*
• DDoS Koruma - 2,500 XNC
• Enterprise - 25,000 XNC

📱 *App Forge*
• Custom App - 5,000 XNC
• Multi Platform - 15,000 XNC

📞 Siparis: @XenithNetSupport
"""
    await update.message.reply_text(mesaj, parse_mode=ParseMode.MARKDOWN)

async def bakiye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    veriler["mesaj_sayisi"] += 1
    kaydet()
    uid = str(update.effective_user.id)
    k = veriler["kullanicilar"].get(uid, None)
    if k:
        mesaj = f"💰 Bakiye: *{k['bakiye']} XNC*\n🎖 Rutbe: *{k['rutbe']}*"
    else:
        mesaj = "❌ /start ile kaydol"
    await update.message.reply_text(mesaj, parse_mode=ParseMode.MARKDOWN)

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = f"""
📊 *BOT ISTATISTIKLERI*

👥 Uye: {len(veriler['kullanicilar'])}
💬 Mesaj: {veriler['mesaj_sayisi']}
🟢 Durum: AKTIF
🌐 7/24 Calisiyor
"""
    await update.message.reply_text(mesaj, parse_mode=ParseMode.MARKDOWN)

async def buton_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sorgu = update.callback_query
    await sorgu.answer()
    veri = sorgu.data
    
    if veri == "hizmetler":
        await hizmetler(update, context)
    elif veri == "bakiye":
        await bakiye(update, context)
    elif veri == "hakkinda":
        mesaj = "🏰 *XENITHNET IMPARATORLUGU*\n\n⚡ Dijital cagin golgelerinde\n👥 1,337+ uye\n🔐 Quantum-Safe\n🌐 7/24 Bulutta"
        tus = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="geri")]])
        await sorgu.edit_message_text(mesaj, parse_mode=ParseMode.MARKDOWN, reply_markup=tus)
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

async def botu_baslat():
    global telegram_bot
    telegram_bot = Application.builder().token(BOT_TOKEN).build()
    telegram_bot.add_handler(CommandHandler("start", start))
    telegram_bot.add_handler(CommandHandler("hizmetler", hizmetler))
    telegram_bot.add_handler(CommandHandler("bakiye", bakiye))
    telegram_bot.add_handler(CommandHandler("istatistik", istatistik))
    telegram_bot.add_handler(CallbackQueryHandler(buton_isleyici))
    
    await telegram_bot.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    komutlar = [
        BotCommand("start", "Imparatorluga katil"),
        BotCommand("hizmetler", "Hizmetleri gor"),
        BotCommand("bakiye", "Bakiye sorgula"),
        BotCommand("istatistik", "Bot durumu"),
    ]
    await telegram_bot.bot.set_my_commands(komutlar)
    logger.info("✅ Bot baslatildi!")

if __name__ == "__main__":
    print("⚡ XenithNet Bot Baslatiliyor...")
    asyncio.run(botu_baslat())
    print(f"🌐 Web sunucu: Port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
