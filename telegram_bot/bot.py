# bot.py — local polling dev only, NOT deployed
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters,
)
from telegram_bot.handlers import (
    start, get_name, get_business, get_problem, get_email,
    cancel, non_text_handler, help_command,
    WAITING_NAME, WAITING_BUSINESS, WAITING_PROBLEM, WAITING_EMAIL,
)

load_dotenv()

def main():
    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            WAITING_BUSINESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_business)],
            WAITING_PROBLEM:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_problem)],
            WAITING_EMAIL:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        },
        fallbacks=[
            CommandHandler("restart", cancel),
            CommandHandler("start", start),
            MessageHandler(filters.PHOTO | filters.Document.ALL | filters.Sticker.ALL, non_text_handler),
        ],
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_command))
    print("Running locally (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()