import requests
import sys

def test_api():
    url = "http://127.0.0.1:8001/news/technology"
    try:
        print(f"Testing {url}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print("Response received!")
        print(f"User Interest: {data.get('interests')}")
        news = data.get('news', [])
        print(f"News count: {len(news)}")
        
        if len(news) > 0:
            print("First article:", news[0]['title'])
            print("Verification PASSED")
        else:
            print("No news returned (might be valid if feed is empty, but unexpected for tech)")
            print("Verification WARNING")
            
    except Exception as e:
        print(f"Verification FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
