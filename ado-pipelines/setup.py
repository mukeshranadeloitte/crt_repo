#!/usr/bin/env python3
"""
Salesforce ADO Pipeline Generator
===================================
Interactive setup script that generates a customized Azure DevOps pipeline YAML
for a Salesforce project.

Modes
-----
1. Full pipeline  — generates complete ADO pipeline YAMLs from scratch.
2. Module snippets — generates only the individual job(s) you need,
                     ready to paste into an existing ADO pipeline YAML.

Usage:
    python3 ado-pipelines/setup.py

Output (full pipeline mode):
    ado-pipelines/generated/e2e-pipeline.yml
    ado-pipelines/generated/update-delta-on-push.yml
    ado-pipelines/generated/variable-checklist.md

Output (module snippet mode):
    ado-pipelines/generated/modules/<module>-job.yml
    ado-pipelines/generated/modules/integration-guide.md
"""

import os
import sys
import re
import textwrap
from datetime import date

# ── colour helpers ────────────────────────────────────────────────────────────
def bold(t):    return f"\033[1m{t}\033[0m"
def green(t):   return f"\033[32m{t}\033[0m"
def yellow(t):  return f"\033[33m{t}\033[0m"
def cyan(t):    return f"\033[36m{t}\033[0m"
def red(t):     return f"\033[31m{t}\033[0m"
def dim(t):     return f"\033[2m{t}\033[0m"

def ask(question, default="", required=False, hint=""):
    """Prompt the user for input, showing the default value."""
    default_hint = f" {dim(f'[default: {default}]')}" if default else ""
    hint_str     = f"\n  {dim(hint)}" if hint else ""
    prompt       = f"\n{bold(question)}{default_hint}{hint_str}\n  > "
    while True:
        answer = input(prompt).strip()
        if not answer:
            if default:
                return default
            if required:
                print(red("  ✗ This field is required. Please enter a value."))
                continue
        return answer

def ask_list(question, default, hint=""):
    """Prompt for a comma-separated list, returns a Python list."""
    raw = ask(question, default=", ".join(default) if isinstance(default, list) else default, hint=hint)
    return [x.strip() for x in raw.split(",") if x.strip()]

def ask_yes_no(question, default="yes"):
    """Yes/No prompt."""
    opts = "(Y/n)" if default.lower() == "yes" else "(y/N)"
    prompt = f"\n{bold(question)} {dim(opts)}\n  > "
    while True:
        answer = input(prompt).strip().lower()
        if not answer:
            return default.lower() == "yes"
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print(red("  ✗ Please enter y or n."))

def section(title):
    print(f"\n{cyan('─' * 62)}")
    print(f"{cyan('  ' + title)}")
    print(f"{cyan('─' * 62)}")

# ─────────────────────────────────────────────────────────────────────────────
# ADO MODULE SNIPPETS
# ─────────────────────────────────────────────────────────────────────────────

