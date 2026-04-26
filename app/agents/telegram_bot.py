import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration - bot calls the same backend (itself) via the public HF Space URL
BACKEND_URL = os.getenv("BACKEND_URL", "https://darshanrevankar-newsai.hf.space")

import requests

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am your AI News Agent ☁️\n\n"
        "Commands:\n"
        "/news <topic> - Get latest news\n"
        "/briefing - Get daily AI briefing\n"
        "/help - Show this message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        topic = " ".join(context.args)
    elif update.message and update.message.text and not update.message.text.startswith('/'):
        topic = update.message.text
    else:
        await update.message.reply_text("Please provide a topic. Example: /news tech")
        return

    await update.message.reply_text(f"🔍 Fetching news for '{topic}'...")

    try:
        response = requests.get(
            f"{BACKEND_URL}/news/{topic}",
            params={"user_id": str(update.effective_user.id)},
            timeout=60
        )
        if response.status_code != 200:
            await update.message.reply_text(f"Error from backend: {response.status_code}")
            return

        data = response.json()
        news_items = data.get("news", [])

        if not news_items:
            await update.message.reply_text(f"No articles found for '{topic}'. Try a broader term.")
            return

        final_text = f"📰 *News for {topic}:*\n\n"
        for item in news_items:
            final_text += f"• *{item['title']}*\n{item['summary']}\n🔗 {item['link']}\n\n"

        final_text += "☕ Support: https://buymeacoffee.com/darshanrevankar"

        if len(final_text) > 4000:
            final_text = final_text[:4000] + "...(truncated)"

        await update.message.reply_text(final_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        await update.message.reply_text("Sorry, something went wrong fetching the news.")

async def get_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Writing your daily briefing... (this takes a few seconds)")

    try:
        response = requests.get(
            f"{BACKEND_URL}/briefing",
            params={"user_id": str(update.effective_user.id)},
            timeout=60
        )
        if response.status_code == 200:
            briefing = response.json().get("briefing", "No briefing content.")
            briefing += "\n\n☕ Support: https://buymeacoffee.com/darshanrevankar"
            await update.message.reply_text(briefing)
        else:
            await update.message.reply_text("Failed to fetch briefing from backend.")
    except Exception as e:
        logging.error(f"Error generating briefing: {e}")
        await update.message.reply_text("Failed to communicate with backend.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.args = update.message.text.split()
    await get_news(update, context)

def get_application():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set", flush=True)
        return None

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('news', get_news))
    app.add_handler(CommandHandler('briefing', get_briefing))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    return app

if __name__ == '__main__':
    app = get_application()
    if app:
        print(f"Bot starting (polling mode)... Connected to {BACKEND_URL}")
        app.run_polling(drop_pending_updates=True, stop_signals=None)
