import os
import pytz
import json
from datetime import datetime, date
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = int(os.environ["CHAT_ID"])
bot = Bot(token=TOKEN)
flask_app = Flask(__name__)
scheduler = BackgroundScheduler(timezone="Asia/Tehran")

STATUS_FILE = "status.json"

def load_status():
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"date": "", "answered": False, "message_id": None}

def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f)

def send_daily_question():
    today_str = str(date.today())
    status = {
        "date": today_str,
        "answered": False,
        "message_id": None
    }

    keyboard = [[InlineKeyboardButton("به والله وارد شدم 📿", callback_data="entered")]]
    msg = bot.send_message(
        chat_id=CHAT_ID,
        text="وارد سایت شدی؟ 🤔",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    status["message_id"] = msg.message_id
    save_status(status)
    print("📨 پیام روزانه ارسال شد")

def send_reminder():
    status = load_status()
    if status["date"] == str(date.today()) and not status["answered"]:
        bot.send_message(chat_id=CHAT_ID, text="دِ بجنب دِ⏰")
        print("⏰ یادآوری ارسال شد")

@flask_app.route("/", methods=["GET"])
def index():
    return "✅ Bashgah Bot is running!"

@flask_app.route("/reminder", methods=["GET"])
def external_reminder():
    from datetime import date
    status = load_status()
    if status["date"] == str(date.today()) and not status["answered"]:
        bot.send_message(chat_id=CHAT_ID, text="دِ بجنب دِ⏰")
        return "✅ Reminder sent."
    return "No reminder needed."
    
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = json.loads(request.data.decode("utf-8"))
        update = Update.de_json(data, bot)

        if update.message:
            if update.message.text == "/start":
                status = load_status()
                today = str(date.today())

                if status["date"] != today:
                    # یعنی پیام امروز ارسال نشده، پس الان بفرست
                    keyboard = [[InlineKeyboardButton("به والله وارد شدم 📿", callback_data="entered")]]
                    msg = bot.send_message(
                        chat_id=CHAT_ID,
                        text="وارد سایت شدی؟ 🤔",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    status["date"] = today
                    status["answered"] = False
                    status["message_id"] = msg.message_id
                    save_status(status)

                elif not status["answered"]:
                     # پیام امروز ارسال شده ولی هنوز پاسخ ندادی
                    keyboard = [[InlineKeyboardButton("به والله وارد شدم 📿", callback_data="entered")]]
                    msg = bot.send_message(
                        chat_id=CHAT_ID,
                        text="وارد سایت شدی؟ 🤔",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    status["message_id"] = msg.message_id
                    save_status(status)

                else:
                    bot.send_message(chat_id=CHAT_ID, text="امان از فراموشی 🤦‍♂️")

            elif update.message.text == "/reset":
                save_status({"date": "", "answered": False, "message_id": None})
                bot.send_message(chat_id=CHAT_ID, text="🔁 ریست شد.")

            elif update.message.text == "/restart":
                bot.send_message(chat_id=CHAT_ID, text="♻️ راه‌اندازی مجدد")

        elif update.callback_query:
            query = update.callback_query
            bot.answer_callback_query(callback_query_id=query.id, text="🤡 باشه باشه، باور کردیم که وارد شدی")

            status = load_status()
            if status["message_id"]:
                try:
                    bot.delete_message(chat_id=CHAT_ID, message_id=status["message_id"])
                except:
                    pass

            from datetime import datetime
            import pytz

            weekday = datetime.now(pytz.timezone("Asia/Tehran")).weekday()
            if weekday in [0, 2, 5]:  # دوشنبه، چهارشنبه، جمعه، شنبه
                response = "خسته نباشی دلاور 💪"
            else:
                response = "خدا قوت پهلوان 🛡️"


            bot.send_message(chat_id=CHAT_ID, text=response)
            status["answered"] = True
            status["message_id"] = None
            save_status(status)

    except Exception as e:
        print("❌ خطای اصلی:", repr(e))
    return "ok"

if __name__ == "__main__":
    scheduler.add_job(send_daily_question, "cron", hour=0, minute=0)
    scheduler.add_job(send_reminder, "cron", hour=21, minute=0)
    scheduler.start()

    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