ADO_MODULES = {
    "sca": {
        "name":        "Salesforce Code Analyzer (SCA)",
        "description": "sf scanner run + waiver check + PR comment (paste into an existing job)",
        "variables":   ["ADO_PAT — Pipeline variable (secret) — Azure DevOps PAT with Pull Request R/W",
                        "GITHUB_REPO (owner/repo) — Pipeline variable"],
        "snippet": """\
# ═══════════════════════════════════════════════════════════════════════
# MODULE: Salesforce Code Analyzer (SCA)
# ═══════════════════════════════════════════════════════════════════════
# PREREQUISITES:
#   ADO Variable Group (or pipeline variables):
#     ADO_PAT     : Azure DevOps PAT — Pull Requests: Read & Write
#     GITHUB_REPO : owner/repo       — e.g. myorg/my-sf-repo
#   SCA_ENFORCEMENT_MODE pipeline variable: enforce | warn | off
#
# Paste this 'job' block inside your existing:
#   jobs:
#     - job: YourExistingJob
#       steps:
#         - ... (existing steps)
# ───────────────────────────────────────────────────────────────────────

- job: SalesforceCodeAnalyzer
  displayName: 'Salesforce Code Analyzer'
  condition: eq(variables['Build.Reason'], 'PullRequest')
  continueOnError: true
  variables:
    SCA_ENFORCEMENT_MODE: 'enforce'         # override per-pipeline if needed
    GITHUB_REPO: '{github_repo}'
  steps:
    - checkout: self
      fetchDepth: 0

    - task: NodeTool@0
      displayName: 'Install Node.js'
      inputs:
        versionSpec: '18.x'

    - script: |
        npm install --global @salesforce/cli --quiet
        echo y | sf plugins install @salesforce/sfdx-scanner 2>/dev/null || true
      displayName: 'Install Salesforce CLI + Scanner'

    - script: |
        set -euo pipefail
        if [ "$SCA_ENFORCEMENT_MODE" = "off" ]; then
          echo "##[warning]SCA_ENFORCEMENT_MODE=off — skipping"; exit 0
        fi
        BASE=$(git merge-base HEAD "origin/$(System.PullRequest.TargetBranchName)" 2>/dev/null || echo "HEAD~1")
        CHANGED=$(git diff --name-only "$BASE" HEAD | grep -E '\\.(cls|trigger|js|html|css)$' | tr '\\n' ',' | sed 's/,$//' || true)
        if [ -z "$CHANGED" ]; then echo "No SF files changed — skip"; exit 0; fi
        sf scanner run --target "$CHANGED" --format csv --outfile sfdx-report.csv --severity-threshold 3 || true
        # Fetch waivers
        curl -sS -H "Authorization: Bearer $(ADO_PAT)" \\
          "https://api.github.com/repos/$GITHUB_REPO/contents/.github/sf-scanner-waivers.csv?ref=main" \\
          | python3 -c "import sys,json,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())" \\
          > fetched-waivers.csv 2>/dev/null || touch fetched-waivers.csv
        TODAY=$(date +%Y-%m-%d); FAIL=false
        if [ -f sfdx-report.csv ]; then
          while IFS=',' read -r rule file line col sev msg url; do
            [ "$rule" = "Rule" ] || [ -z "$rule" ] && continue
            WAIVED=false
            while IFS=',' read -r w_rule w_file _ _ w_expiry _ _ _ _ w_status; do
              [ "$w_rule" = "rule" ] && continue; [ "$w_status" != "ACTIVE" ] && continue
              RM=false; FM=false
              { [ -z "$w_rule" ] || echo "$rule" | grep -qi "$w_rule"; } && RM=true
              { [ -z "$w_file" ] || echo "$file" | grep -qi "$w_file"; } && FM=true
              if $RM && $FM; then
                if echo "$w_expiry" | grep -qE '^[0-9]{{2}}-[0-9]{{2}}-[0-9]{{4}}$'; then
                  EXP="${{w_expiry:6:4}}-${{w_expiry:3:2}}-${{w_expiry:0:2}}"
                else EXP="$w_expiry"; fi
                [[ "$EXP" < "$TODAY" ]] && echo "##[warning]EXPIRED WAIVER: $rule — $file" || WAIVED=true
                break
              fi
            done < fetched-waivers.csv
            $WAIVED || echo "##[warning]VIOLATION: $rule — $file:$line — $msg"
          done < sfdx-report.csv
        fi
      displayName: 'Run SCA + Waiver Check'

    - publish: sfdx-report.csv
      artifact: sfdx-report
      displayName: 'Upload SCA report'
      condition: always()
""",
    },
    "apex-validation": {
        "name":        "Apex PR Validation (delta + check-only deploy + coverage)",
        "description": "Delta build, validate-only deploy, enforce coverage threshold",
        "variables":   ["CRT_UAT_AUTHURL — Pipeline variable (secret) — SFDX Auth URL"],
        "snippet": """\
# ═══════════════════════════════════════════════════════════════════════
# MODULE: Apex PR Validation
# ═══════════════════════════════════════════════════════════════════════
# PREREQUISITES:
#   ADO Variable Group:
#     CRT_UAT_AUTHURL     : SFDX Auth URL (secret)
#   Pipeline variables:
#     ORG_ALIAS           : e.g. uat
#     COVERAGE_THRESHOLD  : e.g. 85
#     DELTA_FROM_COMMIT   : baseline commit SHA
#
# Paste this 'job' block inside your  jobs:  section.
# ═══════════════════════════════════════════════════════════════════════

- job: ApexPRValidation
  displayName: 'Apex PR Validation'
  condition: eq(variables['Build.Reason'], 'PullRequest')
  variables:
    ORG_ALIAS: '{org_alias}'
    COVERAGE_THRESHOLD: '{coverage_threshold}'
  steps:
    - checkout: self
      fetchDepth: 0

    - task: NodeTool@0
      displayName: 'Install Node.js'
      inputs:
        versionSpec: '18.x'

    - script: |
        npm install --global @salesforce/cli --quiet
        echo y | sf plugins install sfdx-git-delta 2>/dev/null || true
      displayName: 'Install Salesforce CLI + sfdx-git-delta'

    - script: |
        set -euo pipefail
        printf '%s' '$(CRT_UAT_AUTHURL)' > sfdxAuthUrl.txt
        sf org login sfdx-url --sfdx-url-file sfdxAuthUrl.txt --alias "$(ORG_ALIAS)" --set-default
        rm -f sfdxAuthUrl.txt
        BASE=$(git merge-base HEAD "origin/$(System.PullRequest.TargetBranchName)" 2>/dev/null || echo "$(DELTA_FROM_COMMIT)")
        sf sgd:source:delta --to HEAD --from "$BASE" --output-dir . --source-dir force-app/
        HAS_DELTA=false
        grep -q '<members>' package/package.xml 2>/dev/null && HAS_DELTA=true
        if [ "$HAS_DELTA" = "false" ]; then echo "No delta — skip"; exit 0; fi
        DEPLOY_OUTPUT=$(sf project deploy validate --target-org "$(ORG_ALIAS)" --manifest package/package.xml --async --json)
        JOB_ID=$(echo "$DEPLOY_OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{{}}).get('id',''))")
        ELAPSED=0
        while true; do
          STATUS_JSON=$(sf project deploy report --job-id "$JOB_ID" --json 2>/dev/null || echo '{{}}')
          STATUS=$(echo "$STATUS_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{{}}).get('status','Unknown'))")
          printf "  %4ds  %s\\n" "$ELAPSED" "$STATUS"
          echo "$STATUS" | grep -qiE '^(Succeeded|Failed|Canceled)' && break
          sleep 15; ELAPSED=$((ELAPSED+15))
        done
        echo "$STATUS" | grep -qi "^Failed" && {{ echo "##[error]Validation failed"; exit 1; }} || true
        echo "✅ Validation passed"
      displayName: 'Delta Deploy Validate'
""",
    },
    "crt-tests": {
        "name":        "CRT Test Trigger (Copado Robotic Testing)",
        "description": "Trigger CRT job via GraphQL, poll result",
        "variables":   ["CRT_API_TOKEN — Pipeline variable (secret) — Copado External PAT",
                        "CRT_JOB_ID, CRT_PROJECT_ID, CRT_ORG_ID — Pipeline variables"],
        "snippet": """\
# ═══════════════════════════════════════════════════════════════════════
# MODULE: CRT Test Trigger (Copado Robotic Testing)
# ═══════════════════════════════════════════════════════════════════════
# PREREQUISITES:
#   ADO Variable Group:
#     CRT_API_TOKEN  : Copado External PAT (secret)
#   Pipeline variables:
#     CRT_JOB_ID     : e.g. 115686
#     CRT_PROJECT_ID : e.g. 73283
#     CRT_ORG_ID     : e.g. 43532
#
# Paste this 'job' block inside your  jobs:  section.
# ═══════════════════════════════════════════════════════════════════════

- job: CRTTests
  displayName: 'CRT Test Trigger'
  variables:
    CRT_JOB_ID:     '{crt_job_id}'
    CRT_PROJECT_ID: '{crt_project_id}'
    CRT_ORG_ID:     '{crt_org_id}'
  steps:
    - script: |
        set -euo pipefail
        TRIGGER=$(curl -sS -X POST \\
          -H "Content-Type: application/json" \\
          -H "X-Authorization: $(CRT_API_TOKEN)" \\
          "https://graphql.eu-robotic.copado.com/v1" \\
          -d '{{"query":"mutation {{ createBuild(projectId: \\"$(CRT_PROJECT_ID)\\", jobId: \\"$(CRT_JOB_ID)\\") {{ id status }} }}"}}')
        BUILD_ID=$(echo "$TRIGGER" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{{}}).get('createBuild',{{}}).get('id',''))")
        [ -z "$BUILD_ID" ] && {{ echo "##[warning]CRT trigger failed"; exit 0; }}
        echo "CRT Build ID: $BUILD_ID"
        ELAPSED=0
        while true; do
          POLL=$(curl -sS -X POST \\
            -H "Content-Type: application/json" \\
            -H "X-Authorization: $(CRT_API_TOKEN)" \\
            "https://graphql.eu-robotic.copado.com/v1" \\
            -d '{{"query":"query {{ latestBuilds(projectId: \\"$(CRT_PROJECT_ID)\\", resultSize: 10) {{ id status }} }}"}}')
          STATUS=$(echo "$POLL" | python3 -c "
import sys,json
data=json.load(sys.stdin).get('data',{{}}).get('latestBuilds',[])
bid='$BUILD_ID'
print(next((b['status'] for b in data if b.get('id')==bid),''))")
          printf "  %4ds  CRT: %s\\n" "$ELAPSED" "$STATUS"
          echo "$STATUS" | grep -qiE '^(passed|failed|error|cancelled|skipped)' && break
          sleep 30; ELAPSED=$((ELAPSED+30))
          [ "$ELAPSED" -ge 1800 ] && {{ echo "##[warning]CRT polling timed out"; break; }}
        done
        echo "CRT Result: $STATUS"
      displayName: 'CRT Trigger & Poll'
      env:
        CRT_API_TOKEN: $(CRT_API_TOKEN)
""",
    },
    "architect-gate": {
        "name":        "Architect Approval Gate",
        "description": "ADO Environment approval gate — only architects can approve deployment to main",
        "variables":   ["ADO Environment with approval check (Manual only — cannot be scripted)"],
        "snippet": """\
# ═══════════════════════════════════════════════════════════════════════
# MODULE: Architect Approval Gate (ADO Environment)
# ═══════════════════════════════════════════════════════════════════════
# PREREQUISITES — Manual setup (cannot be scripted):
#   1. In Azure DevOps → Pipelines → Environments:
#      Create an environment named: '{env_name}'
#   2. In the environment → Approvals and checks → + (Add check):
#      Type: Approvals
#      Approvers: Add each architect user/group
#      Instructions: "Architect approval required before deployment"
#   3. The deployment job below will pause until an architect approves.
#
# Paste the entire  stage:  block into your pipeline YAML under  stages:
# ═══════════════════════════════════════════════════════════════════════

- stage: ArchitectGate
  displayName: 'Architect Approval Gate'
  dependsOn: PRValidation        # change to your preceding stage name
  condition: |
    and(
      succeeded(),
      ne(variables['Build.Reason'], 'PullRequest'),
      eq(variables['Build.SourceBranchName'], '{deploy_branch}')
    )
  jobs:
    - deployment: AwaitArchitectApproval
      displayName: 'Await Architect Approval'
      environment: '{env_name}'   # <-- this triggers the approval check configured above
      strategy:
        runOnce:
          deploy:
            steps:
              - script: echo "✅ Architect approved — proceeding to deployment"
                displayName: 'Approval confirmed'
""",
    },
    "checkmarx": {
        "name":        "CheckMarx AST Scan",
        "description": "SAST security scan via CheckMarx AST task",
        "variables":   ["CX_BASE_URI, CX_TENANT, CX_CLIENT_ID, CX_CLIENT_SECRET — Pipeline variables"],
        "snippet": """\
# ═══════════════════════════════════════════════════════════════════════
# MODULE: CheckMarx AST Scan
# ═══════════════════════════════════════════════════════════════════════
# PREREQUISITES:
#   ADO Marketplace extension: Checkmarx AST (install from marketplace)
#   Pipeline variables (secrets):
#     CX_BASE_URI      : CheckMarx server URL
#     CX_TENANT        : CheckMarx tenant
#     CX_CLIENT_ID     : OAuth client ID
#     CX_CLIENT_SECRET : OAuth client secret
#
# Paste this 'job' block inside your  jobs:  section.
# ═══════════════════════════════════════════════════════════════════════

- job: CheckMarxScan
  displayName: 'CheckMarx AST SAST'
  condition: eq(variables['Build.Reason'], 'PullRequest')
  steps:
    - checkout: self

    # Option A — CheckMarx ADO extension (install from marketplace):
    # - task: CheckMarxASTScanner@2
    #   inputs:
    #     CxBaseURI: $(CX_BASE_URI)
    #     CxTenant:  $(CX_TENANT)
    #     ...

    # Option B — CheckMarx CLI:
    - script: |
        echo "Configure with CheckMarx ADO extension or CLI."
        echo "Credentials available: CX_BASE_URI=$(CX_BASE_URI)"
      displayName: 'CheckMarx Scan (configure per your org setup)'
      env:
        CX_CLIENT_SECRET: $(CX_CLIENT_SECRET)
""",
    },
    "fortify": {
        "name":        "Fortify on Demand SAST/DAST",
        "description": "Security scan via Fortify FoD ADO task",
        "variables":   ["FOD_CLIENT_ID, FOD_CLIENT_SECRET, FOD_APP_NAME, FOD_RELEASE_NAME — Pipeline variables",
                        "FOD_URL — Pipeline variable"],
        "snippet": """\
# ═══════════════════════════════════════════════════════════════════════
# MODULE: Fortify on Demand SAST/DAST
# ═══════════════════════════════════════════════════════════════════════
# PREREQUISITES:
#   ADO Marketplace extension: Fortify on Demand (install from marketplace)
#   Pipeline variables (secrets):
#     FOD_CLIENT_ID     : FoD OAuth client ID
#     FOD_CLIENT_SECRET : FoD OAuth client secret
#     FOD_APP_NAME      : Application name in Fortify
#     FOD_RELEASE_NAME  : Release name in Fortify
#   Pipeline variable:
#     FOD_URL           : FoD instance URL
#
# Paste this 'job' block inside your  jobs:  section.
# ═══════════════════════════════════════════════════════════════════════

- job: FortifyScan
  displayName: 'Fortify SAST/DAST'
  condition: eq(variables['Build.Reason'], 'PullRequest')
  steps:
    - checkout: self

    # Option A — Fortify on Demand ADO extension:
    # - task: FortifyOnDemandStatic@8
    #   inputs:
    #     FodConnection: 'MyFortifyServiceConnection'
    #     ...

    # Option B — fcli CLI:
    - script: |
        echo "Configure with Fortify FoD ADO extension or fcli."
        echo "App: $(FOD_APP_NAME) | Release: $(FOD_RELEASE_NAME)"
      displayName: 'Fortify Scan (configure per your org setup)'
      env:
        FOD_CLIENT_SECRET: $(FOD_CLIENT_SECRET)
""",
    },
}


