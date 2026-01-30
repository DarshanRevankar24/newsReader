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
    print(f"Key found: {key[:5]}...{key[-5:]}")
else:
    print("ERROR: GROQ_API_KEY not found in environment variables.")

try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage
    
    if key:
        print("Initializing ChatGroq...")
        llm = ChatGroq(
            api_key=key,
            model="llama-3.1-8b-instant"
        )
        print("Invoking LLM...")
        response = llm.invoke([HumanMessage(content="Say hello")])
        print(f"Response: {response.content}")
    else:
        print("Skipping invocation due to missing key.")

except Exception as e:
    print(f"LLM Error: {e}")
