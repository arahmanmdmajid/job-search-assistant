# test_setup.py
# Run this to confirm your environment is correctly configured.
# Expected output:
#   OpenAI key found: YES
#   Tavily key found: YES
#   LLM responded: Hello!
#   Tavily returned 5 results
#   All good! Setup complete.

from dotenv import load_dotenv
import os

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print("OpenAI key found:", "YES" if openai_key else "MISSING — add to .env")
print("Tavily key found:", "YES" if tavily_key else "MISSING — add to .env")

if not openai_key or not tavily_key:
    print("\nFix missing keys in your .env file before continuing.")
    exit(1)

# Test LangChain + OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("Say hello in one word")
print("LLM responded:", response.content)

# Test Tavily
from tavily import TavilyClient
client = TavilyClient(api_key=tavily_key)
result = client.search("Python developer jobs 2025")
print("Tavily returned", len(result["results"]), "results")

print("\nAll good! Setup complete. Next step: implement tools.py")
