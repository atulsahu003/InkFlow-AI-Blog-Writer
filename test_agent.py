
from typing import TypedDict, Literal

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END

load_dotenv()

# Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.3,
)

# Tavily web search tool
tavily = TavilySearch(max_results=3)


# Shared state used by all nodes
class BlogState(TypedDict):
    topic: str
    needs_research: str
    research: str
    outline: str


# Node 1: Decide whether research is required
def router_node(state: BlogState):
    prompt = f"""
You are a research decision maker for a blog-writing agent.

Topic: {state['topic']}

Decide whether current web research is useful for this topic.

Choose RESEARCH for:
- Current news, recent trends, latest statistics
- Current technology, products, or policies
- Claims that need up-to-date sources

Choose SKIP for:
- General concepts and timeless explanations
- Topics answerable without current information

Return exactly one word: RESEARCH or SKIP.
"""

    response = llm.invoke(prompt)
    decision = response.content

    # Gemini may return text or a list of content blocks
    if isinstance(decision, list):
        decision = "\n".join(
            item["text"]
            for item in decision
            if isinstance(item, dict) and item.get("type") == "text"
        )

    decision = str(decision).strip().upper()
    needs_research = (
        "RESEARCH"
        if "RESEARCH" in decision
        else "SKIP"
    )

    print(f"\nRouter decision: {needs_research}")

    return {"needs_research": needs_research}


# Node 2: Search the web using Tavily

def research_node(state: BlogState):
    print("\nSearching the web with Tavily...")

    result = tavily.invoke({
        "query": state["topic"]
    })

    # Keep research results in a structured format
    research_items = []

    # Tavily may return a list or a dictionary
    if isinstance(result, dict):
        items = result.get("results", [])
    elif isinstance(result, list):
        items = result
    else:
        items = []

    for item in items:
        if not isinstance(item, dict):
            continue

        title = item.get("title", "Untitled source")
        url = item.get("url", "")
        content = item.get("content", "")

        research_items.append({
            "title": title,
            "url": url,
            "content": content,
        })

    # Print the actual result structure for verification
    print("\nTAVILY SOURCES")
    print("=" * 50)

    for index, item in enumerate(research_items, start=1):
        print(f"\nSource {index}: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"Content: {item['content'][:300]}")

    # Convert the structured results into text for the planner
    research_text = "\n\n".join(
        f"Title: {item['title']}\n"
        f"URL: {item['url']}\n"
        f"Content: {item['content']}"
        for item in research_items
    )

    print("\nResearch completed.")

    return {"research": research_text}



# Node 3: Generate the blog outline
def planner_node(state: BlogState):
    prompt = f"""
You are an expert blog planner.

Blog topic: {state['topic']}

Web research:
{state['research'] or "No web research was required."}

Create a useful blog outline in Markdown.

Include:
1. An engaging blog title
2. An introduction idea
3. Five main headings with useful subtopics
4. A conclusion idea

If research was provided, use it where relevant.
Do not invent statistics or sources.
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    print("\nBlog outline generated.")

    return {"outline": str(content)}


# Conditional routing
def choose_research_path(
    state: BlogState,
) -> Literal["research", "skip_research"]:
    if state["needs_research"] == "RESEARCH":
        return "research"
    return "skip_research"


def skip_research_node(state: BlogState):
    print("\nSkipping web research.")
    return {"research": ""}


# Build LangGraph
builder = StateGraph(BlogState)

builder.add_node("router", router_node)
builder.add_node("research", research_node)
builder.add_node("skip_research", skip_research_node)
builder.add_node("planner", planner_node)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    choose_research_path,
    {
        "research": "research",
        "skip_research": "skip_research",
    },
)

builder.add_edge("research", "planner")
builder.add_edge("skip_research", "planner")
builder.add_edge("planner", END)

graph = builder.compile()


if __name__ == "__main__":
    topic = input("Enter your blog topic: ").strip()

    if not topic:
        raise ValueError("Please enter a blog topic.")

    result = graph.invoke({
        "topic": topic,
        "needs_research": "",
        "research": "",
        "outline": "",
    })

    print("\n" + "=" * 60)
    print("GENERATED BLOG OUTLINE")
    print("=" * 60)
    print(result["outline"])
