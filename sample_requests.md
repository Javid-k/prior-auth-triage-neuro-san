# Sample Authorization Requests

All data below is **synthetic**. No real patient data, PII, or confidential
information is used.

## Approve
> "72-year-old member on a Medicare Advantage plan requesting an MRI."

Expected: **FINAL: APPROVE** (rule R1)

## Route to human (no matching rule)
> "45-year-old on a PPO plan requesting acupuncture."

Expected: **FINAL: ROUTE TO HUMAN** — no rule covers this request, so it is escalated
rather than decided automatically.

## Deny
> "30-year-old requesting a cosmetic procedure."

Expected: **FINAL: DENY** (rule R3)

## Route to human (missing documentation)
> "55-year-old requesting a specialty drug with no step-therapy documentation."

Expected: **FINAL: ROUTE TO HUMAN** (rule R2)

## Route to human (high-cost service)
> "68-year-old on Medicare Advantage requesting proton therapy."

Expected: **FINAL: ROUTE TO HUMAN** (rule R5 — high-cost services require human sign-off)
