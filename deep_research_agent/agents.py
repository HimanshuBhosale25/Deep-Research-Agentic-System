import os
from typing import List, Dict, Any

from langchain.agents import BaseSingleActionAgent
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from dotenv import load_dotenv
from tavily import TavilyClient  

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

llm = ChatOpenAI(model_name="gpt-4.1-nano", openai_api_key=openai_api_key)
tavily_client = TavilyClient(api_key=tavily_api_key)

def tavily_search(query: str) -> List[Dict[str, Any]]:
    """Performs a Tavily search and returns the results."""
    response = tavily_client.search(query=query)
    return response.get("results", [])

research_tool = Tool(
    name="tavily_search",
    func=tavily_search,
    description="Useful for searching the web for up-to-date information.",
)

researcher_prompt = PromptTemplate.from_template(
    """You are an expert at generating search queries for the Tavily search engine to answer the user's question.

    User's Question: '{user_query}'

    Your Task: Generate a concise and effective search query (under 400 characters) that, when used with Tavily, will retrieve relevant information to answer the user's question.

    Output the search query directly and without any additional text or formatting.

    Search Query:"""
)

researcher_chain = (
    {"user_query": RunnablePassthrough()}
    | researcher_prompt
    | llm
    | StrOutputParser()
    | {"query": RunnablePassthrough()}
    | research_tool
)

class ResearcherAgentWrapper:
    def __init__(self, chain: Runnable):
        self.chain = chain

    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        result = self.chain.invoke(input)
        return {"research_results": result}

    async def ainvoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.chain.ainvoke(input)
        return {"research_results": result}

answer_prompt = PromptTemplate.from_template(
    """You are an expert answer drafting agent. Based on the research results provided below, synthesize a comprehensive and well-structured answer to the user's query: '{user_query}'.

    Research Results (Tavily JSON format):
    {research_results}

    Instructions:
    1. Understand the user's original query and the provided research results.
    2. Identify the key themes and supporting evidence from the search results that directly address the user's query.
    3. Synthesize this information into a coherent and well-organized answer, drawing connections between different sources where relevant. Avoid simply listing information from each source independently.
    4. **Cite the source URL at the end of each sentence or paragraph that draws information from a specific source.** Use the following format for citations: `(Source: URL)`.
    5. Ensure the answer is clear, concise, informative, and directly addresses the user's query.

    Draft your answer:"""
)

answer_chain = (
    {"user_query": RunnablePassthrough(), "research_results": RunnablePassthrough()}
    | answer_prompt
    | llm
    | StrOutputParser()
)

class AnswerDraftingAgentWrapper:
    def __init__(self, chain: Runnable):
        self.chain = chain

    def invoke(self, input: Dict[str, Any]) -> Dict[str, str]:
        result = self.chain.invoke(input)
        return {"drafted_answer": result}

    async def ainvoke(self, input: Dict[str, Any]) -> Dict[str, str]:
        result = await self.chain.ainvoke(input)
        return {"drafted_answer": result}

def run_researcher(state):
    """Executes the researcher agent and updates the state."""
    user_query = state["user_query"]
    research_results = researcher_chain.invoke({"user_query": user_query})
    return {"research_results": research_results}

def run_answer_drafter(state):
    """Executes the answer drafting agent and updates the state."""
    user_query = state["user_query"]
    research_results = state["research_results"]
    answer_drafting_agent = state["answer_drafting_agent"]
    return answer_drafting_agent.invoke({"user_query": user_query, "research_results": research_results})