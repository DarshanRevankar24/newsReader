from fastapi import FastAPI, Query
from agents.briefing_agent import generate_daily_briefing

# ... existing imports ...
from services.rss_fetcher import fetch_rss
from agents.rss_agent import get_articles_for_topic
from agents.rank_agent import rank_articles_with_llm
from agents.summary_agent import summarize_articles
from agents.memory_agent import update_memory, get_user_interests

app = FastAPI()

@app.get("/")
def home():
    return {"backend":"up"}

from db.models import Base
from db.core import engine

@app.on_event("startup")
def on_startup():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

@app.get("/briefing")
def get_briefing(user_id: str = "user_1"):
    numeric_uid = 1
    if user_id.startswith("user_"):
         numeric_uid = int(user_id.split("_")[1])
    
    briefing = generate_daily_briefing(numeric_uid)
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
    numeric_user_id = 1
    if feedback.user_id.isdigit():
        numeric_user_id = int(feedback.user_id)
    elif "_" in feedback.user_id:
         numeric_user_id = int(feedback.user_id.split("_")[1])
    
    from db.models import UserInteraction, Article
    
    # Log Interaction
    interaction = UserInteraction(
        user_id=numeric_user_id,
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
        update_user_profile(numeric_user_id, signal)
        print(f"Updated profile for user {numeric_user_id} based on feedback for {article.title}")
    
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
    # Handle user_id str -> int conversion if needed for DB lookup
    # But UserProfile.user_id is Integer.
    uid = 1
    if user_id.startswith("user_"):
        uid = int(user_id.split("_")[1])
        
    profile = db.query(UserProfile).filter_by(user_id=uid).first()
    db.close()
    return profile.profile_text if profile else "General news reader"
