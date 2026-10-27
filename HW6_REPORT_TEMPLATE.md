# Homework 6 LLMOps Pipeline Report

Team members: Alekya Gudise and Michael Kennedy  
Repository: **PASTE GITHUB REPOSITORY URL**  
Baseline commit: **PASTE BASELINE COMMIT**

## Part 4 CI gate

The repository runs `python eval_gate.py --gate` on every pull request through
`.github/workflows/eval-gate.yml`. The gate uses a maximum drop of three baseline
standard deviations and a maximum token increase of 20 percent. It blocks a
release if a critical category fails, quality drops beyond the configured limit,
or response length exceeds the configured limit.

## Part 5 real change

The candidate changes the incident-response prompt version from `v1` to `v2`.
The shorter candidate response omits the primary runbook citation. This is a
real release change because it changes the answer contract while leaving the
incident data and evaluator unchanged.

Pull request: **PASTE PULL REQUEST URL**  
CI run: **PASTE GITHUB ACTIONS RUN URL**

Expected verdict: **BLOCK**

Local candidate result:

```text
BLOCK
citation fell 100.0% with zero A/A noise
grounding fell 100.0% with zero A/A noise
overall fell 40.0% with zero A/A noise
root_cause fell 100.0% with zero A/A noise
```

The candidate is intentionally blocked because removing evidence citations
violates the project’s grounding requirement. The block is a successful result:
the gate prevented a lower-quality release from shipping.

## Evidence

Attach or link the `gate_report.json` artifact from the GitHub Actions run and
include a screenshot of the failed CI check showing the `BLOCK` result.
