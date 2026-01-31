from agents.summary_agent import llm
from langchain_core.messages import HumanMessage
from db.core import SessionLocal
from db.models import UserProfile, Article

def generate_daily_briefing(user_id: int):
    db = SessionLocal()
    profile = db.query(UserProfile).filter_by(user_id=user_id).first()
    
    # Grab recent 5 articles
    # (In future, use vector search here)
    articles = db.query(Article).limit(5).all()
    
    if not articles:
        db.close()
        return "No news available to generate a briefing."
        
    articles_text = "\n".join([f"- {a.title}: {a.summary}" for a in articles])
    
    profile_text = profile.profile_text if profile else "General Interest"
    
    prompt = f"""
    You are a personal news assistant.
    User Profile: {profile_text}
    
    Here are the latest headlines:
    {articles_text}
    
    Write a short, engaging 1-paragraph daily briefing for the user.
    Focus on what matches their profile.
    """
    
    if not llm:
        db.close()
        return "LLM is unavailable. Here are your top headlines:\n" + articles_text

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        db.close()
        return response.content
    except Exception as e:
        db.close()
        return f"Error generating briefing: {e}"
