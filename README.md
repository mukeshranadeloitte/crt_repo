# Salesforce UAT CI/CD Pipeline

End-to-end GitHub Actions pipeline for Salesforce projects — covering PR validation, security scanning, architect-gated deployment, and robotic test execution.

---

## What This Repository Contains

| Path | Description |
|------|-------------|
| `.github/workflows/e2e-uat-pipeline.yml` | Main GitHub Actions workflow (all 7 jobs) |
| `.github/sf-scanner-waivers.csv` | Time-boxed SCA violation waivers (main branch only) |
| `docs/` | Architecture, setup, runbook, troubleshooting, waiver governance |
| `create-e2e-uat-pipeline.prompt.md` | Copilot Agent prompt — generate pipeline for a new project |
| `e2e-uat-pipeline.agent.md` | Copilot Agent knowledge base for the pipeline |
| `ado-pipelines/` | Azure DevOps equivalent pipeline + interactive setup script |
| `jenkins/` | Jenkins equivalent pipeline + interactive setup script |
| `force-app/` | Salesforce source (DX format) |

---

## Pipeline at a Glance

```
PR opened/updated → [1] setup (detect scanners)
                  → [2] salesforce-validation (delta deploy + SCA + coverage)
                  → [3] checkmarx-sast        (if CX secret set)
                  → [4] fortify-sast-dast      (if FOD secret set)

PR approved       → [5] approval-merge-gate   (stale check + architect gate + AUTO-MERGE)
                  → [6] deploy-after-merge     (deploy from merge commit to UAT org)
                  → [7] trigger-crt-tests      (Copado Robotic Testing)
```

**Key behaviours:**
- Delta-based deployments — only changed components are deployed
- PR is merged **automatically** after architect approval (no manual merge)
- Apex test coverage enforced during PR validation (threshold: 85% default)
- SF Code Analyzer violations are waivable with expiry dates
- `DELTA_FROM_COMMIT` auto-updated after every successful deploy

---

## Quick Start

### For a new project — GitHub Actions

Open `create-e2e-uat-pipeline.prompt.md` in **Copilot Agent mode** and follow the interactive questions.

### For a new project — Azure DevOps

```bash
python3 ado-pipelines/setup.py
# Select mode 1 for full pipeline
```

### For a new project — Jenkins

```bash
python3 jenkins/setup.py
# Select mode 1 for full pipeline
```

### To add only specific jobs to an existing pipeline

```bash
python3 ado-pipelines/setup.py  # select mode 2 — module snippets
python3 jenkins/setup.py        # select mode 2 — module snippets
```

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [`docs/pipeline-overview.md`](docs/pipeline-overview.md) | Architecture + job summary |
| [`docs/pipeline-flow.md`](docs/pipeline-flow.md) | Detailed mermaid flow diagrams |
| [`docs/pipeline-setup.md`](docs/pipeline-setup.md) | Secrets, variables, prerequisites |
| [`docs/sca-waivers.md`](docs/sca-waivers.md) | Waiver governance + schema |
| [`docs/manual_runbook.md`](docs/manual_runbook.md) | Approval runbook for reviewers |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Common errors + fixes |
| [`ado-pipelines/SETUP.md`](ado-pipelines/SETUP.md) | ADO pipeline setup guide |
| [`jenkins/SETUP.md`](jenkins/SETUP.md) | Jenkins pipeline setup guide |

---

## Branch & Approval Model

| Branch | PR reviewers required | Architect approval required |
|--------|----------------------|-----------------------------|
| `uat` | Yes — any code reviewer | No |
| `main` | Yes — any code reviewer | **Yes** — `chorevathi-deloitte` or `mukeshranadeloitte` |

Architects: `chorevathi-deloitte`, `mukeshranadeloitte`

CODEOWNERS: `.github/CODEOWNERS`

’’


