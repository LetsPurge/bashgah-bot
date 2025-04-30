import os
import pytz
import json
from datetime import datetime
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = int(os.environ["CHAT_ID"])

bot = Bot(token=TOKEN)
flask_app = Flask(__name__)
scheduler = BackgroundScheduler(timezone="Asia/Tehran")

active_message_id = {"id": None}

def send_daily_question():
    try:
        today = datetime.now(pytz.timezone("Asia/Tehran")).strftime("%A")
        keyboard = [[InlineKeyboardButton("به والله وارد شدم 📿", callback_data="entered")]]
        message = bot.send_message(
            chat_id=CHAT_ID,
            text="وارد سایت شدی؟ 🤔",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        active_message_id["id"] = message.message_id
        print("📨 پیام روزانه ارسال شد")
    except Exception as e:
        print("❌ خطا در ارسال پیام روزانه:", e)

def send_reminder():
    if active_message_id["id"]:
        try:
            bot.send_message(chat_id=CHAT_ID, text="دِ بجنب دِ⏰")
            print("⏰ یادآوری ارسال شد")
        except Exception as e:
            print("❌ خطا در یادآوری:", e)

@flask_app.route("/", methods=["GET"])
def index():
    return "✅ Bashgah Bot is running!"

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = json.loads(request.data.decode("utf-8"))
        update = Update.de_json(data, bot)

        if update.message:
            if update.message.text == "/start":
            if active_message_id["id"]:
        # هنوز دکمه رو نزدی → پیام با دکمه دوباره فرستاده می‌شه
        keyboard = [[InlineKeyboardButton("به والله وارد شدم 📿", callback_data="entered")]]
        message = bot.send_message(
            chat_id=CHAT_ID,
            text="وارد سایت شدی؟ 🤔",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        active_message_id["id"] = message.message_id
    else:
        # قبلاً زدی دکمه → فقط یه پیام بده
        bot.send_message(chat_id=CHAT_ID, text="امان از فراموشی 🤦‍♂️")

            elif update.message.text == "/reset":
                active_message_id["id"] = None
                bot.send_message(chat_id=CHAT_ID, text="🔁 ریست شد.")
            elif update.message.text == "/restart":
                bot.send_message(chat_id=CHAT_ID, text="♻️ راه‌اندازی مجدد")

        elif update.callback_query:
            query = update.callback_query
            bot.answer_callback_query(callback_query_id=query.id, text="🤡 باشه باشه، باور کردیم که وارد شدی")

            # حذف پیام قبلی
            if active_message_id["id"]:
                try:
                    bot.delete_message(chat_id=CHAT_ID, message_id=active_message_id["id"])
                except:
                    pass

            weekday = datetime.now(pytz.timezone("Asia/Tehran")).weekday()
            if weekday in [0, 2, 3, 5]:  # شنبه، دوشنبه، چهارشنبه، جمعه
                response = "خسته نباشی دلاور 💪"
            else:
                response = "خدا قوت پهلوان 🛡️"

            bot.send_message(chat_id=CHAT_ID, text=response)
            active_message_id["id"] = None

    except Exception as e:
        print("❌ خطای اصلی:", repr(e))
    return "ok"

if __name__ == "__main__":
    scheduler.add_job(send_daily_question, "cron", hour=0, minute=0)
    scheduler.add_job(send_reminder, "cron", hour=21, minute=0)
    scheduler.start()

    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
