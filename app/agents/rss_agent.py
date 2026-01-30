RSS_FEEDS = {
    "india": [
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    ],
    "world": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    ],
    "technology": [
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml"
    ],
    "business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html"
    ],
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"
    ],
    "football": [
        "https://feeds.bbci.co.uk/sport/football/rss.xml"
    ],
    "cricket": [
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"
    ],
    "science": [
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://www.sciencedaily.com/rss/top/science.xml"
    ]
}

from services.rss_fetcher import fetch_rss
import urllib.parse

def get_articles_for_topic(topic:str, limit:int=5):
    normalized_topic = topic.lower().strip()
    
    # 1. Check if we have curated feeds for this exact topic
    feeds = RSS_FEEDS.get(normalized_topic)
    
    # 2. If not, fallback to Google News RSS
    if not feeds:
        print(f"Topic '{topic}' not found in curated list. Using Google News fallback.")
        encoded_topic = urllib.parse.quote(topic)
        feeds = [f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"]

    all_articles = []
    seen_links = set()

    for feed_url in feeds:
        try:
            articles = fetch_rss(feed_url, limit)
            for article in articles:
                # Deduplication based on link
                if article['link'] not in seen_links:
                    all_articles.append(article)
                    seen_links.add(article['link'])
        except Exception as e:
            print(f"Error fetching feed {feed_url}: {e}")
            continue
            
    return all_articles    
