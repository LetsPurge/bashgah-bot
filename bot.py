import os
from flask import Flask, request
from telegram import Bot, Update
import json

TOKEN = os.environ["BOT_TOKEN"]
bot = Bot(token=TOKEN)
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def index():
    return "✅ Bashgah Bot is running!"

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        print("📥 درخواست جدید دریافت شد ✅")
        raw_data = request.data.decode("utf-8")
        print("📦 داده‌ی خام دریافتی:", raw_data)

        data = json.loads(raw_data)
        update = Update.de_json(data, bot)
        print("📩 پیام دریافت‌شده:", update)

        chat_id = update.message.chat.id
        text = update.message.text

        bot.send_message(chat_id=chat_id, text=f"✅ دریافت شد: {text}")

    except Exception as e:
        print("❌ خطای واقعی:", repr(e))

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
