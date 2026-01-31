
import feedparser
import urllib.parse

def test_feed(topic):
    encoded_topic = urllib.parse.quote(topic)
    url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
    print(f"Testing URL: {url}")
    feed = feedparser.parse(url)
    print(f"Status: {feed.get('status')}")
    print(f"Entries: {len(feed.entries)}")
    if feed.entries:
        print(f"First Entry: {feed.entries[0].title}")

if __name__ == "__main__":
    test_feed("machine learning")
