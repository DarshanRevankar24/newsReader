import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from groq import Groq

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Lazy LLM — initialized on first use so HF Secrets are always picked up
_llm = None

def _select_model_id(available_model_ids):
    configured_model = os.getenv("GROQ_MODEL")
    available = set(available_model_ids)

    if configured_model:
        if configured_model in available:
            return configured_model
        print(
            f"Warning: GROQ_MODEL '{configured_model}' is unavailable to this API key; "
            "selecting an available model instead."
        )

    preferred_models = (
        "openai/gpt-oss-20b",
        "qwen/qwen3-32b",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "moonshotai/kimi-k2-instruct",
    )
    for model_id in preferred_models:
        if model_id in available:
            return model_id

    non_chat_markers = (
        "embed", "guard", "moderation", "orpheus", "speech", "transcrib",
        "tts", "whisper",
    )
    chat_models = sorted(
        model_id for model_id in available
        if not any(marker in model_id.lower() for marker in non_chat_markers)
    )
    if chat_models:
        return chat_models[0]

    raise RuntimeError(
        "Groq returned no available chat models for this API key. "
        "Check the key's model access or set GROQ_MODEL to an available chat model."
    )

def get_llm():
    global _llm
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY not found in environment")
        return None
    if _llm is None:
        available_models = Groq(api_key=api_key).models.list()
        model_id = _select_model_id(model.id for model in available_models.data)
        _llm = ChatGroq(api_key=api_key, model=model_id)
        print(f"LLM initialized with available Groq model: {model_id}")
    return _llm

def summarize_article(article):
    prompt = f"""
Summarize the following news article in 2–3 lines.
Be factual, concise, and neutral.
Do not add opinions.

Title: {article['title']}
Content: {article['summary']}
"""

    try:
        llm = get_llm()
        if not llm:
            return "Summary unavailable (GROQ_API_KEY is not configured)"
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
