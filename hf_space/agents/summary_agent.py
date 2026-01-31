import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    if not os.getenv("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY not found in environment")
        llm = None
    else:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-8b-instant"
        )
except Exception as e:
    print(f"Warning: Failed to initialize LLM: {e}")
    llm = None

def summarize_article(article):
    if not llm:
        return "Summary unavailable (LLM disabled)"

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