def ask_ado_modules():
    print(f"\n{bold('Available modules:')}\n")
    keys = list(ADO_MODULES.keys())
    for i, k in enumerate(keys, 1):
        m = ADO_MODULES[k]
        print(f"  {cyan(str(i)+'.'):5} {bold(m['name'])}")
        print(f"        {dim(m['description'])}\n")
    print(f"  {cyan('all')}  — generate all modules\n")
    raw = input(bold("Which modules? (numbers comma-separated, or 'all')") + "\n  > ").strip()
    if raw.lower() in ("all", ""):
        return keys
    selected = []
    for token in raw.split(","):
        t = token.strip()
        if t.isdigit() and 1 <= int(t) <= len(keys):
            selected.append(keys[int(t) - 1])
        elif t in keys:
            selected.append(t)
    return selected or keys


def generate_ado_module_mode():
    print(f"\n{bold(cyan('ADO Module Snippet Generator'))}")
    print(dim("Generates self-contained ADO YAML job/stage snippets to paste into your existing pipeline.\n"))

    github_repo        = ask("GitHub repository (owner/repo)?", required=True,
                             hint="Used in SCA waiver fetch step, e.g. myorg/my-sf-repo")
    org_alias          = ask("Salesforce org alias?", default="uat")
    coverage_threshold = ask("Coverage threshold (%)?", default="85")
    deploy_branch      = ask("Deployment branch?", default="uat")
    env_name           = ask("ADO Environment name (for architect gate)?", default="SalesforceUAT-Production")
    crt_job_id         = ask("CRT Job ID?",     default="115686")
    crt_project_id     = ask("CRT Project ID?", default="73283")
    crt_org_id         = ask("CRT Org ID?",     default="43532")

    selected = ask_ado_modules()
    if not selected:
        print(red("No modules selected. Exiting.")); return

    subs = dict(
        github_repo=github_repo,
        org_alias=org_alias,
        coverage_threshold=coverage_threshold,
        deploy_branch=deploy_branch,
        env_name=env_name,
        crt_job_id=crt_job_id,
        crt_project_id=crt_project_id,
        crt_org_id=crt_org_id,
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir    = os.path.join(script_dir, "generated", "modules")
    os.makedirs(out_dir, exist_ok=True)

    generated_files = []
    prereq_summary  = []

    for key in selected:
        m = ADO_MODULES[key]
        snippet = m["snippet"].format(**subs)
        out_path = os.path.join(out_dir, f"{key}-job.yml")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(snippet)
        generated_files.append(out_path)
        prereq_summary.append((m["name"], m["variables"]))

    # Write integration guide
    guide_lines = [
        f"# ADO Module Snippets — Integration Guide",
        f"# Generated: {date.today().isoformat()}",
        f"# GitHub repo: {github_repo}",
        "",
        "## How to integrate each snippet",
        "",
        "1. Open your existing ADO pipeline YAML file",
        "2. Locate the `jobs:` block in the appropriate `stage:` section",
        "3. Copy-paste the `*-job.yml` snippet content under `jobs:`",
        "   (For `architect-gate-job.yml`, paste the full `stage:` block under `stages:`)",
        "4. Add the required variable group variables or pipeline variables listed below",
        "5. Commit and push — the new job will appear in the next pipeline run",
        "",
        "---",
        "",
        "## Prerequisites per module",
        "",
    ]
    for name, vars_ in prereq_summary:
        guide_lines.append(f"### {name}")
        if vars_:
            guide_lines.append("")
            guide_lines.append("**ADO Variable Group / Pipeline Variables:**")
            for v in vars_:
                guide_lines.append(f"- `{v}`")
        guide_lines += ["", "---", ""]

    guide_lines += [
        "## Waiver file (for SCA module)",
        "",
        "Create `.github/sf-scanner-waivers.csv` on your repo's **main branch**:",
        "",
        "```csv",
        "rule,file_pattern,message_contains,severity_threshold,expiry,reason,approved_by,approved_date,ticket,status",
        "ApexDoc,MyClass.cls,,3,31-12-2025,Refactoring in progress.,jane-lead,01-01-2025,PROJ-123,ACTIVE",
        "```",
        "",
        "See `ado-pipelines/SETUP.md` section 11 for full waiver documentation.",
    ]

    guide_path = os.path.join(out_dir, "integration-guide.md")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write("\n".join(guide_lines))
    generated_files.append(guide_path)

    print(f"\n{green('✅ ADO module snippets generated:')}")
    for p in generated_files:
        print(f"   {bold(p)}")
    print(f"\n{cyan('Next steps:')}")
    print(f"  1. Open {bold('integration-guide.md')} for prerequisites and integration steps")
    print(f"  2. Paste each {bold('*-job.yml')} into your existing pipeline YAML jobs section")
    print(f"  3. Add the listed variables to your ADO variable group or pipeline settings")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print()
    print(bold("╔══════════════════════════════════════════════════════════════╗"))
    print(bold("║   Salesforce ADO Pipeline Generator                         ║"))
    print(bold("║   Generates customized pipeline YAML for your ADO project   ║"))
    print(bold("╚══════════════════════════════════════════════════════════════╝"))
    print()
    print("Answer the questions below to customise the pipeline for your project.")
    print(dim("Press Enter to accept the default value shown in [brackets].\n"))

    # ── Mode selection ─────────────────────────────────────────────────────────
    section("MODE SELECTION")
    print(f"  {cyan('1.')} {bold('Full pipeline')}     — generate a complete ADO pipeline YAML from scratch")
    print(f"  {cyan('2.')} {bold('Module snippets')}   — generate only specific job snippets to add to an existing pipeline\n")
    mode_raw = input(bold("Select mode (1 or 2)") + " [default: 1]: ").strip()
    if mode_raw == "2":
        generate_ado_module_mode()
        return

    section("1. PROJECT BASICS")

    project_name = ask(
        "What is your project / application name?",
        required=True,
        hint="Used in pipeline display names. e.g. 'My Salesforce App'"
    )

    ado_org = ask(
        "What is your Azure DevOps organization name?",
        required=True,
        hint="From your ADO URL: https://dev.azure.com/<ORG_NAME>"
    )

    ado_project = ask(
        "What is your Azure DevOps project name?",
        required=True,
        hint="The project that contains your Salesforce repository"
    )

    repo_name = ask(
        "What is your ADO repository name?",
        required=True,
        hint="The repo where your Salesforce source code lives"
    )

    # ── Section 2: Branches ───────────────────────────────────────────────────
    section("2. BRANCH CONFIGURATION")
    print(dim("  The PR validation stage triggers when a PR targets these branches."))

    pr_branches = ask_list(
        "Which branches should the PR validation pipeline run on?",
        default=["uat", "main"],
        hint="Comma-separated. e.g. 'uat, main' or 'develop, staging, main'"
    )

    deploy_branch = ask(
        "Which is your primary deployment / integration branch?",
        default=pr_branches[0] if pr_branches else "uat",
        hint="The branch that is deployed to the SF org. e.g. 'uat'"
    )

    delta_push_branch = ask(
        "Which branch should trigger the delta baseline update on direct push?",
        default=deploy_branch,
        hint="Usually the same as the deployment branch"
    )

    # ── Section 3: Salesforce org ─────────────────────────────────────────────
    section("3. SALESFORCE ORG")

    org_alias = ask(
        "What alias do you use for the target Salesforce org?",
        default="uat",
        hint="e.g. 'uat', 'staging', 'myorg-uat'"
    )

    coverage_threshold = ask(
        "What is the minimum Apex code coverage threshold (%)?",
        default="85",
        hint="Integer between 1-100. Recommended: 85"
    )

    source_dir = ask(
        "What is the Salesforce source directory?",
        default="force-app/main/default",
        hint="Relative path to your Apex/LWC source. Default is standard SFDX layout."
    )

    sca_mode = ask(
        "SCA enforcement mode — how should scanner violations be handled?",
        default="enforce",
        hint="enforce = expired waivers/unwaived violations FAIL the pipeline\n"
             "  warn   = violations are warnings; pipeline always continues\n"
             "  off    = skip SCA entirely"
    )
    while sca_mode not in ("enforce", "warn", "off"):
        print(red("  ✗ Must be one of: enforce, warn, off"))
        sca_mode = ask("SCA enforcement mode", default="enforce")

    # ── Section 4: Reviewers & architects ────────────────────────────────────
    section("4. REVIEWERS & ARCHITECTS")
    print(dim("  Use ADO usernames (the login name shown in ADO user profiles)."))

    reviewers = ask_list(
        "Who are the designated PR reviewers? (ADO usernames)",
        default=["ss10del", "chorevathi-deloitte"],
        hint="These users will be auto-requested as reviewers on every PR"
    )

    architects = ask_list(
        "Who are the Architects / Designated Architects? (ADO usernames)",
        default=["chorevathi-deloitte", "mukeshranadeloitte"],
        hint="Only these users can approve a merge to the MAIN branch"
    )

    # ── Section 5: ADO environment name ──────────────────────────────────────
    section("5. DEPLOYMENT ENVIRONMENT")

    env_name = ask(
        "What should the ADO Environment be named (for approval gates)?",
        default="uat-deployment",
        hint="You will create this environment in ADO Pipelines → Environments"
    )

    # ── Section 6: CRT (optional) ────────────────────────────────────────────
    section("6. COPADO ROBOTIC TESTING (CRT)")

    use_crt = ask_yes_no("Does your project use Copado Robotic Testing (CRT)?", default="yes")
    crt_job_id     = "115686"
    crt_project_id = "73283"
    crt_org_id     = "43532"

    if use_crt:
        crt_job_id     = ask("CRT Job ID",     default="115686", hint="From Copado CRT settings")
        crt_project_id = ask("CRT Project ID", default="73283",  hint="From Copado CRT settings")
        crt_org_id     = ask("CRT Org ID",     default="43532",  hint="From Copado CRT settings")

    # ── Section 7: Security scanners (optional) ───────────────────────────────
    section("7. SECURITY SCANNERS (optional)")
    print(dim("  These run in parallel with PR validation if secrets are configured."))

    use_checkmarx = ask_yes_no("Does your project use CheckMarx AST scanning?", default="no")
    use_fortify   = ask_yes_no("Does your project use Fortify on Demand scanning?", default="no")

    # ─────────────────────────────────────────────────────────────────────────
    # GENERATE OUTPUT
    # ─────────────────────────────────────────────────────────────────────────
    section("GENERATING PIPELINE FILES")

    out_dir = os.path.join(os.path.dirname(__file__), "generated")
    os.makedirs(out_dir, exist_ok=True)

    # ── Build substitution map ────────────────────────────────────────────────
    pr_branches_yaml    = "\n".join(f"      - {b}" for b in pr_branches)
    reviewers_bash      = " ".join(f'"{r}"' for r in reviewers)
    architects_bash     = "\n".join(f'            "{a}"' for a in architects)
    today               = date.today().isoformat()

    # ── Read template e2e-uat-pipeline.yml ───────────────────────────────────
    template_path = os.path.join(os.path.dirname(__file__), "e2e-uat-pipeline.yml")
    if not os.path.exists(template_path):
        print(red(f"\n  ✗ Template not found: {template_path}"))
        print(red("  Make sure you are running this script from the repo root or ado-pipelines/ directory."))
        sys.exit(1)

    with open(template_path, "r", encoding="utf-8") as f:
        pipeline = f.read()

    # Apply substitutions
    pipeline = re.sub(
        r'(    branches:\s*\n\s*include:\s*\n)((?:\s*- \S+\s*\n)+)',
        lambda m: m.group(1) + pr_branches_yaml + "\n",
        pipeline, count=2
    )
    pipeline = pipeline.replace(
        'REVIEWERS=("ss10del" "chorevathi-deloitte")',
        f'REVIEWERS=({reviewers_bash})'
    )
    pipeline = re.sub(
        r'ARCHITECTS=\(\s*\n(?:\s*"[^"]+"\s*\n)+\s*\)',
        f'ARCHITECTS=(\n{architects_bash}\n          )',
        pipeline
    )
    pipeline = pipeline.replace(
        "environment: uat-deployment",
        f"environment: {env_name}"
    )
    # Replace delta push branch in update script reference
    delta_template_path = os.path.join(os.path.dirname(__file__), "update-delta-on-uat-push.yml")
    delta_pipeline = ""
    if os.path.exists(delta_template_path):
        with open(delta_template_path, "r", encoding="utf-8") as f:
            delta_pipeline = f.read()
        delta_pipeline = re.sub(
            r'(    branches:\s*\n\s*include:\s*\n)((?:\s*- \S+\s*\n)+)',
            f"    branches:\n      include:\n      - {delta_push_branch}\n",
            delta_pipeline, count=1
        )

    # ── Write generated e2e pipeline ─────────────────────────────────────────
    out_main = os.path.join(out_dir, "e2e-pipeline.yml")
    header = f"""\
# ═══════════════════════════════════════════════════════════════════════════════
# GENERATED by ado-pipelines/setup.py on {today}
# Project      : {project_name}
# ADO Org      : {ado_org}
# ADO Project  : {ado_project}
# Repository   : {repo_name}
# PR Branches  : {', '.join(pr_branches)}
# Deploy Branch: {deploy_branch}
# Org Alias    : {org_alias}
# Reviewers    : {', '.join(reviewers)}
# Architects   : {', '.join(architects)}
# Environment  : {env_name}
# CRT          : {'enabled' if use_crt else 'disabled'}
# CheckMarx    : {'enabled' if use_checkmarx else 'disabled'}
# Fortify      : {'enabled' if use_fortify else 'disabled'}
# ═══════════════════════════════════════════════════════════════════════════════

"""
    with open(out_main, "w", encoding="utf-8") as f:
        f.write(header + pipeline)
    print(green(f"  ✅ {out_main}"))

    # ── Write generated delta updater ─────────────────────────────────────────
    if delta_pipeline:
        out_delta = os.path.join(out_dir, "update-delta-on-push.yml")
        with open(out_delta, "w", encoding="utf-8") as f:
            f.write(header.replace("e2e-pipeline", "update-delta-on-push") + delta_pipeline)
        print(green(f"  ✅ {out_delta}"))

    # ── Write variable checklist ──────────────────────────────────────────────
    checklist = _build_checklist(
        project_name, ado_org, ado_project, repo_name,
        pr_branches, deploy_branch, env_name,
        org_alias, coverage_threshold, source_dir, sca_mode,
        reviewers, architects,
        use_crt, crt_job_id, crt_project_id, crt_org_id,
        use_checkmarx, use_fortify, today
    )
    out_checklist = os.path.join(out_dir, "variable-checklist.md")
    with open(out_checklist, "w", encoding="utf-8") as f:
        f.write(checklist)
    print(green(f"  ✅ {out_checklist}"))

    # ── Final instructions ────────────────────────────────────────────────────
    print()
    print(bold("╔══════════════════════════════════════════════════════════════╗"))
    print(bold("║   NEXT STEPS                                                 ║"))
    print(bold("╚══════════════════════════════════════════════════════════════╝"))
    print(f"""
  1. {bold('Copy the generated files into your project repository:')}

     cp ado-pipelines/generated/e2e-pipeline.yml          your-repo/ado-pipelines/e2e-pipeline.yml
     cp ado-pipelines/generated/update-delta-on-push.yml  your-repo/ado-pipelines/update-delta-on-push.yml

  2. {bold('Follow the variable checklist to set up all secrets and variables:')}

     Open:  ado-pipelines/generated/variable-checklist.md

  3. {bold('Register both YAML files as pipelines in ADO:')}

     Pipelines → New pipeline → Azure Repos Git → select repo
     → Existing YAML file → /ado-pipelines/e2e-pipeline.yml

  4. {bold('Create the ADO Environment with architect approval gate:')}

     Pipelines → Environments → New → Name: {env_name}
     → Approvals and checks → Approvals → Add: {', '.join(architects)}

  5. {bold('Add branch policy on target branches:')}
     Branches: {', '.join(pr_branches)}
     → Build validation → Required → Salesforce PR Validation

  6. {bold('Set DELTA_FROM_COMMIT to the current tip of {deploy_branch}:')}

     git checkout {deploy_branch} && git rev-parse HEAD
     → Paste SHA into variable group as DELTA_FROM_COMMIT

  See {bold('ado-pipelines/SETUP.md')} for the full guide.
""")


# ─────────────────────────────────────────────────────────────────────────────
# CHECKLIST GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def _build_checklist(
    project_name, ado_org, ado_project, repo_name,
    pr_branches, deploy_branch, env_name,
    org_alias, coverage_threshold, source_dir, sca_mode,
    reviewers, architects,
    use_crt, crt_job_id, crt_project_id, crt_org_id,
    use_checkmarx, use_fortify, today
):
    scanner_rows = ""
    if use_checkmarx:
        scanner_rows += """
### CheckMarx Variables

| Variable | Value | Secret? | Where to find it |
|----------|-------|---------|-----------------|
| `CX_BASE_URI` | _(your CheckMarx AST URL)_ | ✅ Yes | CheckMarx AST portal → Settings |
| `CX_TENANT` | _(your tenant name)_ | ✅ Yes | CheckMarx AST → tenant ID |
| `CX_CLIENT_ID` | _(OAuth client ID)_ | ✅ Yes | CheckMarx → IAM → Clients |
| `CX_CLIENT_SECRET` | _(OAuth client secret)_ | ✅ Yes | CheckMarx → IAM → Clients |
| `CX_PROJECT_NAME` | _(project name — optional)_ | No | Your CheckMarx project name |
"""
    if use_fortify:
        scanner_rows += """
### Fortify Variables

| Variable | Value | Secret? | Where to find it |
|----------|-------|---------|-----------------|
| `FOD_URL` | _(Fortify on Demand URL)_ | No | Fortify portal URL |
| `FOD_CLIENT_ID` | _(client ID)_ | ✅ Yes | Fortify → Administration → API |
| `FOD_CLIENT_SECRET` | _(client secret)_ | ✅ Yes | Fortify → Administration → API |
| `FOD_APP_NAME` | _(application name)_ | ✅ Yes | Fortify application name |
| `FOD_RELEASE_NAME` | _(release name)_ | ✅ Yes | Fortify release name |
"""

    crt_rows = ""
    if use_crt:
        crt_rows = f"""
### CRT Variables

| Variable | Value | Secret? | Where to find it |
|----------|-------|---------|-----------------|
| `CRT_API_TOKEN` | _(Copado API token)_ | ✅ Yes | Copado → Settings → External Personal Access Tokens |
| `CRT_JOB_ID` | `{crt_job_id}` | No | Copado CRT → your test job ID |
| `CRT_PROJECT_ID` | `{crt_project_id}` | No | Copado CRT → project ID |
| `CRT_ORG_ID` | `{crt_org_id}` | No | Copado CRT → org ID |
"""
    else:
        crt_rows = "\n> CRT not enabled for this project — skip this section.\n"

    return f"""\
# Variable & Setup Checklist — {project_name}

> Generated by `ado-pipelines/setup.py` on {today}
> Complete every item in this checklist before running the pipeline for the first time.

---

## Project Summary

| Setting | Value |
|---------|-------|
| **Project name** | {project_name} |
| **ADO Organisation** | {ado_org} |
| **ADO Project** | {ado_project} |
| **Repository** | {repo_name} |
| **PR validation branches** | {', '.join(f'`{b}`' for b in pr_branches)} |
| **Deployment branch** | `{deploy_branch}` |
| **ADO Environment** | `{env_name}` |
| **Reviewers** | {', '.join(f'`{r}`' for r in reviewers)} |
| **Architects** | {', '.join(f'`{a}`' for a in architects)} |

---

## Step 1 — Create the Variable Group

In ADO: **Pipelines → Library → + Variable group**
Name it exactly: `salesforce-uat`

### Salesforce Variables

| Variable | Value to set | Secret? | How to get it |
|----------|-------------|---------|--------------|
| `ORG_ALIAS` | `{org_alias}` | No | Your Salesforce org alias |
| `DELTA_FROM_COMMIT` | _(set in Step 5 below)_ | No | SHA of last deployed commit |
| `COVERAGE_THRESHOLD` | `{coverage_threshold}` | No | Minimum Apex coverage % |
| `SOURCE_DIR` | `{source_dir}` | No | Salesforce source path |
| `SCA_ENFORCEMENT_MODE` | `{sca_mode}` | No | `enforce` / `warn` / `off` |
| `CRT_UAT_AUTHURL` | _(SFDX auth URL — see below)_ | ✅ Yes | `sf org display --target-org {org_alias} --verbose` → copy **Sfdx Auth Url** |

### ADO Variables

| Variable | Value to set | Secret? | Notes |
|----------|-------------|---------|-------|
| `ADO_PAT` | _(your Personal Access Token)_ | ✅ Yes | Scopes: Code Read, Build Read+Execute, Variable Groups Read+Manage, PR Threads Read+Write, Identity Read |
| `DEPLOY_PIPELINE_ID` | _(fill after Step 3)_ | No | Pipeline definition ID from ADO URL |
| `VARIABLE_GROUP_ID` | _(fill after saving this group)_ | No | Visible in URL: `...variableGroups?groupId=XX` |
{crt_rows}{scanner_rows}
---

## Step 2 — Create ADO Environment

1. Go to **Pipelines → Environments → New environment**
2. Name: `{env_name}`
3. Resource: **None**
4. After creating → **⋮ → Approvals and checks → + → Approvals**
5. Add approvers:
{chr(10).join(f'   - `{a}`' for a in architects)}
6. Timeout: 7 days
7. Save

---

## Step 3 — Register Both Pipelines

### Main Pipeline

1. **Pipelines → New pipeline → Azure Repos Git → {repo_name}**
2. Select **Existing Azure Pipelines YAML file**
3. Branch: `main` | Path: `/ado-pipelines/e2e-pipeline.yml`
4. Click **Save** (not Run)
5. Rename to: `{project_name} — Salesforce E2E Pipeline`
6. Note the **Pipeline Definition ID** from the URL → set as `DEPLOY_PIPELINE_ID`

### Delta Updater Pipeline

1. **Pipelines → New pipeline → Azure Repos Git → {repo_name}**
2. Path: `/ado-pipelines/update-delta-on-push.yml`
3. Rename to: `{project_name} — Update Delta Baseline`
4. Link variable group `salesforce-uat` to both pipelines

---

## Step 4 — Configure Branch Policies

For each branch: {', '.join(f'`{b}`' for b in pr_branches)}

1. **Project Settings → Repos → Branches → branch → ⋮ → Branch policies**
2. **Build validation → + Add build policy**
   - Pipeline: `{project_name} — Salesforce E2E Pipeline`
   - Trigger: Automatic
   - Requirement: Required
   - Display name: `Salesforce PR Validation`

---

## Step 5 — Set the Delta Baseline (First-Time Only)

```bash
git checkout {deploy_branch}
git rev-parse HEAD
# Copy the SHA output
```

Paste the SHA into the variable group as `DELTA_FROM_COMMIT`.

---

## Go-Live Checklist

```
□ Variable group 'salesforce-uat' created with all variables
□ CRT_UAT_AUTHURL secret set (SFDX auth URL)
□ ADO_PAT secret set with correct scopes
□ ADO Environment '{env_name}' created with approval gate
□ Approvers added to environment: {', '.join(architects)}
□ e2e-pipeline.yml registered as pipeline in ADO
□ update-delta-on-push.yml registered as pipeline in ADO
□ Variable group linked to both pipelines
□ DEPLOY_PIPELINE_ID and VARIABLE_GROUP_ID updated in variable group
□ Branch policy added to: {', '.join(pr_branches)}
□ DELTA_FROM_COMMIT set to current {deploy_branch} tip SHA
□ SCA waiver file exists at .github/sf-scanner-waivers.csv on main branch
□ Test PR opened to verify pipeline triggers correctly
```
"""


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{yellow('  Setup cancelled.')}\n")
        sys.exit(0)
