import requests
import sys

def verify_topics():
    topics = ["iit"]
    base_url = "http://127.0.0.1:8001/news"
    
    for topic in topics:
        print(f"\n--- Testing Topic: {topic} ---")
        try:
            url = f"{base_url}/{topic}"
            print(f"Fetching {url}...")
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            articles = data.get("news", [])
            
            print(f"Status: {r.status_code}")
            print(f"Articles Found: {len(articles)}")
            
            if len(articles) > 0:
                print(f"Top Article: {articles[0]['title']}")
                print("PASS")
            else:
                print("WARNING: No articles found (Google News might be strict or empty)")
                
        except Exception as e:
            print(f"FAIL: {e}")

if __name__ == "__main__":
    verify_topics()
