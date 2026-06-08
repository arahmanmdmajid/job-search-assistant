"""
tools.py — Three tools for the Job Search Assistant agent.

Each function is decorated with @tool so LangChain can register it.
The LLM reads each docstring to decide which tool to call and when.
"""

import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()


# ---------------------------------------------------------------------------
# Tool 1 — Web Search (Tavily external API)
# ---------------------------------------------------------------------------

@tool
def web_search_tool(query: str) -> str:
    """
    Search the web for job listings, company information, hiring news,
    or any job-market related topic. Use this when the user asks about
    specific jobs, companies, or wants to find current job postings.

    Args:
        query: The search query, e.g. 'Python developer jobs in London 2025'
    """
    from tavily import TavilyClient

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query, max_results=5)

    results = response.get("results", [])
    if not results:
        return "No results found. Try a different search query."

    # Format results into readable text for the LLM
    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"{i}. {r.get('title', 'No title')}\n"
            f"   URL: {r.get('url', '')}\n"
            f"   {r.get('content', '')[:300]}..."
        )

    return "\n\n".join(formatted)


# ---------------------------------------------------------------------------
# Tool 2 — Salary Lookup (Remotive API — free, no key required)
# ---------------------------------------------------------------------------

@tool
def salary_tool(job_title: str) -> str:
    """
    Look up salary ranges and job market data for a given job title.
    Use this when the user asks about salaries, pay ranges, or
    compensation for a specific role or profession.

    Args:
        job_title: The job title to search for, e.g. 'data scientist' or 'software engineer'
    """
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": job_title, "limit": 10}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return f"Could not fetch salary data: {e}"

    jobs = data.get("jobs", [])
    if not jobs:
        return f"No salary data found for '{job_title}'. Try a broader title like 'software engineer'."

    # Extract salary info from listings that include it
    salary_entries = []
    no_salary_count = 0

    for job in jobs:
        salary = job.get("salary", "").strip()
        company = job.get("company_name", "Unknown")
        title = job.get("title", "")
        if salary:
            salary_entries.append(f"- {title} at {company}: {salary}")
        else:
            no_salary_count += 1

    if not salary_entries:
        return (
            f"Found {len(jobs)} '{job_title}' listings on Remotive but none listed "
            f"explicit salary figures. Many remote companies share salary on request."
        )

    result = f"Salary data for '{job_title}' from Remotive (remote jobs):\n\n"
    result += "\n".join(salary_entries[:8])
    if no_salary_count:
        result += f"\n\n({no_salary_count} additional listings did not include salary figures.)"

    return result


# ---------------------------------------------------------------------------
# Tool 3 — Job Description Summarizer (custom Python tool, no external API)
# ---------------------------------------------------------------------------

@tool
def summarize_tool(job_description: str) -> str:
    """
    Summarize a job description into clear bullet points covering the role,
    key responsibilities, required skills, nice-to-have skills, and any
    notable perks or red flags. Use this when the user pastes a job posting
    and wants a quick structured summary.

    Args:
        job_description: The full text of the job description to summarize
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = (
        "You are a helpful job search assistant. Summarize the following job description "
        "into clear, concise bullet points under these headings:\n\n"
        "**Role Overview** — What is this job in one sentence?\n"
        "**Key Responsibilities** — What will the person do day-to-day? (3-5 bullets)\n"
        "**Required Skills** — What are they asking for? (3-5 bullets)\n"
        "**Nice-to-Have** — Any bonus skills mentioned?\n"
        "**Perks / Red Flags** — Anything notable (salary, culture, vague language, etc.)\n\n"
        f"Job Description:\n{job_description}"
    )

    response = llm.invoke(prompt)
    return response.content
