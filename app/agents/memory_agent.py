from collections import defaultdict

USER_MEMORY = defaultdict(lambda: defaultdict(int))

def update_memory(user_id: str, articles: list):
    for article in articles:
        title = article["title"].lower()

        if "ai" in title:
            USER_MEMORY[user_id]["AI"] += 1
        if "cricket" in title or "match" in title:
            USER_MEMORY[user_id]["Cricket"] += 1
        if "startup" in title:
            USER_MEMORY[user_id]["Startups"] += 1

def get_user_interests(user_id: str):
    memory = USER_MEMORY[user_id]
    if not memory:
        return ["Technology"]
    return sorted(memory, key=memory.get, reverse=True)
