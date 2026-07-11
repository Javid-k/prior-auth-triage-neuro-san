Prior-Authorization Triage Assistant
A multi-agent AI system built on the Neuro SAN framework that triages medical
prior-authorization requests into APPROVE, DENY, or ROUTE TO HUMAN
decisions. The system demonstrates multi-agent coordination, tool usage, task
planning, and an evaluation/governance loop.
---
Participants
Participant #1: [YOUR NAME] — [YOUR EMPLOYEE ID]
---
Overview
In enterprise decisioning (such as health-insurance prior authorization), a single
LLM answering alone has two failure modes: it can fabricate a decision, and it can
answer cases it should not. This project addresses both by splitting the work across
specialized agents and adding a governance gate that validates every decision before
it is issued.
The system follows a "rules as data" design: authorization rules live in a data
file (`rules.json`), not in code. Adding or changing a rule means editing data, not
rewriting logic — the same evaluation engine scales from a handful of rules to
hundreds without code changes.
---
Architecture
The network consists of four agents coordinated in a chain:
Auth Coordinator (frontman) — receives the request and orchestrates the flow.
Extractor — pulls structured fields (age, plan, service, documentation,
requested visits) from the free-text request.
Rules Agent — calls the `RulesTool` coded tool, which evaluates the extracted
fields against the ruleset and returns a preliminary decision.
Compliance Reviewer (governance gate) — validates the preliminary decision.
Any case with no matching rule, a rule flagged for review, or conflicting rules is
escalated to human review rather than auto-decided.
```
User Request
     |
     v
Auth Coordinator ---> Extractor        (structured fields)
     |
     +-------------> Rules Agent ---> RulesTool (evaluates rules.json)
     |
     +-------------> Compliance Reviewer  (governance validation)
     |
     v
Final Verdict: APPROVE / DENY / ROUTE TO HUMAN
```
Capabilities demonstrated
Multi-agent coordination: four agents pass work along a defined chain.
Tool usage: the Rules Agent invokes a Python coded tool (`RulesTool`).
Task planning: the Coordinator decomposes the request into extract → evaluate → review.
Evaluation loop: the Compliance Reviewer gates every decision and forces
escalation on uncovered or ambiguous cases.
---
Project Structure
```
registries/
  prior_auth.hocon          # Agent network definition (4 agents)
  manifest.hocon            # Registers prior_auth.hocon with the server
coded_tools/
  prior_auth/
    rules_tool.py           # Coded tool: evaluates a request against rules.json
    rules.json              # Authorization rules (data, not code)
sample_requests.md          # Example requests for demonstration
architecture.md             # Architecture description
summary.md                  # Project summary
requirements.txt            # Python dependencies
README.md                   # This file
```
---
Setup & Run
This project runs inside Neuro SAN Studio
(https://github.com/cognizant-ai-lab/neuro-san-studio).
Place the project files into a Neuro SAN Studio checkout:
`prior_auth.hocon` → `registries/`
`rules_tool.py` and `rules.json` → `coded_tools/prior_auth/`
Ensure `registries/manifest.hocon` contains the entry: `"prior_auth.hocon": true,`
Create and activate a virtual environment, then install dependencies:
```
   python -m venv venv
   venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   pip install langchain-mistralai
   ```
Set your LLM provider API key as an environment variable (Mistral shown):
```
   set MISTRAL_API_KEY=<your-key>   # Windows
   ```
Start the server from the project root:
```
   python -m neuro_san_studio run
   ```
Open the UI at `http://localhost:4173/`, select the prior_auth network, and
submit a request.
---
Usage Examples
"72-year-old member on a Medicare Advantage plan requesting an MRI."
→ APPROVE (rule R1)
"45-year-old on a PPO plan requesting acupuncture."
→ ROUTE TO HUMAN (no rule covers this — the system does not guess)
"30-year-old requesting a cosmetic procedure."
→ DENY (rule R3)
"55-year-old requesting a specialty drug with no step-therapy documentation."
→ ROUTE TO HUMAN (rule R2)
All data used is synthetic. No real patient data, PII, or confidential
information is included.
---
Configuration Notes
The LLM provider is configured in the `llm_config` block at the top of
`prior_auth.hocon`. The example uses Mistral (`mistral-medium-latest`); any
function-calling-capable provider supported by Neuro SAN can be substituted by
changing the `class` and `model_name`.
API keys are supplied via environment variables and are never committed to the
repository.
