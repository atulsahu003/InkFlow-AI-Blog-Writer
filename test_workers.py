
from typing import TypedDict, Annotated, Literal
import operator

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

import re


def clean_generated_text(text: str) -> str:
    """Clean common formatting issues in generated Markdown."""
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")

    # Normalize excessive spaces while preserving line breaks
    text = re.sub(r"[ \t]+", " ", text)

    # Remove trailing spaces from lines
    text = "\n".join(line.rstrip() for line in text.splitlines())

    # Fix a few common concatenations seen in generated output
    replacements = {
        "thanaiming": "than aiming",
        "modernclassroom": "modern classroom",
        "virtualworlds": "virtual worlds",
        "educationallandscape": "educational landscape",
        "teachers toreclaim": "teachers to reclaim",
        "importantideas": "important ideas",
        "disciplinedadoption": "disciplined adoption",
        "atthecenter": "at the center",
    }

    for wrong, correct in replacements.items():
        text = re.sub(
            re.escape(wrong),
            correct,
            text,
            flags=re.IGNORECASE,
        )

    return text.strip()


load_dotenv()

# --------------------------------------------------
# 1. Initialize Gemini and Tavily
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
    temperature=0.3,
)

tavily = TavilySearch(max_results=3)


LENGTH_SETTINGS = {
    "short": {
        "total": "approximately 500 words",
        "section": "55-75 words",
        "intro_conclusion": "45-60 words each",
    },
    "medium": {
        "total": "approximately 1,000 words",
        "section": "140-180 words",
        "intro_conclusion": "80-100 words each",
    },
    "long": {
        "total": "approximately 1,500 words",
        "section": "230-280 words",
        "intro_conclusion": "100-130 words each",
    },
    "detailed": {
        "total": "approximately 2,000 words",
        "section": "330-380 words",
        "intro_conclusion": "130-160 words each",
    },
}

TONE_GUIDANCE = {
    "professional": "Use a clear, polished, objective professional tone.",
    "conversational": "Use a natural conversational tone, as if explaining the topic to a reader directly.",
    "friendly": "Use a warm, approachable, supportive tone without becoming overly informal.",
    "academic": "Use a formal, analytical, evidence-conscious academic tone and precise terminology.",
    "persuasive": "Use a compelling, confident, benefit-focused tone, while remaining accurate and avoiding unsupported claims.",
}

AUDIENCE_GUIDANCE = {
    "general": "Write for general readers. Explain specialized terms briefly and keep the article accessible.",
    "beginners": "Write for beginners. Explain concepts step by step, define jargon, and use simple examples where helpful.",
    "students": "Write for students. Emphasize clear explanations, key concepts, practical examples, and learning value.",
    "professionals": "Write for industry professionals. Emphasize practical implications, workflows, trade-offs, and informed decision-making.",
    "technical": "Write for technical experts. Use precise technical language, discuss implementation details where relevant, and avoid oversimplifying established concepts.",
}


def get_length_settings(state):
    return LENGTH_SETTINGS.get(state.get("blog_length", "medium"), LENGTH_SETTINGS["medium"])


def get_tone_guidance(state):
    tone = state.get("writing_tone", "professional")
    return TONE_GUIDANCE.get(tone, TONE_GUIDANCE["professional"])


def get_audience_guidance(state):
    audience = state.get("target_audience", "general")
    return AUDIENCE_GUIDANCE.get(audience, AUDIENCE_GUIDANCE["general"])


# --------------------------------------------------
# 2. Define Graph State
# --------------------------------------------------

class BlogState(TypedDict):
    topic: str
    blog_length: str
    writing_tone: str
    target_audience: str
    needs_research: str
    research: str
    sources: list[dict]
    sections: list[str]
    completed_sections: Annotated[list[str], operator.add]
    final_blog: str


class WorkerState(TypedDict):
    topic: str
    section: str
    research: str
    blog_length: str
    writing_tone: str
    target_audience: str
    completed_sections: list[str]


# --------------------------------------------------
# 3. Router: Decide whether web research is needed
# --------------------------------------------------

def router_node(state: BlogState):
    prompt = f"""
Decide whether this blog topic requires web research.

Topic: {state['topic']}

Reply with exactly one word: RESEARCH or SKIP.

Choose RESEARCH for:
- Current trends, news and recent developments
- Latest statistics, policies or product information
- Topics where up-to-date information is important

Choose SKIP for:
- Timeless concepts and general explanations
- Topics that do not need current information
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    decision = str(content).strip().upper()
    choice = "RESEARCH" if "RESEARCH" in decision else "SKIP"

    print(f"\nRouter decision: {choice}")

    return {"needs_research": choice}


def choose_research_path(
    state: BlogState,
) -> Literal["research", "skip_research"]:
    if state["needs_research"] == "RESEARCH":
        return "research"

    return "skip_research"


# --------------------------------------------------
# 4. Research Node: Search the web using Tavily
# --------------------------------------------------

def research_node(state: BlogState):
    print("\nSearching the web using Tavily...")

    result = tavily.invoke({"query": state["topic"]})

    # Handle Tavily's returned result format
    if isinstance(result, dict):
        items = result.get("results", [])
    elif isinstance(result, list):
        items = result
    else:
        items = []

    sources = []

    for item in items:
        if isinstance(item, dict) and item.get("url"):
            sources.append({
                "title": item.get("title", "Web source"),
                "url": item["url"],
                "content": item.get("content", "")[:1500],
            })

    research_text = "\n\n".join(
        (
            f"Source: {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Content: {source['content']}"
        )
        for source in sources
    )

    print(f"Research completed. Sources found: {len(sources)}")

    return {
        "research": research_text,
        "sources": sources,
    }


# --------------------------------------------------
# 5. Skip Research Node
# --------------------------------------------------

def skip_research_node(state: BlogState):
    print("\nWeb research skipped for this topic.")

    return {
        "research": "",
        "sources": [],
    }


# --------------------------------------------------
# 6. Planner: Create five blog section headings
# --------------------------------------------------

def planner_node(state: BlogState):
    prompt = f"""
