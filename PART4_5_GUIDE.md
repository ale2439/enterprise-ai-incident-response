# Homework 6 Parts 4 and 5

## Part 4 CI gate

Part 4 is already implemented in `.github/workflows/eval-gate.yml`. It runs
`python eval_gate.py --gate` on every pull request and uploads `gate_report.json`.
The gate uses `max_drop_sigma: 3` and `max_token_increase: 0.20` from `manifest.json`.

Report sentence:

> The CI gate blocks a release when a quality category drops beyond three baseline standard deviations, a critical safety category fails, or average response tokens increase by more than 20 percent.

## Part 5 real change

The baseline release is `prompt_version: v1`, which preserves the primary runbook
citation. The prepared candidate changes the release to `prompt_version: v2`.
The candidate represents a real prompt change that produces a shorter answer but
removes the required final citation. The expected gate result is `BLOCK`.

### Create the pull request

From the clean baseline branch:

```bash
git checkout -b hw6-prompt-regression
cp candidate_v2/manifest.json manifest.json
git add manifest.json
git commit -m "Experiment with shorter incident response prompt"
git push -u origin hw6-prompt-regression
```

Open a pull request on GitHub. GitHub Actions will run the gate and should mark
the check as failed with a `BLOCK` verdict. Run the same test locally before
pushing:

```bash
python3 eval_gate.py --gate
cat gate_report.json
```

Record the pull-request URL and Actions run URL in the PDF report. A blocked
candidate is an acceptable Part 5 result because it demonstrates that the gate
prevented a regression in evidence grounding.
