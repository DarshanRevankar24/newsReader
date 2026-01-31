from agents.summary_agent import llm
from langchain_core.messages import HumanMessage
from utils.embeddings import embed
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(vec1_list, vec2_list):
    if not vec1_list or not vec2_list:
        return 0.0
    v1 = np.array(vec1_list).reshape(1, -1)
    v2 = np.array(vec2_list).reshape(1, -1)
    return cosine_similarity(v1, v2)[0][0]



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
    
    # Generate embedding for interests (simplistic approach: concat interests)
    interest_text = ", ".join(interests)
    interest_embedding = embed(interest_text)

    for article in unique_articles:
        score = 0
        
        # 1. Vector Similarity Score (if models loaded)
        article_embedding = embed(article['title'] + " " + article['summary'])
        sim = calculate_similarity(interest_embedding, article_embedding)
        score += sim * 10  # Weight similarity heavily (0-1 -> 0-10)
        
        # 2. Heuristic Score (Recency, Sources)
        score += score_article(article)
        
        # 3. LLM Score (Optional/Refinement)
        # score += llm_score_article(article, interests)

        scored_articles.append((article, score))
        
    # Sort by score desc
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    
    return [a[0] for a in scored_articles]
