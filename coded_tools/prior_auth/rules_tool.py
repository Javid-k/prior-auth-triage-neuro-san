"""
Prior-Authorization Rules Evaluator (Neuro SAN Coded Tool)

Implements the 'rules as data' pattern: decisions are NOT hardcoded in Python.
The tool loads rules.json and evaluates a request against each rule generically.
Adding a rule means adding a row to rules.json, not editing this code.

Escalation logic (the governance core):
  - No rule matches            -> route_human
  - A matched rule demands it   -> route_human (high-cost, missing docs)
  - Multiple rules conflict     -> route_human
  - Exactly one clear outcome   -> approve / deny
"""

import json
import os
from typing import Any, Dict, List

from neuro_san.interfaces.coded_tool import CodedTool

RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.json")


def _matches(request: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
    """Return True if the request satisfies every condition in a rule."""
    for key, expected in conditions.items():
        if key == "min_age":
            if request.get("age") is None or request["age"] < expected:
                return False
        elif key == "max_requested_visits":
            if request.get("requested_visits") is None or request["requested_visits"] > expected:
                return False
        else:
            if request.get(key) != expected:
                return False
    return True


class RulesTool(CodedTool):
    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> str:
        request = {
            "age": args.get("age"),
            "plan": args.get("plan"),
            "service": args.get("service"),
            "step_therapy_documented": args.get("step_therapy_documented"),
            "requested_visits": args.get("requested_visits"),
        }

        try:
            with open(RULES_PATH, "r", encoding="utf-8") as f:
                rules: List[Dict[str, Any]] = json.load(f)
        except FileNotFoundError:
            return json.dumps({
                "decision": "route_human",
                "reason": "SOURCE_MISSING: rules.json not found; cannot auto-adjudicate.",
                "matched_rules": []
            })

        matched = [r for r in rules if _matches(request, r["conditions"])]

        if not matched:
            return json.dumps({
                "decision": "route_human",
                "reason": "NO_MATCH: no rule covers this request; escalating to human review.",
                "matched_rules": []
            })

        outcomes = {r["outcome"] for r in matched}

        if "approve" in outcomes and "deny" in outcomes:
            return json.dumps({
                "decision": "route_human",
                "reason": "CONFLICT: matched rules disagree; escalating to human review.",
                "matched_rules": [r["id"] for r in matched]
            })

        if "route_human" in outcomes:
            r = next(x for x in matched if x["outcome"] == "route_human")
            return json.dumps({
                "decision": "route_human",
                "reason": f"{r['id']}: {r['rationale']}",
                "matched_rules": [x["id"] for x in matched]
            })

        r = matched[0]
        return json.dumps({
            "decision": r["outcome"],
            "reason": f"{r['id']}: {r['rationale']}",
            "matched_rules": [x["id"] for x in matched]
        })
