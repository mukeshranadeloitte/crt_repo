#!/usr/bin/env python3
"""
Salesforce Jenkins Pipeline Generator
======================================
Interactive setup script that generates a customised Jenkinsfile
for a Salesforce project. Run this once per project to produce your
tailored Jenkinsfile and a filled-in credential checklist.

Usage:
    python3 jenkins/setup.py

Output:
    jenkins/generated/Jenkinsfile
    jenkins/generated/credential-checklist.md
"""

import os
import re
import textwrap
from datetime import date

# ── colour helpers ─────────────────────────────────────────────────────────────
def bold(t):   return f"\033[1m{t}\033[0m"
def green(t):  return f"\033[32m{t}\033[0m"
def yellow(t): return f"\033[33m{t}\033[0m"
def cyan(t):   return f"\033[36m{t}\033[0m"
def red(t):    return f"\033[31m{t}\033[0m"
def dim(t):    return f"\033[2m{t}\033[0m"

def ask(question, default="", required=False, hint=""):
    default_hint = f" {dim(f'[default: {default}]')}" if default else ""
    hint_str     = f"\n  {dim(hint)}" if hint else ""
    prompt       = f"\n{bold(question)}{default_hint}{hint_str}\n  > "
    while True:
        answer = input(prompt).strip()
        if not answer:
            if default:
                return default
            if required:
                print(red("  ✗ This field is required."))
                continue
        return answer

def ask_list(question, default, hint=""):
    raw = ask(question,
              default=", ".join(default) if isinstance(default, list) else default,
              hint=hint)
    return [x.strip() for x in raw.split(",") if x.strip()]

def ask_yes_no(question, default="yes"):
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

def ask_choice(question, choices, default=None):
    print(f"\n{bold(question)}")
    for i, c in enumerate(choices, 1):
        marker = green("▶") if c == default else " "
        print(f"  {marker} {i}. {c}")
    while True:
        raw = input(f"\n  Enter number{f' [default: {default}]' if default else ''}: ").strip()
        if not raw and default:
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]
        print(red(f"  ✗ Enter a number between 1 and {len(choices)}."))

def section(title):
    width = 60
    print(f"\n{cyan('─' * width)}")
    print(cyan(f"  {title}"))
    print(cyan('─' * width))

