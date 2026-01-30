from fastapi import FastAPI,Query
from services.rss_fetcher import fetch_rss
from agents.rss_agent import get_articles_for_topic
from agents.rank_agent import rank_articles_with_llm
from agents.summary_agent import summarize_articles
app=FastAPI()

USER_INTERESTS = [
    "AI",
    "Artificial Intelligence",
    "Technology",
    "India",
    "Startups"
]


@app.get("/")
def home():
    return {"backend":"up"}

@app.get("/news")
def get_news():
    url = "https://feeds.bbci.co.uk/news/rss.xml"
    return fetch_rss(url,10)


@app.get("/news/{topic}")
def get_news(topic: str):
    articles= get_articles_for_topic(topic)
    ranked_articles = rank_articles_with_llm(
    articles,
    USER_INTERESTS
)

    summarize=summarize_articles(ranked_articles)
    return summarize


from agents.memory_agent import update_memory, get_user_interests

@app.get("/news/{category}")
def get_news(category: str, user_id: str = "user_1"):
    articles = fetch_news(category)

    interests = get_user_interests(user_id)

    ranked_articles = rank_articles_with_llm(
        articles,
        interests
    )

    summaries = summarize_articles(ranked_articles[:5])

    update_memory(user_id, ranked_articles[:5])

    return {
        "user_id": user_id,
        "interests": interests,
        "news": summaries
    }


from app.agents.profile_agent import get_or_create_user_profile

@app.get("/news/{topic}")
def get_news(topic: str, user_id: int = 1):
    user_profile = get_or_create_user_profile(user_id)

    articles = ingest_articles(topic)
    ranked = rank_articles_with_llm(
        articles,
        user_profile.embedding
    )
    summaries = summarize_articles(ranked[:10])

    return summaries
