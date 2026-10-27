"""Homework 6 adapter compatible with the supplied evaluation gate.

The release manifest controls the response prompt version. Version v1 preserves
citations. The Part 5 candidate v2 deliberately weakens the citation
instruction so the gate can demonstrate a real BLOCK result.
"""
import json
from incident_response import IncidentOrchestrator

AGENT = IncidentOrchestrator()
MANIFEST = json.load(open("manifest.json", encoding="utf-8"))

def answer(question, seed=0):
    answer_text = AGENT.resolve_incident(question)
    if MANIFEST.get("prompt_version") == "v2":
        # Simulated prompt regression: the candidate still diagnoses incidents,
        # but omits the required final evidence citation.
        answer_text = answer_text.rsplit("\n\nPrimary runbook citation:", 1)[0]
    return answer_text
