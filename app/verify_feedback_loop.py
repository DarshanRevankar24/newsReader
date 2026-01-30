import requests
import sys
from db.core import SessionLocal
from db.models import Article, UserInteraction, UserProfile

def verify():
    # 1. Fetch News (should cache articles)
    print("Fetching news...")
    try:
        r = requests.get("http://127.0.0.1:8001/news/india")
        r.raise_for_status()
        data = r.json()
        articles = data.get("news", [])
        if not articles:
            print("No articles returned, skipping cache check (might be empty feed)")
            return
        
        first_link = articles[0]['link']
        print(f"First article link: {first_link}")
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return

    # 2. Check DB for Cache
    print("Checking DB for cached article...")
    db = SessionLocal()
    cached = db.query(Article).filter(Article.id == first_link).first()
    if cached:
        print(f"Found cached article: {cached.title}")
    else:
        print("Article NOT found in DB cache!")
        db.close()
        return

    # 3. Send Feedback
    print("Sending feedback...")
    feedback_data = {
        "user_id": "user_1",
        "article_link": first_link,
        "interaction_type": "like"
    }
    try:
        r = requests.post("http://127.0.0.1:8001/feedback", json=feedback_data)
        r.raise_for_status()
        print(f"Feedback response: {r.json()}")
    except Exception as e:
        print(f"Failed to send feedback: {e}")
        db.close()
        return

    # 4. Check Profile Update
    print("Checking User Profile...")
    profile = db.query(UserProfile).filter_by(user_id=1).first()
    if profile:
        print(f"Profile Text: {profile.profile_text}")
        if "like" in profile.profile_text and cached.title in profile.profile_text:
             print("VERIFICATION PASSED: Profile reflects feedback!")
        else:
             print("VERIFICATION WARNING: Profile might not be updated correctly.")
    else:
        print("Profile not found!")

    db.close()

if __name__ == "__main__":
    verify()