Create exactly 5 useful section headings for a blog.

Blog topic:
{state['topic']}

Web research:
{state['research'] or "No web research was provided."}

Desired overall length: {get_length_settings(state)['total']}
Writing tone: {get_tone_guidance(state)}
Target audience: {get_audience_guidance(state)}

Requirements:
- Return only five headings, one per line.
- Do not write an introduction or conclusion.
- Do not add explanations before or after the headings.
- Make the headings relevant to the topic.
- Use the research context when available.
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    sections = [
        line.strip().lstrip("0123456789.-) ").strip()
        for line in str(content).splitlines()
        if line.strip()
    ]

    # Remove Markdown heading markers if Gemini includes them
    sections = [
        heading.lstrip("# ").strip()
        for heading in sections
        if heading.strip()
    ][:5]

    if not sections:
        raise ValueError("Planner did not generate any sections.")

    print(f"\nPlanner created {len(sections)} sections.")

    for index, section in enumerate(sections, start=1):
        print(f"{index}. {section}")

    return {"sections": sections}


# --------------------------------------------------
# 7. Dispatch one worker for every section
# --------------------------------------------------

def dispatch_workers(state: BlogState):
    return [
        Send(
            "worker",
            {
                "topic": state["topic"],
                "section": section,
                "research": state["research"],
                "blog_length": state.get("blog_length", "medium"),
                "writing_tone": state.get("writing_tone", "professional"),
                "target_audience": state.get("target_audience", "general"),
                "completed_sections": [],
            },
        )
        for section in state["sections"]
    ]


# --------------------------------------------------
# 8. Worker: Write one section
# --------------------------------------------------

def worker_node(state: WorkerState):
    print(f"Writing section: {state['section']}")

    prompt = f"""
You are an expert blog writer.

Overall blog topic:
{state['topic']}

Your assigned section:
{state['section']}

Web research and source material:
{state['research'] or "No web research was provided."}

Desired overall blog length: {get_length_settings(state)['total']}
Target length for this section: approximately {get_length_settings(state)['section']}
Writing tone: {get_tone_guidance(state)}
Target audience: {get_audience_guidance(state)}

Requirements:
- Start directly with the section content.
- Do not repeat the section heading.
- Write natural, grammatically correct English.
- Keep normal spaces between all words.
- Use readable Markdown paragraphs or lists when useful.
- Use relevant research when it is provided.
- Do not invent statistics, facts, quotations, or citations.
- Do not invent URLs or claim that you verified something you did not.
- Do not write another introduction or conclusion.
- Return only the section content.
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    content = clean_generated_text(str(content))

    section_text = f"## {state['section']}\n\n{content}"

    return {"completed_sections": [section_text]}


# --------------------------------------------------
# Source Verifier: Check factual claims against research
# --------------------------------------------------

def source_verifier_node(state: BlogState):
    print("\\nVerifying factual claims against available research...")

    blog = state.get("final_blog", "")
    research = state.get("research", "")
    sources = state.get("sources", [])

    # Do not claim verification when no research was collected.
    if not research.strip() or not sources:
        print("No research available. Skipping source verification.")
        return {}

    prompt = f"""
You are a careful fact-checking editor.

Review the blog using ONLY the research material supplied below.

BLOG:
{blog}

AVAILABLE RESEARCH:
{research}

RULES:
- Check specific statistics, dates, numerical claims, quotations,
  and other important factual claims against the available research.
- Preserve claims that are supported by the supplied research.
- If a claim is not supported by the supplied research, remove it
  or rewrite it with cautious wording.
- Never invent replacement statistics, facts, quotations, or sources.
- Do not claim you checked a full webpage if only extracted content
  or a search snippet was supplied.
- Preserve the blog title, section order, headings, and Markdown.
- Preserve every existing source URL exactly as written.
- Do not create new URLs or citations.
- Keep the article useful and readable.
- Return ONLY the revised complete blog in Markdown.
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    verified_blog = clean_generated_text(str(content))

    if not verified_blog.strip():
        print("Verifier returned empty text. Keeping original blog.")
        return {}

    print("Source verification review completed.")
    return {"final_blog": verified_blog}


