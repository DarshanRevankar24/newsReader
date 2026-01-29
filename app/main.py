from fastapi import FastAPI,Query
from services.rss_fetcher import fetch_rss
from agents.rss_agent import get_articles_for_topic
from agents.rank_agent import process_articles
from agents.summary_agent import summarize_articles
app=FastAPI()

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
    ranked_articles=process_articles(articles)
    summarize=summarize_articles(ranked_articles)
    return summarize
