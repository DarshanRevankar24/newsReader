RSS_FEEDS = {
    "india": [
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
        "https://www.thehindu.com/news/national/feeder/default.rss"
    ],
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml"
    ],
    "football": [
        "https://feeds.bbci.co.uk/sport/football/rss.xml"
    ]
}

from services.rss_fetcher import fetch_rss
def get_articles_for_topic(topic:str,limit:int=5):
    feeds=RSS_FEEDS.get(topic.lower(),[])
    all_articles=[]
    for feed_url in feeds:
        articles=fetch_rss(feed_url,limit)
        all_articles.extend(articles)
    return all_articles    
