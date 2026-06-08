import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters,
)
from dotenv import load_dotenv
from telegram_bot.handlers import (
    start, get_name, get_business, get_problem, get_email,
    cancel, non_text_handler, help_command,
    WAITING_NAME, WAITING_BUSINESS, WAITING_PROBLEM, WAITING_EMAIL,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN       = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # e.g. https://yourapp.koyeb.app

def build_application() -> Application:
    app = Application.builder().token(TOKEN).build()
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
    return app

ptb_app = build_application()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb_app.initialize()
    await ptb_app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/webhook",
        allowed_updates=Update.ALL_TYPES,
    )
    logger.info(f"Webhook set → {WEBHOOK_URL}/webhook")
    yield
    await ptb_app.bot.delete_webhook()
    await ptb_app.shutdown()

api = FastAPI(lifespan=lifespan)

@api.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}

@api.get("/health")
async def health():
    return {"status": "running"}

@api.get("/")
async def root():
    return {"bot": "LeadQual Demo", "status": "active"}