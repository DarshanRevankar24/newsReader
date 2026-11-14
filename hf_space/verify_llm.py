import os
from dotenv import load_dotenv

# Try loading from different locations to be sure
load_dotenv()
load_dotenv(".env")
load_dotenv("app/.env")
load_dotenv("app/agents/.env")

print(f"Checking GROQ_API_KEY...")
key = os.getenv("GROQ_API_KEY")
if key:
    print("GROQ_API_KEY found.")
else:
    print("ERROR: GROQ_API_KEY not found in environment variables.")

try:
    from langchain_core.messages import HumanMessage
    from agents.summary_agent import get_llm
    
    if key:
        print("Finding an available Groq chat model...")
        llm = get_llm()
        if not llm:
            raise RuntimeError("GROQ_API_KEY is not configured.")
        print("Invoking LLM...")
        response = llm.invoke([HumanMessage(content="Say hello")])
        print(f"Response: {response.content}")
    else:
        print("Skipping invocation due to missing key.")

except Exception as e:
    print(f"LLM Error: {e}")
