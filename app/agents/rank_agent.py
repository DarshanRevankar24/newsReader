from agents.summary_agent import llm
from langchain_core.messages import HumanMessage



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
    

def llm_score_article(article, interests):
    prompt = f"""
You are a news relevance evaluator.

User interests:
{", ".join(interests)}

Article title:
{article['title']}

Article summary:
{article['summary']}

Give a relevance score from 0 to 10.
Respond with ONLY a number.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return int(response.content.strip())

def rank_articles_with_llm(articles, interests):
    ranked = []

    for article in articles:
        llm_score = llm_score_article(article, interests)

        article["llm_score"] = llm_score
        ranked.append(article)

    ranked.sort(
        key=lambda x: x["llm_score"],
        reverse=True
    )

    return ranked

# def process_articles(articles, top_k=10):
#     unique = deduplicate_articles(articles)
#     ranked = rank_articles(unique, top_k)
#     return ranked
