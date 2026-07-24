"""
Agent State — Defines the state schema for the LangGraph agent.
"""
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the banking analytics agent."""
    # Conversation messages (LangGraph manages append-only message list)
    messages: Annotated[list, add_messages]
