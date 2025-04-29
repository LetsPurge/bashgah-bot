import os
import logging
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

# --- تنظیمات از متغیرهای محیطی ---
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثل https://your-app.onrender.com

TIMEZONE = pytz.timezone("Asia/Tehran")
button_pressed = False

# --- ساختن اپ Flask ---
flask_app = Flask(__name__)
bot = Bot(token=TOKEN)
scheduler = BackgroundScheduler(timezone="Asia/Tehran")

# --- دکمه ورود ---
def get_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("به والله وارد شدم 📿", callback_data="entered")]]
    )

# --- ارسال پیام ساعت ۰۰:۰۰ ---
def send_midnight_message():
    global button_pressed
    button_pressed = False
    bot.send_message(chat_id=CHAT_ID, text="❓ وارد سایت شدی؟", reply_markup=get_keyboard())

# --- یادآوری ساعت ۲۱:۰۰ ---
def send_reminder():
    if not button_pressed:
        bot.send_message(chat_id=CHAT_ID, text="⏰ دِ بجنب دِ!")

# --- مدیریت زدن دکمه ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global button_pressed
    query = update.callback_query
    await query.answer("🤡 باشه باشه، باور کردیم که وارد شدی")
    await query.message.delete()

    weekday = datetime.now(TIMEZONE).weekday()
    if weekday in [5, 0, 2, 4]:  # شنبه، دوشنبه، چهارشنبه، جمعه
        await bot.send_message(chat_id=CHAT_ID, text="🏋️‍♂️ خسته نباشی دلاور!")
    else:
        await bot.send_message(chat_id=CHAT_ID, text="💪 خدا قوت پهلوان!")
    button_pressed = True

# --- دستور start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logging.info(f"Start command received from chat: {chat_id}")
    await update.message.reply_text(f"بات فعاله! Chat ID: {chat_id}")

# --- reset دستی ---
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global button_pressed
    if update.effective_chat.id != CHAT_ID:
        return
    button_pressed = False
    await update.message.reply_text("🔄 وضعیت دکمه ریست شد.")

# --- webhook endpoint ---
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logging.info(f"Received update: {data}")
        update = Update.de_json(data, bot)
        if update:
            logging.info("Processing update")
            flask_app.application.update_queue.put_nowait(update)
            logging.info("Update queued successfully")
            return "OK", 200
        logging.warning("No valid update received")
        return "No update data", 400
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        return "Error processing webhook", 500

# --- health check (GET /) ---
@flask_app.route("/", methods=["GET"])
def index():
    return "✅ Bashgah Bot is running!"

# --- main ---
import asyncio

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log')
        ]
    )

    scheduler.add_job(send_midnight_message, CronTrigger(hour=0, minute=0))
    scheduler.add_job(send_reminder, CronTrigger(hour=21, minute=0))
    scheduler.start()

    application = Application.builder().token(TOKEN).build()
    logging.info("Application initialized")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CallbackQueryHandler(button_handler))
    logging.info("Handlers added")

    flask_app.application = application

    # تنظیم وب‌هوک به صورت async
    async def set_webhook():
        await bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
        logging.info("Webhook set successfully")

    # اجرای تابع async
    asyncio.run(set_webhook())

    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
