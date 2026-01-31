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
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss"
    ],
    "tech": [ # Alias for technology
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml"
    ],
    "business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://feeds.bloomberg.com/markets/news.xml"
    ],
    "finance": [ # Alias/Separate
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://feeds.bloomberg.com/markets/news.xml",
        "https://www.financialexpress.com/feed/"
    ],
    "sports": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"
    ],
    "football": [
        "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "https://www.goal.com/feeds/en/news"
    ],
    "cricket": [
        "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
        "https://www.cricbuzz.com/rss/news"
    ],
    "science": [
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "https://www.sciencedaily.com/rss/top/science.xml"
    ],
    "health": [
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://www.medicalnewstoday.com/feed",
        "https://www.webmd.com/rss/public/rss.aspx?feed_id=1"
    ],
    "entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "https://www.hollywoodreporter.com/feed/",
        "https://variety.com/feed/"
    ],
    "politics": [
        "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://rss.politico.com/politics-news.xml"
    ],
    "ai": [
        "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
        "https://wired.com/feed/tag/ai/latest/rss",
        "https://mit-news-rss.mit.edu/rss/topic/artificial-intelligence2"
    ],
    "startups": [
        "https://techcrunch.com/startups/feed/",
        "https://feeds.feedburner.com/entrepreneur/latest"
    ]
}

from services.rss_fetcher import fetch_rss
import urllib.parse
from duckduckgo_search import DDGS

def search_web_fallback(topic: str, limit: int = 5):
    """
    Search web using DuckDuckGo if RSS fails.
    """
    print(f"RSS failed. Searching web for: {topic}")
    results = []
    try:
        ddgs = DDGS()
        # Use 'news' backend if possible, or text search
        # Simple text search often works better for general topics
        search_results = ddgs.text(topic, max_results=limit) 
        
        for res in search_results:
            results.append({
                "title": res.get('title', 'No Title'),
                "link": res.get('href', ''),
                "summary": res.get('body', ''),
                "source": "Web Search",
                "published": "Unknown"
            })
    except Exception as e:
        print(f"Error in web search fallback: {e}")
        
    return results

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
            
    # 3. If still no articles, try Web Search Fallback
    if not all_articles:
        all_articles = search_web_fallback(topic, limit)
            
    return all_articles    
