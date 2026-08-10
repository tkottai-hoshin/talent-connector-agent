import streamlit as st
import json
from src.matching import run_until_filtered, continue_scoring
from datetime import date

st.set_page_config(page_title="AI Talent Connector", page_icon="🤝", layout="wide")

st.title("AI Talent Connector")
st.caption("Agentic matching of Accounting professionals with human-in-the-loop guardrail")

# Load employees
with open("data/employees.json", "r") as f:
    employees = json.load(f)

# Session state
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None
if "stage" not in st.session_state:
    st.session_state.stage = "input"

# Sidebar
with st.sidebar:
    st.header("New Staffing Opportunity")
    job_title = st.text_input("Job Title", value="Senior Accounting Professional")
    
    default_job = """We are looking for a Senior Accounting Professional to support a key client engagement in the manufacturing sector and contribute to internal finance initiatives.

Key responsibilities:
- Lead month-end and quarter-end close activities
- Prepare and review complex journal entries, reconciliations, and financial statements
- Ensure compliance with US GAAP and internal controls
- Support audit processes and provide documentation to external auditors
- Partner with business stakeholders to improve accounting processes and reporting
- Mentor junior accounting staff and review their work

Required qualifications:
- 6+ years of progressive accounting experience
- Strong knowledge of US GAAP, month-end close, and financial reporting
- Experience with ERP systems (preferably SAP, Oracle, or NetSuite)
- Excellent attention to detail and analytical skills
- Ability to start by October 1, 2026

Nice to have:
- CPA designation
- Experience in manufacturing or professional services environments
- Exposure to process improvement or systems implementation projects
- Advanced Excel and data analysis skills"""

    job_description = st.text_area("Job Description", value=default_job, height=350)
    job_start = st.date_input("Target Start Date", value=date(2026, 10, 1))
    
    run_matching = st.button("Find Best Matches", type="primary", use_container_width=True)

# Run until shortlist
if run_matching and job_description.strip():
    with st.spinner("Agent is analyzing the job and creating a shortlist..."):
        state = run_until_filtered(
            job_description=job_description,
            employees=employees,
            job_start_date=str(job_start)
        )
        st.session_state.agent_state = state
        st.session_state.stage = "filtered"
        st.rerun()

# Show Shortlist + Guardrail
if st.session_state.stage == "filtered" and st.session_state.agent_state:
    state = st.session_state.agent_state
    
    st.subheader("Narrow Shortlist (Guardrail)")
    st.info("The agent has created a shortlist. Review it before proceeding to deep scoring.")
    
    for i, emp in enumerate(state["filtered_employees"], 1):
        st.write(f"**{i}. {emp['name']}** — {emp['title']} | Available: {emp['available_from']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Proceed to Full Scoring", type="primary"):
            with st.spinner("Agent is performing deep evaluation..."):
                final_state = continue_scoring(state)
                st.session_state.agent_state = final_state
                st.session_state.stage = "completed"
                st.rerun()
    
    with col2:
        if st.button("↺ Start Over"):
            st.session_state.stage = "input"
            st.session_state.agent_state = None
            st.rerun()

# Final Results
if st.session_state.stage == "completed" and st.session_state.agent_state:
    results = st.session_state.agent_state["final_results"]
    
    st.subheader("Final Ranked Matches")
    
    for i, r in enumerate(results[:8], 1):
        with st.expander(f"#{i}  {r['name']}  —  {r.get('overall_score', 0)}% match  |  Available: {r['available_from']}", expanded=(i <= 3)):
            col1, col2, col3 = st.columns(3)
            col1.metric("Overall", f"{r.get('overall_score', 0)}%")
            col2.metric("Skills", f"{r.get('skills_score', 0)}%")
            col3.metric("Timeline", f"{r.get('timeline_score', 0)}%")
            
            st.markdown("**Explanation**")
            st.write(r.get("explanation", ""))
            
            st.markdown("**Key Strengths**")
            st.write(", ".join(r.get("key_strengths", [])))
            
            if r.get("gaps"):
                st.markdown("**Gaps**")
                st.write(", ".join(r["gaps"]))
