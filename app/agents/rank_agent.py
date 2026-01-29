USER_INTERESTS = [
    "AI",
    "Artificial Intelligence",
    "Technology",
    "India",
    "Startups"
]


def deduplicate_articles(articles):
    seen_titles = set()
    unique_articles = []

    for article in articles:
        title = article["title"].lower()
        if title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)

    return unique_articles
     

from datetime import datetime

def score_article(article):
    score = 0

    title = article["title"].lower()

    # Recency boost
    if article.get("published"):
        score += 2

    # Keyword importance
    important_words = ["breaking", "election", "match", "india", "government"]
    for word in important_words:
        if word in title:
            score += 1

    # Source trust
    trusted_sources = ["BBC", "The Hindu"]
    if article["source"] in trusted_sources:
        score += 2

    return score
    
def rank_articles(articles, interests=USER_INTERESTS):
    ranked_articles = []

    for article in articles:
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()

        score = 0
        for topic in interests:
            if topic.lower() in title or topic.lower() in summary:
                score += 1

        article["relevance_score"] = score
        ranked_articles.append(article)

    ranked_articles.sort(
        key=lambda x: x["relevance_score"],
        reverse=True
    )

    return ranked_articles


# def process_articles(articles, top_k=10):
#     unique = deduplicate_articles(articles)
#     ranked = rank_articles(unique, top_k)
#     return ranked
