import os
import logging
from telegram_bot.groq_scorer import score_lead
from telegram_bot.sheets_logger import log_lead
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
    """Receive email → ack user immediately → score → log → alert if hot."""
    email = update.message.text.strip()
    context.user_data["email"] = email

    name     = context.user_data.get("name", "")
    business = context.user_data.get("business", "")
    problem  = context.user_data.get("problem", "")

    # ACK FIRST — never make user wait for Groq (1-3 sec lag)
    await update.message.reply_text(
        f"Thanks {name}! ✅\n\n"
        "We'll review your details and get back to you within 24 hours.\n\n"
        f"Confirmation sent to: {email}"
    )

    # Step 1: Score
    scoring    = score_lead(name, business, problem, email)
    score      = scoring.get("score", "cold")
    reason     = scoring.get("reason", "")
    confidence = scoring.get("confidence", "low")
    logger.info(f"Lead scored: {name} | {score} | {reason}")

    # Step 2: Log
    logged = log_lead(name, business, problem, email, score, reason, confidence)
    logger.info(f"Sheets log: {'success' if logged else 'failed'}")

    # Step 3: Alert owner if hot
    if score == "hot":
        owner_chat_id = os.environ.get("TELEGRAM_OWNER_CHAT_ID")
        if owner_chat_id:
            alert_text = (
                f"🔥 *Hot Lead*\n\n"
                f"*Name:* {name}\n"
                f"*Business:* {business}\n"
                f"*Problem:* {problem}\n"
                f"*Email:* {email}\n\n"
                f"*Why hot:* {reason}\n"
                f"*Confidence:* {confidence}"
            )
            try:
                await context.bot.send_message(
                    chat_id=int(owner_chat_id),
                    text=alert_text,
                    parse_mode="Markdown"
                )
                logger.info(f"Hot lead alert sent for {name}")
            except Exception as e:
                logger.error(f"Alert failed: {e}")

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
