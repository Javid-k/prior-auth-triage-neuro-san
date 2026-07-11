# Project Summary

## Prior-Authorization Triage Assistant

### What it is

A multi-agent AI system, built on the Neuro SAN framework, that triages medical
prior-authorization requests and returns one of three decisions: **APPROVE**,
**DENY**, or **ROUTE TO HUMAN**. Rather than relying on a single model to answer,
the system coordinates four specialized agents and validates every decision through a
governance gate before it is issued.

### The problem it solves

Prior authorization is the process by which a health insurer decides, before a service
is delivered, whether it will be covered. Automating this with a single LLM is risky
in two ways: the model can fabricate a decision it cannot justify, and it can
confidently answer cases that policy requires a human to handle. In a regulated
decisioning setting, both are unacceptable. This project is designed to prevent both:
decisions must be justified by an explicit rule, and any case that is uncovered or
ambiguous is escalated to a human instead of guessed.

### How it works

The workflow moves through four agents:

- **Auth Coordinator** orchestrates the request end to end.
- **Extractor** converts the free-text request into structured fields.
- **Rules Agent** calls a Python coded tool that evaluates those fields against a
  ruleset and returns a preliminary decision.
- **Compliance Reviewer** validates that decision against governance policy and forces
  escalation to human review for any uncovered, flagged, or conflicting case.

At the core is a **"rules as data"** design. Authorization rules are stored as data
rows in a JSON file, each with conditions, an outcome, and a rationale. A generic
evaluator reads and applies them at runtime. Because the logic is separated from the
data, the ruleset scales from a handful of rules to hundreds simply by adding rows —
with no changes to code.

### Why it is a meaningful use of agentic AI

The project demonstrates all four capabilities called for in the hackathon:

- **Multi-agent coordination:** four agents collaborate along a defined chain.
- **Tool usage:** the Rules Agent invokes a coded Python tool to evaluate rules.
- **Task planning:** the Coordinator decomposes the request into distinct stages.
- **Evaluation loop:** the Compliance Reviewer gates every decision, ensuring nothing
  is issued without justification.

The governance gate is the distinguishing element. Most single-agent assistants will
answer whatever they are asked; this system is explicitly built to know the limits of
what it is allowed to decide, and to escalate rather than fabricate. That property —
trustworthy, auditable automated decisioning with a human fallback — is exactly what
enterprise and regulated use cases require.

### Design perspective

The project also reflects a broader idea: a different approach to the kind of
decisioning traditionally handled by rules engines. A rules engine is deterministic
and auditable but rigid; a purely agentic system is flexible but less predictable.
This design combines them — deterministic rule evaluation for clear cases, agent
reasoning for interpreting messy input, and mandatory human escalation for anything
uncertain — pointing toward how flexible AI reasoning and reliable governance can work
together.

### Data & compliance

All rules and sample requests are synthetic. The system contains no PII, no real
medical records, and no confidential organizational data. LLM API keys are supplied
through environment variables and are never committed to the repository.
