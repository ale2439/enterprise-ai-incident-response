from incident_response import IncidentOrchestrator

cases = [
    ("INC-001", ["5433", "log-001", "deploy-001"]),
    ("INC-002", ["key-2025", "log-002", "deploy-002"]),
    ("INC-003", ["one upstream request per item", "log-003", "deploy-003"]),
    ("INC-004", ["breaking phoneNumber schema", "log-004", "deploy-004"]),
]
agent = IncidentOrchestrator(); passed = 0
for incident, checks in cases:
    report = agent.resolve_incident(f"Investigate {incident}", incident)
    ok = all(x.lower() in report.lower() for x in checks) and "read-only" in report.lower()
    passed += int(ok); print(f"{incident}: {'PASS' if ok else 'FAIL'}")
print(f"Overall: {passed}/{len(cases)}")