# ── Jenkinsfile template ───────────────────────────────────────────────────────
JENKINSFILE_TEMPLATE = '''\
#!/usr/bin/env groovy
// ============================================================
// Salesforce UAT End-to-End Pipeline — Jenkins
// Project  : {project_name}
// Generated: {gen_date}
// ============================================================
// Triggers:
//   PR to {target_branches_display}  → PR Validation stages
//   Push to {deploy_branch}          → Deployment stages
// ============================================================

pipeline {{
    agent any

    environment {{
        ORG_ALIAS            = '{org_alias}'
        COVERAGE_THRESHOLD   = '{coverage_threshold}'
        SOURCE_DIR           = 'force-app/main/default'
        SCA_ENFORCEMENT_MODE = '{sca_mode}'
        DELTA_FROM_COMMIT    = "${{env.DELTA_FROM_COMMIT ?: ''}}"
        GITHUB_REPO          = '{github_repo}'
        GITHUB_API_URL       = 'https://api.github.com'
        DEPLOY_BRANCH        = '{deploy_branch}'
        TARGET_BRANCHES      = '{target_branches_csv}'
        PR_REVIEWERS         = '{reviewers_csv}'
        ARCHITECTS           = '{architects_csv}'
{crt_env_vars}    }}

    options {{
        ansiColor('xterm')
        timestamps()
        timeout(time: 2, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }}

    stages {{

        // ──────────────────────────────────────────────────────────
        // STAGE 1 — Evaluate Scanner Availability
        // ──────────────────────────────────────────────────────────
        stage('Evaluate Scanner Availability') {{
            when {{ changeRequest() }}
            steps {{
                script {{
                    env.RUN_CHECKMARX = 'false'
                    env.RUN_FORTIFY   = 'false'
                    try {{
                        withCredentials([string(credentialsId: 'CX_CLIENT_SECRET', variable: 'CX_SECRET')]) {{
                            if (CX_SECRET?.trim()) env.RUN_CHECKMARX = 'true'
                        }}
                    }} catch (e) {{ /* credential not configured */ }}
                    try {{
                        withCredentials([string(credentialsId: 'FOD_CLIENT_SECRET', variable: 'FOD_SECRET')]) {{
                            if (FOD_SECRET?.trim()) env.RUN_FORTIFY = 'true'
                        }}
                    }} catch (e) {{ /* credential not configured */ }}
                    echo "Scanner availability — CheckMarx: ${{env.RUN_CHECKMARX}}  Fortify: ${{env.RUN_FORTIFY}}"
                }}
            }}
        }}

        // ──────────────────────────────────────────────────────────
        // STAGE 2 — Salesforce PR Validation
        // ──────────────────────────────────────────────────────────
        stage('Salesforce PR Validation') {{
            when {{ changeRequest() }}
            steps {{
                cleanWs()
                checkout scm
                sh 'git fetch --unshallow || true'
                withCredentials([
                    string(credentialsId: 'CRT_UAT_AUTHURL', variable: 'SFDX_AUTH_URL'),
                    string(credentialsId: 'GITHUB_PAT',      variable: 'GH_PAT')
                ]) {{
                    sh """
                        set -euo pipefail

                        # ── Install toolchain ────────────────────────────────
                        npm install --global @salesforce/cli --quiet
                        echo y | sf plugins install sfdx-git-delta 2>/dev/null || true
                        git config --global --add safe.directory "$WORKSPACE"

                        # ── Authenticate org ─────────────────────────────────
                        printf '%s' "$SFDX_AUTH_URL" > sfdxAuthUrl.txt
                        sf org login sfdx-url --sfdx-url-file sfdxAuthUrl.txt --alias "$ORG_ALIAS" --set-default
                        rm -f sfdxAuthUrl.txt

                        # ── Request PR reviewers ─────────────────────────────
                        if [ -n "${{CHANGE_ID:-}}" ] && [ -n "$GH_PAT" ]; then
                            PR_AUTHOR=$(curl -sS -H "Authorization: Bearer $GH_PAT" \\
                                "$GITHUB_API_URL/repos/$GITHUB_REPO/pulls/$CHANGE_ID" | jq -r '.user.login')
                            REVIEWERS_JSON=$(echo "$PR_REVIEWERS" | tr ',' '\\n' \\
                                | grep -v "^$PR_AUTHOR$" \\
                                | jq -R . | jq -sc .)
                            curl -sS -X POST \\
                                -H "Authorization: Bearer $GH_PAT" \\
                                -H "Content-Type: application/json" \\
                                "$GITHUB_API_URL/repos/$GITHUB_REPO/pulls/$CHANGE_ID/requested_reviewers" \\
                                -d "{\\"reviewers\\":$REVIEWERS_JSON}" || true
                        fi

                        # ── Build delta ──────────────────────────────────────
                        BASE_SHA=\$(git merge-base HEAD "origin/$CHANGE_TARGET" 2>/dev/null || echo "$DELTA_FROM_COMMIT")
                        echo "Delta FROM: $BASE_SHA  TO: HEAD"
                        sf sgd:source:delta --to "HEAD" --from "$BASE_SHA" \\
                            --output-dir "." --source-dir force-app/

                        echo "===== package/package.xml ====="
                        cat package/package.xml 2>/dev/null || echo "(not generated)"
                        echo "===== destructiveChanges/destructiveChanges.xml ====="
                        cat destructiveChanges/destructiveChanges.xml 2>/dev/null || echo "(not generated)"

                        # ── Has delta? ───────────────────────────────────────
                        HAS_DELTA=false
                        if grep -q '<members>' package/package.xml 2>/dev/null || \\
                           grep -q '<members>' destructiveChanges/destructiveChanges.xml 2>/dev/null; then
                            HAS_DELTA=true
                        fi
                        echo "has_delta=$HAS_DELTA"

                        if [ "$HAS_DELTA" = "true" ]; then
                            # ── Infer test classes ───────────────────────────
                            CHANGED_APEX=\$(git diff --name-only "$BASE_SHA" HEAD \\
                                | grep -E '\\.cls$' | grep -v 'Test' || true)
                            TEST_CLASSES=""
                            for f in $CHANGED_APEX; do
                                base=\$(basename "$f" .cls)
                                for suffix in Test Tests TestClass; do
                                    if [ -f "force-app/main/default/classes/${{base}}${{suffix}}.cls" ]; then
                                        TEST_CLASSES="$TEST_CLASSES ${{base}}${{suffix}}"
                                    fi
                                done
                            done
                            TEST_CLASSES=\$(echo "$TEST_CLASSES" | xargs)

                            # ── Validate deploy ──────────────────────────────
                            echo "════════════════════════ Validate Deploy ════════════════════════"
                            DEPLOY_CMD="sf project deploy validate --target-org $ORG_ALIAS --async --json"
                            if [ -f package/package.xml ] && grep -q '<members>' package/package.xml; then
                                DEPLOY_CMD="$DEPLOY_CMD --manifest package/package.xml"
                            else
                                DEPLOY_CMD="$DEPLOY_CMD --source-dir $SOURCE_DIR"
                            fi
                            if [ -f destructiveChanges/destructiveChanges.xml ] && \\
                               grep -q '<members>' destructiveChanges/destructiveChanges.xml; then
                                DEPLOY_CMD="$DEPLOY_CMD --post-destructive-changes destructiveChanges/destructiveChanges.xml"
                            fi
                            if [ -n "$TEST_CLASSES" ]; then
                                TC_LIST=\$(echo "$TEST_CLASSES" | tr ' ' ',')
                                DEPLOY_CMD="$DEPLOY_CMD --tests $TC_LIST --test-level RunSpecifiedTests"
                            fi

                            DEPLOY_OUTPUT=\$($DEPLOY_CMD)
                            JOB_ID=\$(echo "$DEPLOY_OUTPUT" | jq -r '.result.id // .id // empty')
                            echo "Deploy job ID: $JOB_ID"

                            # Poll for completion
                            ELAPSED=0
                            while true; do
                                STATUS_JSON=\$(sf project deploy report --job-id "$JOB_ID" --json 2>/dev/null || echo '{}')
                                STATUS=\$(echo "$STATUS_JSON" | jq -r '.result.status // "Unknown"')
                                printf "  %4ds  %s\\n" "$ELAPSED" "$STATUS"
                                if echo "$STATUS" | grep -qiE '^(Succeeded|Failed|Canceled|SucceededPartial)'; then
                                    break
                                fi
                                sleep 15
                                ELAPSED=\$((ELAPSED + 15))
                            done

                            if echo "$STATUS" | grep -qi "^Failed"; then
                                echo "::error::Deployment validation failed"
                                echo "$STATUS_JSON" | jq -r '.result.details.componentFailures[]? | "  ❌ \\(.componentType) \\(.fileName): \\(.problem)"' || true
                                exit 1
                            fi
                            echo "✅ Validation passed"

                            # ── Coverage check ───────────────────────────────
                            COVERAGE=\$(echo "$STATUS_JSON" | jq -r '
                                .result.details.runTestResult.codeCoverage[]?
                                | (.numLocations - .numLocationsNotCovered) / .numLocations * 100
                                | floor' | sort -n | head -1)
                            if [ -n "$COVERAGE" ] && [ "$COVERAGE" -lt "$COVERAGE_THRESHOLD" ]; then
                                echo "::error::Coverage $COVERAGE% is below threshold $COVERAGE_THRESHOLD%"
                                exit 1
                            fi
                        fi

                        # ── SCA ──────────────────────────────────────────────
                        if [ "$SCA_ENFORCEMENT_MODE" != "off" ]; then
                            echo y | sf plugins install @salesforce/sfdx-scanner 2>/dev/null || true

                            CHANGED_SF=\$(git diff --name-only "$BASE_SHA" HEAD \\
                                | grep -E '\\.(cls|trigger|js|html|css)$' | tr '\\n' ',' | sed 's/,\$//' || true)

                            if [ -n "$CHANGED_SF" ]; then
                                sf scanner run \\
                                    --target "$CHANGED_SF" \\
                                    --format csv \\
                                    --outfile sfdx-report.csv \\
                                    --severity-threshold 3 || true

                                # Fetch waivers from main
                                curl -sS -H "Authorization: Bearer $GH_PAT" \\
                                    "$GITHUB_API_URL/repos/$GITHUB_REPO/contents/.github/sf-scanner-waivers.csv?ref=main" \\
                                    | jq -r '.content' | base64 -d > fetched-waivers.csv 2>/dev/null || touch fetched-waivers.csv

                                # Check violations against waivers
                                TODAY=\$(date +%Y-%m-%d)
                                FAIL=false
                                while IFS=',' read -r rule file line col sev msg url; do
                                    [ "$rule" = "Rule" ] && continue
                                    WAIVED=false
                                    EXPIRED=false
                                    while IFS=',' read -r w_rule w_file w_msg w_sev w_expiry w_reason w_by w_date w_ticket w_status; do
                                        [ "$w_rule" = "rule" ] && continue
                                        [ "$w_status" != "ACTIVE" ] && continue
                                        RULE_MATCH=false
                                        FILE_MATCH=false
                                        { [ -z "$w_rule" ] || [ "$w_rule" = "*" ] || echo "$rule" | grep -qi "$w_rule"; } && RULE_MATCH=true
                                        { [ -z "$w_file" ] || [ "$w_file" = "*" ] || echo "$file" | grep -qi "$w_file"; } && FILE_MATCH=true
                                        if $RULE_MATCH && $FILE_MATCH; then
                                            # Parse expiry DD-MM-YYYY or YYYY-MM-DD
                                            if echo "$w_expiry" | grep -qE '^[0-9]{{2}}-[0-9]{{2}}-[0-9]{{4}}$'; then
                                                EXP_ISO="\${{w_expiry:6:4}}-\${{w_expiry:3:2}}-\${{w_expiry:0:2}}"
                                            else
                                                EXP_ISO="$w_expiry"
                                            fi
                                            if [[ "$EXP_ISO" < "$TODAY" ]]; then
                                                EXPIRED=true
                                            else
                                                WAIVED=true
                                            fi
                                            break
                                        fi
                                    done < fetched-waivers.csv
                                    if $EXPIRED; then
                                        echo "❌ EXPIRED WAIVER: $rule — $file:$line"
                                        [ "$SCA_ENFORCEMENT_MODE" = "enforce" ] && FAIL=true
                                    elif $WAIVED; then
                                        echo "✅ WAIVED: $rule — $file:$line"
                                    else
                                        echo "⚠️  VIOLATION: $rule — $file:$line — $msg"
                                    fi
                                done < sfdx-report.csv

                                $FAIL && { echo "::error::SCA enforcement failed — fix expired waivers"; exit 1; } || true
                            fi
                        fi

                        # ── Notify reviewers ─────────────────────────────────
                        if [ -n "${{CHANGE_ID:-}}" ] && [ -n "$GH_PAT" ]; then
                            COMMENT="### ✅ All PR Validation Checks Passed\\n\\nThe following checks completed successfully:\\n- ✅ Salesforce delta build\\n- ✅ Check-only deployment\\n- ✅ Apex test coverage >= $COVERAGE_THRESHOLD%\\n- ✅ SCA scan (mode: $SCA_ENFORCEMENT_MODE)\\n\\n**PR is ready for review.**"
                            curl -sS -X POST \\
                                -H "Authorization: Bearer $GH_PAT" \\
                                -H "Content-Type: application/json" \\
                                "$GITHUB_API_URL/repos/$GITHUB_REPO/issues/$CHANGE_ID/comments" \\
                                -d "{\\"body\\":\\"$COMMENT\\"}" || true
                        fi
                    """
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'sfdx-report.csv,fetched-waivers.csv', allowEmptyArchive: true
                }}
            }}
        }}

        // ──────────────────────────────────────────────────────────
        // STAGE 3 — CheckMarx SAST (optional)
        // ──────────────────────────────────────────────────────────
        stage('CheckMarx SAST') {{
            when {{
                allOf {{
                    changeRequest()
                    expression {{ env.RUN_CHECKMARX == 'true' }}
                }}
            }}
            steps {{
                withCredentials([
                    string(credentialsId: 'CX_BASE_URI',      variable: 'CX_BASE_URI'),
                    string(credentialsId: 'CX_TENANT',        variable: 'CX_TENANT'),
                    string(credentialsId: 'CX_CLIENT_ID',     variable: 'CX_CLIENT_ID'),
                    string(credentialsId: 'CX_CLIENT_SECRET', variable: 'CX_CLIENT_SECRET')
                ]) {{
                    echo "Running CheckMarx AST Scan..."
                    // Replace with your CheckMarx Jenkins plugin step or CLI invocation:
                    // checkmarxAstScan serverUrl: env.CX_BASE_URI, ...
                    sh 'echo "CheckMarx step placeholder — configure with your CheckMarx plugin"'
                }}
            }}
        }}

        // ──────────────────────────────────────────────────────────
        // STAGE 4 — Fortify SAST/DAST (optional)
        // ──────────────────────────────────────────────────────────
        stage('Fortify SAST/DAST') {{
            when {{
                allOf {{
                    changeRequest()
                    expression {{ env.RUN_FORTIFY == 'true' }}
                }}
            }}
            steps {{
                withCredentials([
                    string(credentialsId: 'FOD_CLIENT_ID',     variable: 'FOD_CLIENT_ID'),
                    string(credentialsId: 'FOD_CLIENT_SECRET', variable: 'FOD_CLIENT_SECRET'),
                    string(credentialsId: 'FOD_APP_NAME',      variable: 'FOD_APP_NAME'),
                    string(credentialsId: 'FOD_RELEASE_NAME',  variable: 'FOD_RELEASE_NAME')
                ]) {{
                    echo "Running Fortify on Demand Scan..."
                    // Replace with your Fortify Jenkins plugin step or fcli invocation
                    sh 'echo "Fortify step placeholder — configure with your Fortify plugin"'
                }}
            }}
        }}

        // ──────────────────────────────────────────────────────────
        // STAGE 5 — Architect Approval Gate (deployment branch only)
        // ──────────────────────────────────────────────────────────
        stage('Architect Approval Gate') {{
            when {{
                allOf {{
                    not {{ changeRequest() }}
                    branch env.DEPLOY_BRANCH
                }}
            }}
            steps {{
                script {{
                    def architects = env.ARCHITECTS.split(',').collect {{ it.trim() }}
                    timeout(time: 7, unit: 'DAYS') {{
                        def approver = input(
                            message: "Deploy to ${{env.ORG_ALIAS}} org?\\nArchitects only: ${{architects.join(', ')}}",
                            submitter: env.ARCHITECTS,
                            submitterParameter: 'APPROVED_BY'
                        )
                        env.DEPLOY_APPROVER = approver
                        echo "✅ Deployment approved by: $approver"
                    }}
                }}
            }}
        }}

        // ──────────────────────────────────────────────────────────
        // STAGE 6 — Deploy to UAT org
        // ──────────────────────────────────────────────────────────
        stage('Deploy to UAT org') {{
            when {{
                allOf {{
                    not {{ changeRequest() }}
                    branch env.DEPLOY_BRANCH
                }}
            }}
            steps {{
                cleanWs()
                checkout scm
                sh 'git fetch --unshallow || true'
                withCredentials([
                    string(credentialsId: 'CRT_UAT_AUTHURL', variable: 'SFDX_AUTH_URL'),
                    string(credentialsId: 'GITHUB_PAT',      variable: 'GH_PAT')
                ]) {{
                    sh """
                        set -euo pipefail

                        npm install --global @salesforce/cli --quiet
                        echo y | sf plugins install sfdx-git-delta 2>/dev/null || true
                        git config --global --add safe.directory "$WORKSPACE"

                        printf '%s' "$SFDX_AUTH_URL" > sfdxAuthUrl.txt
                        sf org login sfdx-url --sfdx-url-file sfdxAuthUrl.txt --alias "$ORG_ALIAS" --set-default
                        rm -f sfdxAuthUrl.txt

                        # ── Build delta ──────────────────────────────────────
                        echo "Delta FROM: $DELTA_FROM_COMMIT  TO: HEAD"
                        sf sgd:source:delta --to "HEAD" --from "$DELTA_FROM_COMMIT" \\
                            --output-dir "." --source-dir force-app/

                        echo "===== package/package.xml ====="
                        cat package/package.xml 2>/dev/null || echo "(not generated)"
                        echo "===== destructiveChanges/destructiveChanges.xml ====="
                        cat destructiveChanges/destructiveChanges.xml 2>/dev/null || echo "(not generated)"

                        HAS_DELTA=false
                        if grep -q '<members>' package/package.xml 2>/dev/null || \\
                           grep -q '<members>' destructiveChanges/destructiveChanges.xml 2>/dev/null; then
                            HAS_DELTA=true
                        fi

                        if [ "$HAS_DELTA" = "false" ]; then
                            echo "ℹ️  No delta — nothing to deploy."
                            exit 0
                        fi

                        # ── Deploy ───────────────────────────────────────────
                        echo "════════════════════════ Deploying ════════════════════════"
                        DEPLOY_CMD="sf project deploy start --target-org $ORG_ALIAS --async --test-level NoTestRun --json"
                        if grep -q '<members>' package/package.xml 2>/dev/null; then
                            DEPLOY_CMD="$DEPLOY_CMD --manifest package/package.xml"
                        else
                            DEPLOY_CMD="$DEPLOY_CMD --source-dir $SOURCE_DIR"
                        fi
                        if grep -q '<members>' destructiveChanges/destructiveChanges.xml 2>/dev/null; then
                            DEPLOY_CMD="$DEPLOY_CMD --post-destructive-changes destructiveChanges/destructiveChanges.xml"
                        fi

                        DEPLOY_OUTPUT=\$($DEPLOY_CMD)
                        JOB_ID=\$(echo "$DEPLOY_OUTPUT" | jq -r '.result.id // .id // empty')
                        echo "Deploy job ID: $JOB_ID"

                        ELAPSED=0
                        while true; do
                            STATUS_JSON=\$(sf project deploy report --job-id "$JOB_ID" --json 2>/dev/null || echo '{}')
                            STATUS=\$(echo "$STATUS_JSON" | jq -r '.result.status // "Unknown"')
                            COMP_DONE=\$(echo "$STATUS_JSON" | jq -r '.result.numberComponentsDeployed // 0')
                            COMP_TOTAL=\$(echo "$STATUS_JSON" | jq -r '.result.numberComponentsTotal // 0')
                            printf "  %4ds  %-20s  components: %s/%s\\n" "$ELAPSED" "$STATUS" "$COMP_DONE" "$COMP_TOTAL"
                            if echo "$STATUS" | grep -qiE '^(Succeeded|Failed|Canceled|SucceededPartial)'; then
                                break
                            fi
                            sleep 15
                            ELAPSED=\$((ELAPSED + 15))
                        done

                        if echo "$STATUS" | grep -qi "^Failed"; then
                            echo "$STATUS_JSON" | jq -r '.result.details.componentFailures[]? | "  ❌ \\(.componentType) \\(.fileName): \\(.problem)"' || true
                            exit 1
                        fi
                        echo "✅ Deployment succeeded"

                        # ── Update DELTA_FROM_COMMIT ──────────────────────────
                        DEPLOY_SHA=\$(git rev-parse HEAD)
                        echo "Updating DELTA_FROM_COMMIT → $DEPLOY_SHA"
                        HTTP=\$(curl -sS -o /tmp/var_resp.json -w "%{{http_code}}" \\
                            -X PATCH \\
                            -H "Authorization: Bearer $GH_PAT" \\
                            -H "Accept: application/vnd.github+json" \\
                            "https://api.github.com/repos/$GITHUB_REPO/actions/variables/DELTA_FROM_COMMIT" \\
                            -d "{\\"name\\":\\"DELTA_FROM_COMMIT\\",\\"value\\":\\"$DEPLOY_SHA\\"}")
                        if [ "$HTTP" = "204" ]; then
                            echo "✅ DELTA_FROM_COMMIT updated to $DEPLOY_SHA"
                        else
                            echo "::warning::Could not update DELTA_FROM_COMMIT (HTTP $HTTP). Update manually to: $DEPLOY_SHA"
                        fi
                    """
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'package/package.xml,destructiveChanges/destructiveChanges.xml', allowEmptyArchive: true
                }}
            }}
        }}

        // ──────────────────────────────────────────────────────────
        // STAGE 7 — Trigger CRT Tests
        // ──────────────────────────────────────────────────────────
        stage('Trigger CRT Tests') {{
            when {{
                allOf {{
                    not {{ changeRequest() }}
                    branch env.DEPLOY_BRANCH
                }}
            }}
            steps {{
                withCredentials([string(credentialsId: 'CRT_API_TOKEN', variable: 'CRT_API_TOKEN')]) {{
                    sh """
                        set -euo pipefail
                        echo "════════════════════════ CRT Tests ════════════════════════"

                        # Trigger build
                        TRIGGER_RESP=\$(curl -sS -X POST \\
                            -H "Content-Type: application/json" \\
                            -H "X-Authorization: $CRT_API_TOKEN" \\
                            "https://graphql.eu-robotic.copado.com/v1" \\
                            -d '{{"query":"mutation {{ createBuild(projectId: \\"{crt_project_id}\\", jobId: \\"{crt_job_id}\\") {{ id status }} }}"}}')
                        BUILD_ID=\$(echo "$TRIGGER_RESP" | jq -r '.data.createBuild.id // empty')
                        echo "CRT Build ID: $BUILD_ID"

                        if [ -z "$BUILD_ID" ]; then
                            echo "::warning::Could not trigger CRT build. Check CRT_API_TOKEN and CRT IDs."
                            exit 0
                        fi

                        # Poll status
                        ELAPSED=0
                        CRT_STATUS="executing"
                        while true; do
                            POLL_RESP=\$(curl -sS -X POST \\
                                -H "Content-Type: application/json" \\
                                -H "X-Authorization: $CRT_API_TOKEN" \\
                                "https://graphql.eu-robotic.copado.com/v1" \\
                                -d '{{"query":"query {{ latestBuilds(projectId: \\"{crt_project_id}\\", resultSize: 10) {{ id status }} }}"}}')
                            CRT_STATUS=\$(echo "$POLL_RESP" | jq -r --arg bid "$BUILD_ID" '.data.latestBuilds[] | select(.id == $bid) | .status // "unknown"' | head -1)
                            printf "  %4ds  CRT status: %s\\n" "$ELAPSED" "$CRT_STATUS"
                            if echo "$CRT_STATUS" | grep -qiE '^(passed|failed|error|cancelled|skipped)'; then
                                break
                            fi
                            sleep 30
                            ELAPSED=\$((ELAPSED + 30))
                            [ "$ELAPSED" -ge 1800 ] && {{ echo "::warning::CRT polling timed out after 30 minutes"; break; }}
                        done

                        echo ""
                        echo "╔══════════════════════════════════════╗"
                        echo "║       CRT Job Execution Summary       ║"
                        echo "╠══════════════════════════════════════╣"
                        echo "  Test Build ID  : $BUILD_ID"
                        echo "  Test Result    : $CRT_STATUS"
                        echo "  CRT Dashboard  : https://eu-robotic.copado.com/jobs/{crt_job_id}?projectId={crt_project_id}&orgId={crt_org_id}"
                        echo "╚══════════════════════════════════════╝"

                        if echo "$CRT_STATUS" | grep -qi "^failed\\|^error"; then
                            echo "::warning::CRT tests $CRT_STATUS — review CRT dashboard"
                        fi
                    """
                }}
            }}
        }}

    }}

    post {{
        success {{
            echo green("✅ Pipeline completed successfully")
        }}
        failure {{
            echo red("❌ Pipeline failed — check stage logs above")
        }}
        always {{
            cleanWs()
        }}
    }}
}}
'''

