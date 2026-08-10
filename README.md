<img width="2914" height="92" alt="image" src="https://github.com/user-attachments/assets/733c6a77-2f48-4160-94cd-b8e9a41e7a45" />

2-Step workflow for a Talent & Workforce lead to source candidates



Step #1: Enter the job description. 
<img width="2914" height="1274" alt="image" src="https://github.com/user-attachments/assets/5697c0a0-502b-4ffe-9fbf-52a705a9a91b" />

Node 1 - Analyze & Filter

The Talent Connector Agent will process the data in the first graph node, which will analyze_job() description and filter_candidates() that have applied to the role. 

In the first guardrail, the Talent & Workforce lead is analyzing the first pass of candidates in this workflow. You don't have to put in this Guardrail. All it does is it just makes sure the Talent & Workforce lead is analyzing the candidate backgrounds before ranking them in the next step. 
<img width="2914" height="1274" alt="image" src="https://github.com/user-attachments/assets/8e1fa3e9-842b-403b-8f78-76e40461c388" />


Step #2: Talent & Workforce Lead is satisfied with the first pass, next Click "Proceed to Full Scoring". 

Node 2 - Score & Rank
  
<img width="2914" height="1388" alt="image" src="https://github.com/user-attachments/assets/f8105336-3241-49b3-8cb9-5cd2d2412c5b" />

This analysis is focused on key word relevance, direct working experience, skills match, and availability / timeline alignment. 

The Talent & Workforce lead is able to score_candidates() rank_and_finalize() to build a report. The decision analytics engine can be modified to add more filters to qualify candidates further. This can be done by embedding new Nodes to analyze Resume, Cover Letter, Workforce System Candidate Bio / Intro Statement + Added Skills + Availability + Leveling + Years of Experience + Rate Card + Internal vs External Candidate + other signals)


Why This Design?

- Agentic workflow instead of a single LLM call
- Human-in-the-loop control after the first filtering stage
- Easily extensible, new nodes can be added to incorporate additional data sources

<img width="1064" height="758" alt="image" src="https://github.com/user-attachments/assets/7c9390dc-ed22-46da-a276-107afd239ccb" />


Data Storage:

Currently the system uses local storage. The architecture is modular so it can be easily extended to connect through API with real Workforce Management, HCM systems or HRIS platforms.



