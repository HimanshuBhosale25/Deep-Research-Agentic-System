from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

from .agents import (
    ResearcherAgentWrapper,
    AnswerDraftingAgentWrapper,
    run_researcher,
    run_answer_drafter,
    llm
)

class AgentState(TypedDict):
    user_query: str
    research_results: List[Dict[str, Any]]
    drafted_answer: str
    messages: List[BaseMessage]
    researcher_agent: ResearcherAgentWrapper
    answer_drafting_agent: AnswerDraftingAgentWrapper

def create_research_answer_workflow():
    """Creates the LangGraph workflow for research and answer generation."""
    graph = StateGraph(AgentState)
    graph.add_node("research", run_researcher)
    graph.add_node("draft", run_answer_drafter)
    graph.set_entry_point("research")
    graph.add_edge("research", "draft")
    graph.add_edge("draft", END)

    return graph.compile()