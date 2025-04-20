from langchain_core.messages import HumanMessage

from .workflow import create_research_answer_workflow, AgentState
from .agents import (
    llm,
    researcher_chain,
    answer_chain,
    ResearcherAgentWrapper,
    AnswerDraftingAgentWrapper,
)

def main():
    user_query = "What are the main challenges in developing a safe and reliable self-driving car?"

    researcher_agent = ResearcherAgentWrapper(chain=researcher_chain)
    answer_drafting_agent = AnswerDraftingAgentWrapper(chain=answer_chain)

    workflow = create_research_answer_workflow()

    inputs: AgentState = {
    "user_query": user_query,
    "research_results": [],  
    "drafted_answer": "",
    "messages": [HumanMessage(content=user_query)],
    "researcher_agent": researcher_agent,
    "answer_drafting_agent": answer_drafting_agent,
}

    result = workflow.invoke(inputs)

    print(f"Query: {user_query}")
    print(f"Research Results:\n{result['research_results']}")
    print(f"\nDrafted Answer:\n{result['drafted_answer']}")

if __name__ == "__main__":
    main()