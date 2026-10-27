import argparse
from incident_response import IncidentOrchestrator, BaselineAgent

ap = argparse.ArgumentParser()
ap.add_argument('--incident', default='INC-001')
ap.add_argument('--baseline', action='store_true')
a = ap.parse_args()
if a.baseline:
    print(BaselineAgent().answer(f"Investigate {a.incident}"))
else:
    print(IncidentOrchestrator().resolve_incident(f"Investigate {a.incident}", a.incident))
