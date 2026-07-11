# Architecture Description

## Prior-Authorization Triage Assistant (Neuro SAN)

### 1. Problem

Health-insurance prior authorization requires deciding whether a requested medical
service should be approved, denied, or sent for human review. Automating this with a
single LLM is risky: the model may fabricate a decision it cannot justify, or produce
a confident answer for a case that policy says a human must handle. Both failures are
unacceptable in a regulated decisioning context.

### 2. Approach

The system decomposes the decision across four specialized agents and inserts a
governance gate that validates every outcome before it is returned. It uses a
**"rules as data"** pattern: the authorization logic lives in a data file
(`rules.json`) that a generic evaluator reads at runtime, rather than being hardcoded.
This separates policy (data) from mechanism (code) and lets the ruleset grow without
code changes.

### 3. Components

**Auth Coordinator (frontman agent)**
Entry point. Receives the free-text authorization request and orchestrates the chain:
extract fields, evaluate rules, review the result, and return the final verdict. It
does not make the decision itself.

**Extractor (agent)**
Parses the free-text request into structured fields: age, plan, service,
step-therapy documentation status, and requested visit count. It reports only what is
present and does not infer missing values.

**Rules Agent (agent) + RulesTool (coded tool)**
The Rules Agent calls `RulesTool`, a Python coded tool that loads `rules.json` and
evaluates the structured request against each rule. It returns a structured result
containing the decision, the reason (with the rule id), and the list of matched rules.

**Compliance Reviewer (governance agent)**
Validates the preliminary decision against governance policy. It confirms an
approve/deny only when a matching rule id justifies it, and escalates to human review
whenever there is no matching rule, a rule explicitly flagged for review, or a
conflict between matched rules. This is the control layer that prevents unjustified
automated decisions.

### 4. Decision & Escalation Logic

The `RulesTool` applies the following logic:

- **Exactly one clear outcome** → return that outcome (APPROVE or DENY) with the
  supporting rule id and rationale.
- **No rule matches** → ROUTE TO HUMAN (the system does not guess).
- **A matched rule is flagged for review** (e.g. high-cost services, missing required
  documentation) → ROUTE TO HUMAN.
- **Matched rules conflict** (one approves, one denies) → ROUTE TO HUMAN.

This mirrors how real payer systems auto-adjudicate clear cases while escalating
uncertain ones to human reviewers.

### 5. Rules as Data

Rules are stored as rows in `rules.json`, each with an id, a set of conditions, an
outcome, and a rationale. The evaluator matches a request against a rule's conditions
generically (supporting exact-match conditions plus `min_age` and
`max_requested_visits` range checks). Because the evaluation engine is independent of
the rule content, the ruleset can scale from a few rules to hundreds by adding data
rows — no code changes are required.

### 6. Agentic Capabilities

- **Multi-agent coordination** — four agents pass work along a defined chain.
- **Tool usage** — a coded Python tool is invoked by the Rules Agent.
- **Task planning** — the Coordinator decomposes the task into extract → evaluate → review.
- **Evaluation loop** — the Compliance Reviewer validates and gates every decision.

### 7. Data & Compliance

All rules and sample requests are synthetic. The system contains no PII, no real
medical records, and no confidential data. API keys are provided via environment
variables and are never stored in the repository.
