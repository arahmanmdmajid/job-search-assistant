"""
agent.py — LangGraph StateGraph workflow for the Job Search Assistant.

Flow:
    user message → agent_node → (tool call?) → ToolNode → agent_node → ... → END

Memory is persisted per thread_id using MemorySaver (checkpointing).
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from tools import web_search_tool, salary_tool, summarize_tool

load_dotenv()

# ---------------------------------------------------------------------------
# 1. LLM — bind the three tools so the model knows they exist
# ---------------------------------------------------------------------------

tools = [web_search_tool, salary_tool, summarize_tool]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# ---------------------------------------------------------------------------
# 2. System prompt — tells the LLM its role and personality
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a helpful Job Search Assistant. You help users with:
- Finding job listings and openings (use web_search_tool)
- Researching salary ranges for specific roles (use salary_tool)
- Summarizing job descriptions into clear bullet points (use summarize_tool)
- General career advice based on your knowledge

Always be concise, friendly, and practical. When a user asks about jobs or salaries,
use the appropriate tool to get real, up-to-date information rather than guessing.
If a user pastes a job description, offer to summarize it for them."""

# ---------------------------------------------------------------------------
# 3. Nodes
# ---------------------------------------------------------------------------

def agent_node(state: MessagesState) -> dict:
    """
    The main thinking node. Prepends the system prompt, calls the LLM,
    and returns the response to be added to the message state.
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: MessagesState) -> str:
    """
    Conditional routing function.
    Checks the last message: if it contains tool calls, route to 'tools'.
    Otherwise the LLM is done — route to END.
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


# ---------------------------------------------------------------------------
# 4. Build the StateGraph
# ---------------------------------------------------------------------------

tool_node = ToolNode(tools)

graph_builder = StateGraph(MessagesState)

# Add nodes
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", tool_node)

# Entry point — always start at agent_node
graph_builder.set_entry_point("agent")

# Conditional edge from agent: either go to tools or END
graph_builder.add_conditional_edges("agent", should_continue)

# After tools finish, always loop back to agent so LLM can process the result
graph_builder.add_edge("tools", "agent")

# ---------------------------------------------------------------------------
# 5. Compile with MemorySaver (enables checkpointing per thread_id)
# ---------------------------------------------------------------------------

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# ---------------------------------------------------------------------------
# 6. Helper function — used by app.py to send one message and get a reply
# ---------------------------------------------------------------------------

def chat(user_message: str, thread_id: str) -> str:
    """
    Send a user message to the graph and return the assistant's reply.

    Args:
        user_message: The text the user typed
        thread_id:    Unique ID for this conversation session (for memory)
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config,
    )
    # The last message in state is always the assistant's final response
    return result["messages"][-1].content
