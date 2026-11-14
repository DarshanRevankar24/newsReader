import os
from fastapi import FastAPI, Query, Request
from agents.briefing_agent import generate_daily_briefing

# ... existing imports ...
from services.rss_fetcher import fetch_rss
from agents.rss_agent import get_articles_for_topic
from agents.rank_agent import rank_articles_with_llm
from agents.summary_agent import summarize_articles
from agents.memory_agent import update_memory, get_user_interests
from utils.user_identity import numeric_user_id

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"backend":"up"}

@app.get("/debug")
def debug_env():
    key = os.getenv("GROQ_API_KEY", "")
    return {
        "GROQ_API_KEY_set": bool(key),
        "GROQ_API_KEY_prefix": key[:8] + "..." if len(key) > 8 else "NOT SET",
        "GROQ_API_KEY_length": len(key),
    }

from db.models import Base
from db.core import engine

@app.on_event("startup")
def on_startup():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

@app.get("/briefing")
def get_briefing(user_id: str = "user_1"):
    briefing = generate_daily_briefing(numeric_user_id(user_id))
    return {"briefing": briefing}

@app.get("/news/{topic}")
def get_news(topic: str, user_id: str = "user_1"):
    # 1. Get articles for the topic
    # Using get_articles_for_topic from rss_agent
    articles = get_articles_for_topic(topic)
    
    if not articles:
        return {"message": f"No articles found for topic: {topic}", "news": []}

    # 2. Get User Interests
    # Currently from memory_agent (in-memory), later will be from DB
    interests = get_user_interests(user_id)
    
    # 3. Rank Articles
    # Using the fixed rank_agent function
    ranked_articles = rank_articles_with_llm(
        articles,
        interests
    )

    # 4. Limit and Summarize
    # Summarize top 5
    top_articles = ranked_articles[:5]
    summaries = summarize_articles(top_articles)

    # 5. Update Memory
    # Record that these articles proved relevant (or just seen)
    update_memory(user_id, top_articles)
    save_articles_to_db(top_articles)

    return {
        "user_id": user_id,
        "interests": interests,
        "news": summaries
    }

from pydantic import BaseModel

class Feedback(BaseModel):
    user_id: str
    article_link: str
    interaction_type: str  # 'like', 'dislike', 'click'

@app.post("/feedback")
def submit_feedback(feedback: Feedback):
    db = SessionLocal()
    
    # Resolve User Link
    numeric_uid = numeric_user_id(feedback.user_id)
    
    from db.models import UserInteraction, Article
    
    # Log Interaction
    interaction = UserInteraction(
        user_id=numeric_uid,
        article_link=feedback.article_link,
        interaction_type=feedback.interaction_type
    )
    db.add(interaction)
    
    # Process Feedback for Profile Update
    # 1. Fetch article from DB
    article = db.query(Article).filter(Article.id == feedback.article_link).first()
    
    if article:
        # 2. Update Profile
        from agents.profile_agent import update_user_profile
        
        signal = f"User {feedback.interaction_type}ed article: '{article.title}'. Summary: {article.summary}"
        update_user_profile(numeric_uid, signal)
        print(f"Updated profile for user {numeric_uid} based on feedback for {article.title}")
    
    db.commit()
    db.close()
    
    return {"status": "success", "message": "Feedback recorded and profile updated"}

from db.models import UserProfile, Article
from db.core import SessionLocal

def save_articles_to_db(articles):
    db = SessionLocal()
    for art in articles:
        # Check if exists
        exists = db.query(Article).filter(Article.id == art['link']).first()
        if not exists:
            new_art = Article(
                id=art['link'],
                title=art['title'],
                summary=art['summary'],
                source=art['source'],
                published=None, # date parsing is complex, skipping for now
                embedding=""
            )
            db.add(new_art)
    db.commit()
    db.close()

def get_user_profile_text(user_id):
    db = SessionLocal()
    uid = numeric_user_id(user_id)
    profile = db.query(UserProfile).filter_by(user_id=uid).first()
    db.close()
    return profile.profile_text if profile else "General news reader"

from telegram import Bot, Update

# Telegram config
BASE_URL = os.getenv("BASE_URL", "https://YOUR_FIREBASE_APP_URL") # E.g., your Cloud Run or Firebase Hosting URL
WEBHOOK_PATH = "/telegram-webhook"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Bot instance - no initialize() call needed for send_message
tg_bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None
if tg_bot:
    print("Telegram Bot instance ready.", flush=True)
else:
    print("No TELEGRAM_BOT_TOKEN set.", flush=True)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    if not tg_bot:
        return {"ok": False, "error": "No bot token"}

    data = await request.json()
    msg = data.get("message") or data.get("edited_message")
    if not msg:
        return {"ok": True}

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    user_id = str(msg.get("from", {}).get("id", "1"))

    async def send(reply: str):
        await tg_bot.send_message(chat_id=chat_id, text=reply[:4096])

    if text.startswith("/start") or text.startswith("/help"):
        await send(
            "Hello! I am your AI News Agent ☁️\n\n"
            "Commands:\n"
            "/news <topic> - Get latest news\n"
            "/briefing - Get your daily AI briefing\n"
            "/help - Show this message"
        )

    elif text.startswith("/news"):
        topic = text.replace("/news", "", 1).strip()
        if not topic:
            await send("Please provide a topic. Example: /news AI")
            return {"ok": True}
        await send(f"🔍 Fetching news for '{topic}'...")
        try:
            articles = get_articles_for_topic(topic)
            if not articles:
                await send(f"No articles found for '{topic}'. Try a broader term.")
                return {"ok": True}
            interests = get_user_interests(user_id)
            ranked = rank_articles_with_llm(articles, interests)[:5]
            summaries = summarize_articles(ranked)
            reply = f"📰 *News for {topic}:*\n\n"
            for item in summaries:
                reply += f"• {item['title']}\n{item['summary']}\n🔗 {item['link']}\n\n"
            reply += "☕ https://buymeacoffee.com/darshanrevankar"
            await send(reply)
        except Exception as e:
            await send(f"Sorry, something went wrong: {e}")

    elif text.startswith("/briefing"):
        await send("Writing your daily briefing... (this takes a few seconds)")
        try:
            briefing = generate_daily_briefing(1)
            briefing += "\n\n☕ https://buymeacoffee.com/darshanrevankar"
            await send(briefing)
        except Exception as e:
            await send(f"Failed to generate briefing: {e}")

    else:
        # Treat plain text as a news topic
        topic = text
        await send(f"🔍 Fetching news for '{topic}'...")
        try:
            articles = get_articles_for_topic(topic)
            if not articles:
                await send(f"No articles found for '{topic}'.")
                return {"ok": True}
            interests = get_user_interests(user_id)
            ranked = rank_articles_with_llm(articles, interests)[:5]
            summaries = summarize_articles(ranked)
            reply = f"📰 *News for {topic}:*\n\n"
            for item in summaries:
                reply += f"• {item['title']}\n{item['summary']}\n🔗 {item['link']}\n\n"
            reply += "☕ https://buymeacoffee.com/darshanrevankar"
            await send(reply)
        except Exception as e:
            await send(f"Error: {e}")

    return {"ok": True}