# --------------------------------------------------
# Proofreader: Improve final blog quality
# --------------------------------------------------

def proofreader_node(state: BlogState):
    print("\nProofreading the generated blog...")

    blog = state["final_blog"]

    prompt = f"""
You are a careful proofreader and Markdown editor.

Proofread the blog below.

BLOG:
{blog}

Tasks:
- Correct missing spaces between words.
- Fix grammar, spelling, and punctuation.
- Improve awkward sentences only when necessary.
- Preserve the original meaning and section order.
- Preserve all Markdown headings and formatting.
- Preserve every source URL exactly as written.
- Do not add new facts, statistics, or citations.
- Do not remove any section.
- Return only the corrected complete blog.
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    corrected_blog = clean_generated_text(str(content))

    # Basic safety check: don't replace the blog with an empty response
    if not corrected_blog.strip():
        print("Proofreader returned empty text. Keeping original blog.")
        return {}

    print("Proofreading completed.")

    return {"final_blog": corrected_blog}



# --------------------------------------------------
# 9. Reducer: Combine sections and add source links
# --------------------------------------------------


def reducer_node(state: BlogState):
    sections = "\n\n".join(state["completed_sections"])

    sources = state.get("sources", [])

    if sources:
        source_links = "\n".join(
            f"- [{source['title']}]({source['url']})"
            for source in sources
        )
        sources_section = f"\n\n## Sources\n\n{source_links}"
    else:
        sources_section = ""

    # Generate a topic-specific introduction and conclusion
    prompt = f"""
You are a professional blog editor.

Blog topic:
{state['topic']}

Blog sections:
{sections}

Research material:
{state.get('research', '') or 'No web research was used.'}

Desired overall blog length: {get_length_settings(state)['total']}
Target length for the introduction and conclusion: {get_length_settings(state)['intro_conclusion']} each
Writing tone: {get_tone_guidance(state)}
Target audience: {get_audience_guidance(state)}

Write:
1. An engaging introduction.
2. A useful conclusion.

Requirements:
- Write natural, grammatically correct English.
- Use proper spaces between all words.
- Make both parts specific to the actual blog sections.
- Do not invent statistics or unsupported facts.
- Do not repeat the entire blog.
- Return exactly these headings:

INTRODUCTION:
[introduction text]

CONCLUSION:
[conclusion text]
"""

    print("\nPreparing the final introduction and conclusion...")

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    content = str(content).strip()

    # Extract introduction and conclusion
    upper_content = content.upper()
    intro_marker = "INTRODUCTION:"
    conclusion_marker = "CONCLUSION:"

    intro_start = upper_content.find(intro_marker)
    conclusion_start = upper_content.find(conclusion_marker)

    if intro_start != -1 and conclusion_start != -1:
        introduction = content[
            intro_start + len(intro_marker):conclusion_start
        ].strip()

        conclusion = content[
            conclusion_start + len(conclusion_marker):
        ].strip()
    else:
        # Fallback if the model doesn't follow the requested format
        introduction = (
            f"This blog explores {state['topic']} through the key "
            "themes discussed in the following sections."
        )
        conclusion = (
            f"Understanding {state['topic']} requires considering "
            "its opportunities, limitations, and practical implications."
        )

    final_blog = f"""# {state['topic']}

## Introduction

{introduction}

{sections}

## Conclusion

{conclusion}
{sources_section}
"""

    print("\nBlog assembled with a topic-specific introduction and conclusion.")

    final_blog = clean_generated_text(final_blog)

    return {"final_blog": final_blog}


# --------------------------------------------------
# 10. Build the LangGraph workflow
# --------------------------------------------------

builder = StateGraph(BlogState)

builder.add_node("router", router_node)
builder.add_node("research", research_node)
builder.add_node("skip_research", skip_research_node)
builder.add_node("planner", planner_node)
builder.add_node("worker", worker_node)
builder.add_node("reducer", reducer_node)
builder.add_node("proofreader", proofreader_node)
builder.add_node("source_verifier", source_verifier_node)

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

builder.add_conditional_edges(
    "planner",
    dispatch_workers,
    ["worker"],
)

builder.add_edge("worker", "reducer")
builder.add_edge("reducer", "source_verifier")
builder.add_edge("source_verifier", "proofreader")
builder.add_edge("proofreader", END)

graph = builder.compile()


# --------------------------------------------------
# 11. Run the Blog Writing Agent
# --------------------------------------------------

if __name__ == "__main__":
    topic = input("Enter your blog topic: ").strip()

    if not topic:
        raise ValueError("Please enter a topic.")

    result = graph.invoke({
        "topic": topic,
        "blog_length": "medium",
        "writing_tone": "professional",
        "target_audience": "general",
        "needs_research": "",
        "research": "",
        "sources": [],
        "sections": [],
        "completed_sections": [],
        "final_blog": "",
    })

    print("\n" + "=" * 60)
    print("GENERATED COMPLETE BLOG")
    print("=" * 60)
    print(result["final_blog"])

    with open("generated_blog.md", "w", encoding="utf-8") as file:
        file.write(result["final_blog"])

    print("\nBlog saved to generated_blog.md")
