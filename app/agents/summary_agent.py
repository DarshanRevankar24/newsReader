import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant"
)

def summarize_article(article):
    prompt = f"""
Summarize the following news article in 2–3 lines.
Be factual, concise, and neutral.
Do not add opinions.

Title: {article['title']}
Content: {article['summary']}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


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
