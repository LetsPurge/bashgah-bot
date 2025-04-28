from flask import Flask
import threading
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

# --- تنظیمات ---
TOKEN = "7899798019:AAHHLV6JTMlaLx_iWPXC-ltffu8is09w7hk"
CHAT_ID = 1725732444  # چت آیدی خودت
TIMEZONE = pytz.timezone("Asia/Tehran")

# --- لاگ ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- متغیر وضعیت ---
button_pressed_today = False

# --- دکمه ورود ---
def get_keyboard():
    keyboard = [[InlineKeyboardButton("به والله وارد شدم 📿", callback_data="entered")]]
    return InlineKeyboardMarkup(keyboard)

# --- شروع ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return
    await update.message.reply_text("🎯 بات فعال شد و منتظر دستوراتت قهرمان!")

# --- ریست دستی ---
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global button_pressed_today
    if update.effective_chat.id != CHAT_ID:
        return
    button_pressed_today = False
    await update.message.reply_text("🔄 ریست شد. آماده‌ی شروع روز جدید!")

# --- ریستارت دستی (شبیه سازی) ---
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return
    await update.message.reply_text("♻️ درخواست ریست ثبت شد. لطفاً اپ رو از Render ریستارت کن.")

# --- ارسال سوال ورود ---
async def ask_entry(context: ContextTypes.DEFAULT_TYPE):
    global button_pressed_today
    button_pressed_today = False
    await context.bot.send_message(chat_id=CHAT_ID, text="❓ وارد سایت شدی؟", reply_markup=get_keyboard())

# --- یادآوری ساعت 21:00 ---
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    if not button_pressed_today:
        await context.bot.send_message(chat_id=CHAT_ID, text="⏰ دِ بجنب دِ!")

# --- وقتی دکمه فشرده شد ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global button_pressed_today
    if update.effective_chat.id != CHAT_ID:
        return

    query = update.callback_query
    await query.answer("🤡 باشه باشه، باور کردیم که وارد شدی")
    await query.message.delete()

    now = datetime.now(TIMEZONE)
    weekday = now.weekday()  # 0=Monday, 6=Sunday

    if weekday in [5, 0, 2, 4]:  # شنبه، دوشنبه، چهارشنبه، جمعه
        await context.bot.send_message(chat_id=CHAT_ID, text="🏋️‍♂️ خسته نباشی دلاور!")
    else:  # یکشنبه، سه‌شنبه، پنجشنبه
        await context.bot.send_message(chat_id=CHAT_ID, text="💪 خدا قوت پهلوان!")

    button_pressed_today = True

# --- راه‌اندازی برنامه ---
async def post_init(application: Application):
    scheduler = AsyncIOScheduler(timezone="Asia/Tehran")
    scheduler.add_job(ask_entry, CronTrigger(hour=0, minute=0))
    scheduler.add_job(send_reminder, CronTrigger(hour=21, minute=0))
    scheduler.start()

# --- اجرای اصلی ---
app = Application.builder().token(TOKEN).post_init(post_init).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("restart", restart))
app.add_handler(CallbackQueryHandler(button))

# --- راه اندازی سرور فیک برای Render ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bashgah Bot is alive! 🚀"

def run():
    app_web.run(host='0.0.0.0', port=10000)

threading.Thread(target=run).start()

if __name__ == "__main__":
    app.run_polling()
