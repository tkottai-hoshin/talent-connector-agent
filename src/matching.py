import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# ---------- State ----------
class AgentState(TypedDict):
    job_description: str
    job_start_date: str
    employees: List[dict]
    filtered_employees: List[dict]
    scored_employees: List[dict]
    final_results: List[dict]
    job_analysis: dict
    stage: str

# ---------- LLM ----------
llm = ChatOllama(model="llama3.2:3b", temperature=0.3, format="json")

# ---------- Nodes ----------
def analyze_job(state: AgentState):
    prompt = f"""
    Analyze this job description and extract key information.
    Return ONLY valid JSON with these keys:
    - required_skills (list)
    - preferred_skills (list)
    - min_experience_years (number)
    - key_responsibilities (list)
    - seniority_level (string)
    
    Job Description:
    {state['job_description']}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    analysis = json.loads(response.content)
    return {
        "job_analysis": analysis,
        "stage": "analyzed"
    }

def filter_candidates(state: AgentState):
    """Create a narrow shortlist"""
    filtered = state["employees"][:8]  # simple limit for speed
    
    return {
        "filtered_employees": filtered,
        "stage": "filtered"
    }

def score_candidates(state: AgentState):
    scored = []
    analysis = state.get("job_analysis", {})
    
    for emp in state["filtered_employees"]:
        prompt = f"""
You are an expert talent matcher.

Job Analysis: {json.dumps(analysis)}
Job Description: {state['job_description']}
Target Start Date: {state['job_start_date']}

Employee:
Name: {emp['name']}
Title: {emp['title']}
Level: {emp['level']}
Bio: {emp['bio']}
Skills: {', '.join(emp['skills'])}
Available From: {emp['available_from']}

Return ONLY valid JSON:
{{
  "overall_score": 0-100,
  "skills_score": 0-100,
  "experience_score": 0-100,
  "timeline_score": 0-100,
  "explanation": "2-3 sentences",
  "key_strengths": ["..."],
  "gaps": ["..."]
}}
"""
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            score_data = json.loads(response.content)
            scored.append({**emp, **score_data})
        except Exception as e:
            print(f"Error scoring {emp['name']}: {e}")
            continue
    
    return {
        "scored_employees": scored,
        "stage": "scored"
    }

def rank_and_finalize(state: AgentState):
    results = sorted(
        state["scored_employees"],
        key=lambda x: x.get("overall_score", 0),
        reverse=True
    )
    return {
        "final_results": results,
        "stage": "completed"
    }

# ---------- Build Graph ----------
workflow = StateGraph(AgentState)

workflow.add_node("analyze_job", analyze_job)
workflow.add_node("filter_candidates", filter_candidates)
workflow.add_node("score_candidates", score_candidates)
workflow.add_node("rank_and_finalize", rank_and_finalize)

workflow.set_entry_point("analyze_job")
workflow.add_edge("analyze_job", "filter_candidates")
workflow.add_edge("filter_candidates", "score_candidates")
workflow.add_edge("score_candidates", "rank_and_finalize")
workflow.add_edge("rank_and_finalize", END)

agent = workflow.compile()

# ---------- Helper functions ----------
def run_until_filtered(job_description: str, employees: list, job_start_date: str = None):
    """Run only until the shortlist is ready"""
    initial_state = {
        "job_description": job_description,
        "job_start_date": job_start_date or "",
        "employees": employees,
        "filtered_employees": [],
        "scored_employees": [],
        "final_results": [],
        "job_analysis": {},
        "stage": "start"
    }
    
    state = initial_state
    state.update(analyze_job(state))
    state.update(filter_candidates(state))
    return state

def continue_scoring(state: dict):
    """Continue from the filtered stage"""
    state.update(score_candidates(state))
    state.update(rank_and_finalize(state))
    return state
