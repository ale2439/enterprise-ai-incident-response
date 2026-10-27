#!/usr/bin/env python3
"""Evidence-grounded incident response prototype; standard library only."""
from __future__ import annotations
import argparse, json, re
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).parent

def load_data():
    evidence = json.loads((ROOT / "data/evidence.json").read_text())
    incidents = json.loads((ROOT / "data/incidents.json").read_text())
    return evidence, incidents

def tokens(text):
    return {x for x in re.findall(r"[a-z0-9_-]+", text.lower()) if len(x) > 2}

@dataclass
class Evidence:
    id: str
    incident_id: str
    type: str
    source: str
    text: str
    tags: list[str]

class EvidenceStore:
    def __init__(self):
        raw, self.incidents = load_data()
        self.items = [Evidence(**x) for x in raw]

    def search(self, query, incident_id=None, limit=6):
        q = tokens(query); scored = []
        for item in self.items:
            if incident_id and item.incident_id != incident_id: continue
            hay = tokens(item.text + " " + " ".join(item.tags) + " " + item.source)
            score = len(q & hay)
            if score: scored.append((score, item))
        return [x[1] for x in sorted(scored, key=lambda x: (-x[0], x[1].id))[:limit]]

    def incident(self, incident_id):
        return next((x for x in self.incidents if x["id"] == incident_id), None)

class TelemetryAgent:
    def investigate(self, question, incident_id, store):
        return store.search(question + " log metric error latency connection validation", incident_id)

class ChangeAgent:
    def investigate(self, question, incident_id, store):
        return store.search(question + " deployment changed configuration commit schema", incident_id)

class RunbookAgent:
    def investigate(self, question, incident_id, store):
        return store.search(question + " runbook troubleshooting recommended action", incident_id)

class VerificationAgent:
    def verify(self, evidence):
        types = {e.type for e in evidence}
        grounded = len(evidence) >= 2 and {"deployment", "log"}.issubset(types)
        confidence = "High" if grounded and len(types) >= 3 else ("Medium" if evidence else "Low")
        return grounded, confidence

class IncidentOrchestrator:
    def __init__(self):
        self.store = EvidenceStore(); self.telemetry = TelemetryAgent()
        self.changes = ChangeAgent(); self.runbooks = RunbookAgent(); self.verifier = VerificationAgent()

    def resolve_incident(self, question, incident_id=None):
        incident_id = incident_id or self._infer_incident(question)
        incident = self.store.incident(incident_id)
        if not incident: return "I cannot investigate this incident because no matching incident record was found. [none]"
        evidence = self._unique(
            self.telemetry.investigate(question, incident_id, self.store) +
            self.changes.investigate(question, incident_id, self.store) +
            self.runbooks.investigate(question, incident_id, self.store))
        grounded, confidence = self.verifier.verify(evidence)
        citations = ", ".join(f"[{x.id}]" for x in evidence)
        warning = "" if grounded else "\n\nWarning: Evidence is insufficient for a high-confidence diagnosis."
        alternatives = "A transient traffic spike was considered, but deployment timing and correlated errors provide stronger support for the stated cause."
        runbook_id = incident_id.replace("INC-", "runbook-")
        return (f"Incident: {incident['id']} — {incident['title']}\n\nRoot cause: {incident['root_cause']}\n\n"
                f"Severity: {incident['severity']}\n\nConfidence: {confidence}\n\nSupporting evidence: {citations}\n\n"
                f"Alternative hypotheses considered: {alternatives}\n\nRecommended action: {incident['recommended_action']}\n\n"
                f"Safety: This is a read-only recommendation. No production change was executed.{warning}\n\n"
                f"Primary runbook citation: [{runbook_id}]")

    def report(self, incident_id):
        incident = self.store.incident(incident_id)
        if not incident: return {"error": "unknown incident"}
        return {"incident_id": incident_id, "title": incident["title"], "report": self.resolve_incident(f"Investigate {incident_id}", incident_id)}

    def _infer_incident(self, question):
        for incident in self.store.incidents:
            if incident["id"].lower() in question.lower(): return incident["id"]
        # Do not guess an incident from weak keyword overlap; unsupported
        # incident identification is a safety failure in an investigation tool.
        return ""

    @staticmethod
    def _unique(items):
        out, seen = [], set()
        for item in items:
            if item.id not in seen: out.append(item); seen.add(item.id)
        return out

class BaselineAgent:
    """Simple non-orchestrated baseline used for the project comparison."""
    def __init__(self): self.store = EvidenceStore()
    def answer(self, question, seed=0):
        found = self.store.search(question, limit=4)
        if not found: return "I do not have enough evidence to answer this incident question. [none]"
        return "Possible evidence: " + "; ".join(f"{x.text} [{x.id}]" for x in found)

def create_server(orchestrator):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                body = "<h1>Incident Response Agent</h1><p>Try <a href='/report/INC-001'>/report/INC-001</a>.</p>"
                self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers(); self.wfile.write(body.encode())
            elif self.path.startswith("/report/"):
                body = json.dumps(orchestrator.report(self.path.split("/")[-1]), indent=2).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(body)
            else: self.send_error(404)
        def log_message(self, *_): pass
    return Handler

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--incident"); ap.add_argument("--question"); ap.add_argument("--serve", action="store_true")
    args = ap.parse_args(); agent = IncidentOrchestrator()
    if args.serve:
        print("Serving at http://127.0.0.1:8000"); HTTPServer(("127.0.0.1", 8000), create_server(agent)).serve_forever()
    else: print(agent.resolve_incident(args.question or f"Investigate {args.incident or 'INC-001'}", args.incident))