# ── Credential checklist template ──────────────────────────────────────────────
CHECKLIST_TEMPLATE = """\
# Jenkins Credential & Setup Checklist
# Project: {project_name}
# Generated: {gen_date}

## Required Jenkins Credentials

Add each credential at:
Jenkins → Manage Jenkins → Credentials → System → Global credentials → Add Credential
Kind: Secret text  (unless noted)

| Credential ID      | Value                         | Status |
|--------------------|-------------------------------|--------|
| CRT_UAT_AUTHURL    | <SFDX Auth URL force://...>   | ☐ Done |
| GITHUB_PAT         | <GitHub fine-grained PAT>     | ☐ Done |
| CRT_API_TOKEN      | <Copado CRT API token>        | ☐ Done |

## Optional Credentials (Security Scanners)

| Credential ID      | Scanner    | Status        |
|--------------------|------------|---------------|
| CX_CLIENT_SECRET   | CheckMarx  | ☐ Done / N/A  |
| CX_BASE_URI        | CheckMarx  | ☐ Done / N/A  |
| CX_TENANT          | CheckMarx  | ☐ Done / N/A  |
| CX_CLIENT_ID       | CheckMarx  | ☐ Done / N/A  |
| FOD_CLIENT_SECRET  | Fortify    | ☐ Done / N/A  |
| FOD_CLIENT_ID      | Fortify    | ☐ Done / N/A  |
| FOD_APP_NAME       | Fortify    | ☐ Done / N/A  |
| FOD_RELEASE_NAME   | Fortify    | ☐ Done / N/A  |

## Required Environment Variables

Jenkins → Manage Jenkins → Configure System → Environment variables

| Variable            | Value to Set                 | Status |
|---------------------|------------------------------|--------|
| DELTA_FROM_COMMIT   | <run: git rev-parse HEAD on {deploy_branch}> | ☐ Done |

## Project Configuration Applied

| Setting              | Value                     |
|----------------------|---------------------------|
| Project Name         | {project_name}            |
| Jenkins URL          | {jenkins_url}             |
| GitHub Repo          | {github_repo}             |
| Target Branches      | {target_branches_display} |
| Deployment Branch    | {deploy_branch}           |
| Org Alias            | {org_alias}               |
| Coverage Threshold   | {coverage_threshold}%     |
| PR Reviewers         | {reviewers_csv}           |
| Architects           | {architects_csv}          |
| SCA Enforcement Mode | {sca_mode}                |
| CRT Job ID           | {crt_job_id}              |
| CRT Project ID       | {crt_project_id}          |
| CRT Org ID           | {crt_org_id}              |

## Go-Live Checklist

```
☐ Ran jenkins/setup.py and reviewed generated Jenkinsfile
☐ Jenkinsfile copied to repo root and committed
☐ Required Jenkins plugins installed
☐ All credentials added to Jenkins (see tables above)
☐ DELTA_FROM_COMMIT environment variable set
☐ Multibranch Pipeline job created pointing to Jenkinsfile
☐ GitHub webhook configured → HTTP 200 in Recent Deliveries
☐ Salesforce CLI + jq available on Jenkins agent
☐ Test PR opened → PR validation stages triggered successfully
☐ Deployment stage tested → architect input() appears
☐ .github/sf-scanner-waivers.csv exists on main branch
☐ First deployment succeeded → DELTA_FROM_COMMIT auto-updated
```
"""

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{bold(cyan('╔══════════════════════════════════════════════════════════╗'))}")
    print(f"{bold(cyan('║   Salesforce Jenkins Pipeline Generator                   ║'))}")
    print(f"{bold(cyan('╚══════════════════════════════════════════════════════════╝'))}")
    print(f"\n{dim('Answer each question — press Enter to accept the default.')}\n")

    # ── Section 1: Project basics ──────────────────────────────────────────────
    section("1 / 7  Project Basics")
    project_name = ask("Project name?", default="Salesforce UAT Project", required=True)
    jenkins_url  = ask("Jenkins URL?", default="https://jenkins.example.com",
                       hint="e.g. https://jenkins.mycompany.com")
    github_repo  = ask("GitHub repository (owner/repo)?", required=True,
                       hint="e.g. myorg/my-salesforce-repo")

    # ── Section 2: Branches ────────────────────────────────────────────────────
    section("2 / 7  Branches")
    target_branches = ask_list(
        "Which branches should PR validation run on?",
        default=["uat", "main"],
        hint="Comma-separated, e.g. uat, main")
    deploy_branch = ask(
        "Which is the deployment (primary) branch?",
        default=target_branches[0] if target_branches else "uat",
        hint="Push/merge to this branch triggers deployment stages")

    # ── Section 3: Salesforce ──────────────────────────────────────────────────
    section("3 / 7  Salesforce")
    org_alias = ask("Salesforce org alias?", default="uat",
                    hint="The alias you used: sf org login web --alias <alias>")
    coverage_threshold = ask("Apex coverage threshold (%)?", default="85",
                             hint="Minimum per-class coverage (1-100)")

    # ── Section 4: People ──────────────────────────────────────────────────────
    section("4 / 7  Reviewers & Architects")
    reviewers = ask_list(
        "Default PR reviewer GitHub usernames?",
        default=["reviewer1", "reviewer2"],
        hint="Comma-separated — auto-requested on every PR. Leave blank to skip.")
    architects = ask_list(
        "Architect GitHub usernames (deployment approvers for main branch)?",
        default=["architect1"],
        hint="Comma-separated — only these users can click Proceed in the Jenkins input step.")

    # ── Section 5: CRT ─────────────────────────────────────────────────────────
    section("5 / 7  CRT (Copado Robotic Testing)")
    use_crt = ask_yes_no("Are you using Copado Robotic Testing (CRT)?", default="yes")
    crt_job_id     = "115686"
    crt_project_id = "73283"
    crt_org_id     = "43532"
    if use_crt:
        crt_job_id     = ask("CRT Job ID?",     default="115686", hint="Copado CRT → your test job → ID")
        crt_project_id = ask("CRT Project ID?", default="73283",  hint="Copado CRT → Project ID")
        crt_org_id     = ask("CRT Org ID?",     default="43532",  hint="Copado CRT → Org ID")

    # ── Section 6: Security scanners ───────────────────────────────────────────
    section("6 / 7  Security Scanners")
    scanner = ask_choice(
        "Which security scanners are you using?",
        choices=["none", "checkmarx", "fortify", "both"],
        default="none")

    # ── Section 7: SCA ─────────────────────────────────────────────────────────
    section("7 / 7  SCA Enforcement Mode")
    sca_mode = ask_choice(
        "How should Salesforce Code Analyzer violations be handled?",
        choices=["enforce", "warn", "off"],
        default="enforce")
    print(dim("  enforce = expired waivers FAIL the pipeline"))
    print(dim("  warn    = all violations are warnings only"))
    print(dim("  off     = all SCA steps skipped entirely"))

    # ── Confirm ────────────────────────────────────────────────────────────────
    print(f"\n{cyan('─' * 60)}")
    print(bold("  Summary — review before generating"))
    print(cyan('─' * 60))
    rows = [
        ("Project name",         project_name),
        ("Jenkins URL",          jenkins_url),
        ("GitHub repo",          github_repo),
        ("Target branches",      ", ".join(target_branches)),
        ("Deployment branch",    deploy_branch),
        ("Org alias",            org_alias),
        ("Coverage threshold",   f"{coverage_threshold}%"),
        ("PR reviewers",         ", ".join(reviewers) or "(none)"),
        ("Architects",           ", ".join(architects) or "(none)"),
        ("CRT",                  f"yes  (job:{crt_job_id}  project:{crt_project_id}  org:{crt_org_id})" if use_crt else "no"),
        ("Scanners",             scanner),
        ("SCA enforcement mode", sca_mode),
    ]
    for k, v in rows:
        print(f"  {bold(k+':'):<35} {v}")
    print(cyan('─' * 60))

    if not ask_yes_no("\nGenerate files with these settings?", default="yes"):
        print(yellow("\nAborted. Re-run to try again."))
        return

    # ── Build substitution values ──────────────────────────────────────────────
    target_branches_display = " / ".join(target_branches)
    target_branches_csv     = ",".join(target_branches)
    reviewers_csv           = ",".join(reviewers)
    architects_csv          = ",".join(architects)
    gen_date                = date.today().isoformat()

    crt_env_vars = ""
    if use_crt:
        crt_env_vars = (
            f"        CRT_JOB_ID           = '{crt_job_id}'\n"
            f"        CRT_PROJECT_ID       = '{crt_project_id}'\n"
            f"        CRT_ORG_ID           = '{crt_org_id}'\n"
        )

    subs = dict(
        project_name=project_name,
        gen_date=gen_date,
        org_alias=org_alias,
        coverage_threshold=coverage_threshold,
        sca_mode=sca_mode,
        deploy_branch=deploy_branch,
        target_branches_display=target_branches_display,
        target_branches_csv=target_branches_csv,
        reviewers_csv=reviewers_csv,
        architects_csv=architects_csv,
        github_repo=github_repo,
        crt_env_vars=crt_env_vars,
        crt_job_id=crt_job_id,
        crt_project_id=crt_project_id,
        crt_org_id=crt_org_id,
        jenkins_url=jenkins_url,
    )

    jenkinsfile_content  = JENKINSFILE_TEMPLATE.format(**subs)
    checklist_content    = CHECKLIST_TEMPLATE.format(**subs)

    # Remove CheckMarx/Fortify stages if not needed
    if scanner == "none":
        jenkinsfile_content = re.sub(
            r"        // ──.*?STAGE 3 — CheckMarx.*?        // ──.*?STAGE 4 — Fortify.*?        // ──.*?STAGE 5",
            "        // ──────────────────────────────────────────────────────────\n        // STAGE 5",
            jenkinsfile_content, flags=re.DOTALL)
    elif scanner == "checkmarx":
        jenkinsfile_content = re.sub(
            r"        // ──.*?STAGE 4 — Fortify.*?        // ──.*?STAGE 5",
            "        // ──────────────────────────────────────────────────────────\n        // STAGE 5",
            jenkinsfile_content, flags=re.DOTALL)
    elif scanner == "fortify":
        jenkinsfile_content = re.sub(
            r"        // ──.*?STAGE 3 — CheckMarx.*?        // ──.*?STAGE 4",
            "        // ──────────────────────────────────────────────────────────\n        // STAGE 4",
            jenkinsfile_content, flags=re.DOTALL)

    if not use_crt:
        jenkinsfile_content = re.sub(
            r"        // ──.*?STAGE 7 — Trigger CRT.*",
            "", jenkinsfile_content, flags=re.DOTALL)
        jenkinsfile_content = jenkinsfile_content.rstrip() + "\n\n    }\n\n    post {\n        success {\n            echo \"✅ Pipeline completed successfully\"\n        }\n        failure {\n            echo \"❌ Pipeline failed — check stage logs above\"\n        }\n        always {\n            cleanWs()\n        }\n    }\n}\n"

    # ── Write output files ─────────────────────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir    = os.path.join(script_dir, "generated")
    os.makedirs(out_dir, exist_ok=True)

    jenkinsfile_path  = os.path.join(out_dir, "Jenkinsfile")
    checklist_path    = os.path.join(out_dir, "credential-checklist.md")

    with open(jenkinsfile_path,  "w", encoding="utf-8") as f:
        f.write(jenkinsfile_content)
    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write(checklist_content)

    print(f"\n{green('✅ Files generated successfully:')}")
    print(f"   {bold(jenkinsfile_path)}")
    print(f"   {bold(checklist_path)}")
    print(f"""
{cyan('Next steps:')}
  1. Copy {bold('jenkins/generated/Jenkinsfile')} to your repo root
  2. Open {bold('jenkins/generated/credential-checklist.md')} and follow each step
  3. Add credentials to Jenkins (Manage Jenkins → Credentials)
  4. Set DELTA_FROM_COMMIT environment variable (git rev-parse HEAD on {deploy_branch})
  5. Create Multibranch Pipeline job pointing to your Jenkinsfile
  6. Configure GitHub webhook → {jenkins_url}/github-webhook/
  7. Open a test PR and verify the pipeline triggers
""")


if __name__ == "__main__":
    main()
