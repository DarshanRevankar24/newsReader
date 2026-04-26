import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "https://darshanrevankar-news-bot.hf.space")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I am your AI News Agent (Connected to Cloud ☁️).\n\nCommands:\n/news <topic> - Get latest news\n/briefing - Get daily AI briefing\n/help - Show this message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /news command. Args: {context.args}")
    
    # Handle direct text input case vs command args
    if context.args:
        topic = " ".join(context.args)
    elif update.message.text and not update.message.text.startswith('/'):
        topic = update.message.text
    else:
        # Fallback if no topic provided in a command context
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a topic. Example: /news tech")
        return

    print(f"Fetching news for topic: {topic} from {BACKEND_URL}...")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔍 Fetching news for '{topic}' from cloud backend...")

    try:
        # Call Backend API
        # Using synchronous requests library (blocking) for simplicity in this MVP.
        # Ideally use httpx.AsyncClient for high scale.
        response = requests.get(f"{BACKEND_URL}/news/{topic}", params={"user_id": str(update.effective_user.id)})
        
        if response.status_code != 200:
             await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error from backend: {response.status_code}")
             return
             
        data = response.json()
        news_items = data.get("news", [])
        
        if not news_items:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"No articles found for '{topic}'. Try a broader term.")
            return

        # Format Message
        final_text = f"**Summary for {topic}:**\n\n"
        for item in news_items:
            # Backend response structure: { "title":..., "summary":..., "source":..., "link":... }
            final_text += f"• **{item['title']}**\n{item['summary']}\n🔗 Read more: {item['link']}\n\n"
            
        final_text += "\n\n☕ You can support me here: https://buymeacoffee.com/darshanrevankar"
        
        # Split message if too long (Telegram limit is 4096 chars)
        if len(final_text) > 4000:
            final_text = final_text[:4000] + "...(truncated)"
            
        await context.bot.send_message(chat_id=update.effective_chat.id, text=final_text)

    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(f"Error fetching news: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, something went wrong fetching the news.")

async def get_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Writing your daily briefing... (this takes a few seconds)")
    
    try:
        response = requests.get(f"{BACKEND_URL}/briefing", params={"user_id": str(update.effective_user.id)})
        
        if response.status_code == 200:
            data = response.json()
            briefing = data.get("briefing", "No briefing content.")
            briefing += "\n\n☕ You can support me here: https://buymeacoffee.com/darshanrevankar"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=briefing)
        else:
             await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to fetch briefing from backend.")

    except Exception as e:
         logging.error(f"Error generating briefing: {e}")
         await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to communicate with backend.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Retrieve the text, treat it as a topic for news
    topic = update.message.text
    # Set context.args to simulate command (optional, but our logic handles direct text)
    context.args = topic.split()
    await get_news(update, context)

def get_application():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return None

    application = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('news', get_news))
    application.add_handler(CommandHandler('briefing', get_briefing))
    
    # Handle non-command text messages
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    return application

if __name__ == '__main__':
    app_bot = get_application()
    if app_bot:
        print(f"Bot starting... Connected to {BACKEND_URL}")
        app_bot.run_polling(drop_pending_updates=True, stop_signals=None)
