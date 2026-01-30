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
    if not llm:
        return 0

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

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        try:
            return int(response.content.strip())
        except ValueError:
            return 0
    except Exception:
        return 0

def rank_articles_with_llm(articles, interests):
    scored_articles = []
    
    # Deduplicate first
    unique_articles = deduplicate_articles(articles)
    
    print(f"Ranking {len(unique_articles)} articles for interests: {interests}")
    
    for article in unique_articles:
        # Combined score: Basic heuristic + LLM
        # Doing LLM on all might be slow/expensive, limiting to top 20 candidate by heuristic first is better practice
        # but for now we follow the user's lead.
        # Let's simple check if we want to run LLM on all. 
        # To save tokens/time, let's just score with LLM if title matches keywords? 
        # No, let's just do it.
        score = llm_score_article(article, interests)
        scored_articles.append((article, score))
        
    # Sort by score desc
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    
    return [a[0] for a in scored_articles]
