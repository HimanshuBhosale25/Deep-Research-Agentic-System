import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from typing import List, Dict, Any
from deep_research_agent.workflow import create_research_answer_workflow, AgentState
from deep_research_agent.agents import (
    ResearcherAgentWrapper,
    AnswerDraftingAgentWrapper,
    researcher_chain,
    answer_chain,
)
from langchain_core.messages import HumanMessage

app = FastAPI(title="Deep Research Agent API")

origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    query: str
    research_results: List[Dict[str, Any]]
    drafted_answer: str

@app.post("/research/", response_model=ResearchResponse)
async def perform_research(request: ResearchRequest):
    user_query = request.query

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

    try:
        result = workflow.invoke(inputs)
        return ResearchResponse(
            query=user_query,
            research_results=result["research_results"],
            drafted_answer=result["drafted_answer"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)