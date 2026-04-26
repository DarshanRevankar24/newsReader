import os
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Import our existing agents
# Note: We need to set up path to import from sibling directories or run as module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.rss_agent import get_articles_for_topic
from agents.briefing_agent import generate_daily_briefing
from agents.summary_agent import summarize_articles
# We can use memory agent later to link user_id from telegram to our DB

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I am your AI News Agent.\n\nCommands:\n/news <topic> - Get latest news\n/briefing - Get daily AI briefing\n/help - Show this message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /news command. Args: {context.args}")
    
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a topic. Example: /news tech")
        return

    topic = " ".join(context.args)
    print(f"Fetching news for topic: {topic}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔍 Fetching news for '{topic}'...")

    try:
        # Run synchronous agents in thread pool if needed, but for now simple call
        print("Calling get_articles_for_topic...")
        articles = get_articles_for_topic(topic, limit=5)
        print(f"Found {len(articles)} articles.")
        
        if not articles:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"No articles found for '{topic}'. Try a broader term.")
            return

        # Prepare message
        # User requested just a paragraph, no links loop.
        print("Summarizing...")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Found articles. creating summary...")
        
        summary_data = summarize_articles(articles[:5])
        
        # Convert list of dicts to a single text
        final_text = f"**Summary for {topic}:**\n\n"
        for item in summary_data:
            final_text += f"• **{item['title']}**\n{item['summary']}\n🔗 Read more: {item['link']}\n\n"
            
        final_text += "\n\n☕ You can support me here: https://buymeacoffee.com/darshanrevankar"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=final_text)

    except Exception as e:
        print(f"ERROR in get_news: {e}")
        logging.error(f"Error fetching news: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, something went wrong fetching the news.")

async def get_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # In a real app, map Telegram ID to DB User ID. For now map all to user_1
    mapped_user_id = 1 
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Writing your daily briefing... (this takes a few seconds)")
    
    try:
        # This calls LLM, might block event loop if not careful, but fine for MVP
        briefing = generate_daily_briefing(mapped_user_id)
        briefing += "\n\n☕ You can support me here: https://buymeacoffee.com/darshanrevankar"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=briefing)
    except Exception as e:
         logging.error(f"Error generating briefing: {e}")
         await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to generate briefing.")


def get_application():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return None

    app = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).build()
    
    from telegram.ext import filters, MessageHandler

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = update.message.text
        context.args = topic.split()
        await get_news(update, context)

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('news', get_news))
    app.add_handler(CommandHandler('briefing', get_briefing))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    return app

if __name__ == '__main__':
    app = get_application()
    if app:
        print("Bot is running...")
        app.run_polling(drop_pending_updates=True, stop_signals=None)
