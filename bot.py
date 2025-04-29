from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text("سلام، من زنده‌ام!")

def main():
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
