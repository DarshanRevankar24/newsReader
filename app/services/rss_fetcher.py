import feedparser
from datetime import datetime

def fetch_rss(fetch_url:str,limit: int = 10):
    feed=feedparser.parse(fetch_url)
    articles=[]
    for entry in feed.entries[:limit]:
        article={
        "title":entry.get("title",""),
        "link":entry.get("link",""),
        "published":entry.get("published",""),
        "summary":entry.get("summary",""),
        "source":feed.feed.get("title","")
        }
        articles.append(article)
    return articles