import os
from dotenv import load_dotenv

load_dotenv()

print("Gemini key loaded:", bool(os.getenv("GOOGLE_API_KEY")))
print("Tavily key loaded:", bool(os.getenv("TAVILY_API_KEY")))