import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Lazy LLM — initialized on first use so HF Secrets are always picked up
_llm = None

def get_llm():
    global _llm
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY not found in environment")
        return None
    if _llm is None:
        try:
            _llm = ChatGroq(api_key=api_key, model="llama-3.1-8b-instant")
            print(f"LLM initialized with key prefix: {api_key[:8]}...")
        except Exception as e:
            print(f"Warning: Failed to initialize LLM: {e}")
            return None
    return _llm

# Keep backward-compat alias used by briefing_agent
llm = None

def summarize_article(article):
    llm = get_llm()
    if not llm:
        return "Summary unavailable (LLM disabled or API key missing)"

    prompt = f"""
Summarize the following news article in 2–3 lines.
Be factual, concise, and neutral.
Do not add opinions.

Title: {article['title']}
Content: {article['summary']}
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"Error summarizing: {e}"


def summarize_articles(articles):
    results = []

    for article in articles:
        summary = summarize_article(article)
        results.append({
            "title": article["title"],
            "summary": summary,
            "source": article["source"],
            "link": article["link"]
        })

    return results
