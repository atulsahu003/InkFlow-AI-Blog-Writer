
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

search_tool = TavilySearch(max_results=3)

results = search_tool.invoke({
    "query": "Latest developments in artificial intelligence"
})

if isinstance(results, dict):
    results = results.get("results", [])

for result in results:
    print("Title:", result.get("title", "No title"))
    print("URL:", result.get("url", "No URL"))
    print("Content:", result.get("content", "No content"))
    print("-" * 60)
