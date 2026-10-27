# Enterprise AI Incident Response Agent

This repository contains a runnable, dependency-free prototype based on the project abstract.
It investigates controlled microservice incidents using specialized agents, retrieves supporting
evidence, verifies competing hypotheses, and produces a cited root-cause report.

## Run the demo

```bash
python3 run_demo.py --incident INC-001
python3 run_demo.py --incident INC-002 --baseline
python3 evaluate.py
python3 incident_response.py --serve
```

Open `http://127.0.0.1:8000` after starting the server.

The prototype is read-only: it recommends remediation but never changes, restarts, or rolls back
a service. Part 4 is already wired through `.github/workflows/eval-gate.yml`. Part 5 is prepared
in `candidate_v2/` and explained in `PART4_5_GUIDE.md`.
