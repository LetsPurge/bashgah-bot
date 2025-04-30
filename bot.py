import os
from flask import Flask, request
from telegram import Bot, Update

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
        data = request.get_data()
        print("📦 دیتا خام:", data)
        update = Update.de_json(request.get_json(force=True), bot)
        print("📩 پیام جدید:", update)
    except Exception as e:
        print("❌ خطای واقعی:", repr(e))  # این دقیق خطا رو نشون میده
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
