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
    from telegram.ext import Application

app = Application.builder().token(TOKEN).build()

@app.post(f"/{TOKEN}")
async def webhook(request):
    data = await request.get_json()
    update = Update.de_json(data, bot)
    print("📩 پیام جدید:", update)
    return "ok"

    print("📩 پیام جدید:", update)
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
