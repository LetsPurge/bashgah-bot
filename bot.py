# bot.py

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from config import TOKEN, CHAT_ID
import db
import datetime

# --- لاگ ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- متغیرهای وضعیت گفتگو ---
CHOOSING_ACTION, TYPING_VALUE = range(2)
pending_action = None

# --- شروع ربات ---
app = ApplicationBuilder().token(TOKEN).build()

# --- شروع کاربر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return
    db.init_db()
    await send_table(update)

# --- ساخت جدول ---
async def send_table(update: Update):
    records = db.get_all_records()
    text = "📋 جدول ورود یا ورود 📋\n\n"
    text += "روز هفته | وضعیت ورود | قرعه‌کشی | توضیحات\n"
    text += "---------------------------------------------\n"
    for rec in records:
        text += f"{rec['day']} | {rec['status']} | {rec['lottery']} | {rec['note']}\n"

    keyboard = [
        [InlineKeyboardButton("به والله که وارد شدم📿", callback_data='entered')],
        [InlineKeyboardButton("قرعه‌کشی 🎲", callback_data='lottery')],
        [InlineKeyboardButton("توضیح بده 📜", callback_data='note')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

# --- پاسخ به دکمه‌ها ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_action
    query = update.callback_query
    await query.answer()

    if update.effective_chat.id != CHAT_ID:
        return

    if query.data == 'entered':
        today = get_today_name()
        db.update_record(today, "status", "ورود انجام شد✅")
        await query.edit_message_text("✅ ورود ثبت شد!")
        await send_table(update)

    elif query.data == 'lottery':
        pending_action = 'lottery'
        await query.edit_message_text("چند امتیاز؟")

    elif query.data == 'note':
        pending_action = 'note'
        await query.edit_message_text("هرچه می‌خواهد دل تنگت بگو!")

# --- گرفتن عدد یا متن بعد از دکمه‌ها ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_action
    if update.effective_chat.id != CHAT_ID:
        return

    if pending_action == 'lottery':
        today = get_today_name()
        value = update.message.text.strip()
        db.update_record(today, "lottery", f"{value} امتیاز")
        await update.message.reply_text("🎲 قرعه‌کشی ثبت شد!")
        await send_table(update)

    elif pending_action == 'note':
        today = get_today_name()
        value = update.message.text.strip()
        db.update_record(today, "note", value)
        await update.message.reply_text("📜 توضیح ثبت شد!")
        await send_table(update)

    pending_action = None

# --- دریافت نام روز جاری ---
def get_today_name():
    days = ["دوشنبه", "سه‌شنبه", "چهار‌شنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"]
    today_idx = (datetime.datetime.today().weekday() + 1) % 7
    return days[today_idx]

# --- /help ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return

    text = """🛠️ دستورات قابل استفاده:
/start - شروع و دریافت جدول
/help - دریافت لیست دستورات
/history - مشاهده تاریخچه
"""
    await update.message.reply_text(text)

# --- اضافه کردن هندلرها ---
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# --- اجرا ---
if __name__ == "__main__":
    db.init_db()
    app.run_polling()
