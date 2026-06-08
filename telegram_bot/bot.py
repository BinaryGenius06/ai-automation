import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WAITING_NAME, WAITING_BUSINESS, WAITING_PROBLEM, WAITING_EMAIL = range(4)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Hi! I help match you with the right solution.\n\n"
        "Quick 3 questions — takes 90 seconds.\n\n"
        "What's your name?"
    )
    return WAITING_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("Please enter your full name.")
        return WAITING_NAME
    context.user_data["name"] = name
    await update.message.reply_text(
        f"Nice to meet you, {name}!\n\n"
        "What does your business do? (one line is fine)"
    )
    return WAITING_BUSINESS
async def get_business(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["business"] = update.message.text.strip()
    await update.message.reply_text(
        "Got it. What's the main problem you're trying to solve?\n\n"
        "For example: manual follow-ups, slow customer support, data entry..."
    )
    return WAITING_PROBLEM


async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["problem"] = update.message.text.strip()
    await update.message.reply_text(
        "Got it. Last one — what's your email so we can follow up?"
    )
    return WAITING_EMAIL
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text.strip()
    context.user_data["email"] = email
    name = context.user_data.get("name", "there")

    # TODO Day 9: send to Groq for scoring here
    # TODO Day 9: log to Google Sheet here
    # TODO Day 9: send alert if hot lead here

    logger.info(f"New lead: {context.user_data}")

    await update.message.reply_text(
        f"Thanks {name}! ✅\n\n"
        f"We'll review your info and get back to you within 24 hours at {email}.\n\n"
        "Type /start to begin again."
    )
    return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "No problem — let's start over.\n\nSend /start when ready."
    )
    return ConversationHandler.END


async def non_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Please reply with text only. Send /start to begin."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "This bot qualifies leads for businesses automatically.\n\n"
        "It asks 3 quick questions and notifies the right team.\n\n"
        "Send /start to begin."
    )
    
def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
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

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))

    print("Bot running... Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()