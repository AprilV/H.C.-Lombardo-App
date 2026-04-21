"""
Replace the Project Logbook tab in Dashboard/index.html.

LEFT  (flex:1 1 65%)  — scrollable terminal log, sticky search bar + filter buttons at top
RIGHT (flex:0 0 480px) — full project reference: §1–§12 sessions, sprint history, contracts
"""
import os
import sys
import re
from datetime import date

DASHBOARD = "c:/ReactGitEC2/IS330/H.C Lombardo App/Dashboard/index.html"
DEVLOG    = "c:/ReactGitEC2/IS330/H.C Lombardo App/devlog_output.html"

with open(DASHBOARD, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(DEVLOG, 'r', encoding='utf-8') as f:
    devlog_raw = f.read()

# ── Extract .ln div lines ──────────────────────────────────────────────────────
ln_lines     = re.findall(r'<div class="ln[^>]*>.*?</div>', devlog_raw)
ln_count     = len(ln_lines)
log_fragment = '\n'.join(ln_lines)

commit_lines = [l for l in ln_lines if 'ln-commit' in l]
commit_count = len(commit_lines)
key_count    = sum(1 for l in ln_lines if 'c-key' in l or 'ln-keylabel' in l)
bug_count    = sum(1 for l in ln_lines if ' c-bug' in l)
fix_count    = sum(1 for l in ln_lines if ' c-fix' in l)
today_str    = date.today().strftime('%b %d, %Y')

# ── Find start/end markers ─────────────────────────────────────────────────────
start_line = end_line = None
for i, line in enumerate(lines):
    if start_line is None and '<div id="tab-ailog"' in line:
        start_line = i
    if '</div><!-- /tab-ailog -->' in line:
        end_line = i
        break

if start_line is None or end_line is None:
    print(f"ERROR: markers not found. start={start_line} end={end_line}")
    sys.exit(1)

print(f"Replacing lines {start_line+1} to {end_line+1} ({end_line - start_line + 1} lines)")
print(f"Extracted {ln_count:,} log lines from {commit_count} commits")

# ── RIGHT PANEL: full §1–§12 project reference (static HTML, no f-string vars) ──
RIGHT_PANEL_HTML = """
  <!-- ── RIGHT: Full project reference §1–§12 ── -->
  <div style="flex:0 0 480px;min-width:320px;background:#0d1117;border-left:2px solid #f0883e;
              overflow-y:auto;padding:1.5rem 1.25rem 3rem;">

    <div style="font-size:0.78rem;font-weight:700;color:#f0883e;letter-spacing:0.08em;margin-bottom:0.2rem;">AI PROJECT LOG — REFERENCE</div>
    <div style="font-size:0.66rem;color:#484f58;margin-bottom:1.5rem;">H.C. Lombardo NFL Analytics &middot; Spring 2026 &middot; April V. Sykes, PM</div>

    <!-- §1 SESSION START CHECKLIST -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§1 — Session Start Checklist (Non-Negotiable)</h3>
        <p style="color:var(--muted);font-size:0.78rem;margin-bottom:0.5rem;">Every single session. No exceptions. Do these before saying or doing ANYTHING.</p>
        <ol style="color:#f1f5f9;font-size:0.78rem;line-height:2;margin:0;padding-left:1.25rem;">
            <li>Read <code style="background:rgba(255,255,255,0.08);padding:0.1rem 0.35rem;border-radius:0.2rem;font-size:0.74rem;">memory/handover_apr19.md</code> — full project state, what was done, what's next</li>
            <li>Read <code style="background:rgba(255,255,255,0.08);padding:0.1rem 0.35rem;border-radius:0.2rem;font-size:0.74rem;">memory/feedback_preferences.md</code> — operating rules and session preferences</li>
            <li>Read ALL other files in the memory directory</li>
            <li>Read <code style="background:rgba(255,255,255,0.08);padding:0.1rem 0.35rem;border-radius:0.2rem;font-size:0.74rem;">docs/ai_reference/AI_EXECUTION_CONTRACT.md</code></li>
            <li>Read <code style="background:rgba(255,255,255,0.08);padding:0.1rem 0.35rem;border-radius:0.2rem;font-size:0.74rem;">docs/ai_reference/READ_THIS_FIRST.md</code> and <code style="background:rgba(255,255,255,0.08);padding:0.1rem 0.35rem;border-radius:0.2rem;font-size:0.74rem;">BEST_PRACTICES.md</code></li>
            <li>Read <code style="background:rgba(255,255,255,0.08);padding:0.1rem 0.35rem;border-radius:0.2rem;font-size:0.74rem;">Dashboard/index.html</code> — understand current state, do NOT ask April what's done</li>
            <li>THEN AND ONLY THEN — respond to April</li>
        </ol>
        <div style="margin-top:0.75rem;padding-top:0.6rem;border-top:1px solid var(--border-subtle);font-size:0.74rem;color:#f87171;">
            <strong>Why:</strong> On Apr 19, 2026, Claude skipped this step, built in the wrong location, wasted April's day off, and violated the contract repeatedly.
        </div>
    </div>

    <!-- §2 AI EXECUTION CONTRACT -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§2 — AI Execution Contract (Full Text)</h3>
        <div style="font-size:0.78rem;line-height:1.8;color:#f1f5f9;">
            <p style="color:#f87171;font-weight:700;margin-bottom:0.4rem;">STATUS: ACTIVE — NON-NEGOTIABLE · APPLIES TO: ALL AI ASSISTANTS · PRIORITY: ABSOLUTE</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">1. REQUIRED PRECONDITION: FULL INGESTION</p>
            <p style="color:var(--muted);">BEFORE responding to ANY request, the AI MUST: (1) Read this document in FULL. (2) Confirm ALL rules can be followed. (3) Identify whether additional documents must be read.<br>PROHIBITED: Skimming · Partial reading · "I inferred" · "I assumed" · Proceeding without certainty.<br>IF FULL COMPLIANCE IS NOT POSSIBLE → STOP → ASK QUESTIONS → WAIT</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">2. AUTHORITY ORDER (STRICT)</p>
            <p style="color:var(--muted);">Obey in order: (1) AI_EXECUTION_CONTRACT.md · (2) READ_THIS_FIRST.md · (3) BEST_PRACTICES.md · (4) Master reference docs · (5) The codebase.<br>IF CONFLICT EXISTS → STOP → ASK → WAIT</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">3. NO-ASSUMPTION RULE (HARD STOP)</p>
            <p style="color:var(--muted);">FORBIDDEN to assume: project state · sprint or phase · environment · scope · intent · file ownership · "obvious" solutions.<br>ASSUMPTIONS ARE FAILURES. IF REQUIRED INFORMATION IS MISSING → ASK → DO NOT PROCEED</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">4. EXECUTION PHILOSOPHY (LOCKED)</p>
            <p style="color:var(--muted);">Priorities IN ORDER: Correctness &gt; Speed · System integrity &gt; Local fixes · Questions &gt; Guessing · Long-term stability &gt; Short-term output.<br>"Best effort" is NOT acceptable. Progress without correctness is FAILURE.</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">5. SYSTEM-WIDE AWARENESS</p>
            <p style="color:var(--muted);">BEFORE any change: (1) Identify ALL affected files. (2) Identify ALL affected modules/pages/components. (3) Identify ALL downstream effects.<br>PROHIBITED: Example-only fixes · Single-file fixes when shared systems exist · Ignoring indirect impact.</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">6. MANDATORY CLEANUP</p>
            <p style="color:var(--muted);">WHENEVER code is modified: Remove obsolete logic · Remove superseded implementations · Remove unused imports/variables · Remove commented-out code · Eliminate duplicate logic.<br>PROHIBITED: Leaving "just in case" code · Commenting out instead of removing.</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">7. QUESTION-FIRST FALLBACK</p>
            <p style="color:var(--muted);">MUST ask questions when: instructions are ambiguous · scope is unclear · multiple valid approaches exist · risk of breaking existing behavior. DO NOT: Guess · Fill gaps · Proceed silently.</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">8. REQUIRED RESPONSE FORMAT</p>
            <p style="color:var(--muted);">ANY solution MUST include: (1) Documents read · (2) Files reviewed · (3) Files impacted · (4) Changes proposed · (5) Code to be removed · (6) Open questions. EMPTY SECTIONS NOT PERMITTED.</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">9. FAILURE CONDITIONS</p>
            <p style="color:var(--muted);">AI HAS FAILED if it: skims docs · makes assumptions · applies partial fixes · leaves dead code · optimizes for speed over correctness. ON FAILURE → STOP → ASK → WAIT</p>
            <p style="color:#FFD700;font-weight:700;margin:0.75rem 0 0.25rem;">10. FINAL DIRECTIVE</p>
            <p style="color:var(--muted);margin-bottom:0;">The AI is not here to be fast. The AI is here to be correct. Compliance is mandatory. Deviation is not permitted.</p>
        </div>
    </div>

    <!-- §3 READ_THIS_FIRST -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§3 — READ_THIS_FIRST.md (Summary)</h3>
        <div style="font-size:0.78rem;line-height:1.8;color:var(--muted);">
            <p><strong style="color:#f1f5f9;">This is NOT a sandbox.</strong> This codebase is not a tutorial, demo, or experiment. Changes cascade. Treat all changes as potentially system-wide.</p>
            <p><strong style="color:#f87171;">FAILURE looks like:</strong> skipping required reads · guessing intent or scope · fixing only one instance of a repeated issue · leaving dead/duplicate/commented-out code · applying changes without identifying impact · proceeding without asking when uncertain.</p>
            <p style="margin-bottom:0;"><strong style="color:#10b981;">SUCCESS looks like:</strong> asking questions early · identifying full scope before acting · applying consistent system-wide changes · cleaning up obsolete code · preserving existing behavior unless instructed otherwise · preferring correctness over speed.</p>
        </div>
    </div>

    <!-- §4 ROLE AND WORKING RULES -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§4 — Role, Working Rules &amp; Operating Procedure</h3>
        <div style="font-size:0.78rem;line-height:1.8;color:#f1f5f9;">
            <p style="font-size:0.82rem;font-weight:700;color:#FFD700;margin-bottom:0.25rem;">ROLE — NON-NEGOTIABLE</p>
            <p style="color:var(--muted);">April is the Project Manager. Claude is the developer. Nothing more. Do not move without April's explicit permission. Do not assume, anticipate, or act ahead of instruction. April directs. Claude executes. That is the only dynamic.</p>
            <p style="font-size:0.82rem;font-weight:700;color:#FFD700;margin:0.6rem 0 0.25rem;">THIS IS A WEB PAGE — NOT AN APP</p>
            <p style="color:var(--muted);">Always refer to it as a web page. Best practices for web development apply to everything. This will be reviewed by employers, professors, and other students. Every decision must reflect professional web development standards.</p>
            <p style="font-size:0.82rem;font-weight:700;color:#FFD700;margin:0.6rem 0 0.25rem;">AUTOMATION RULE</p>
            <p style="color:var(--muted);">Automate it while building it. If a value changes over time — compute it. If something repeats a pattern — loop it. Hardcoding is only acceptable when there is no reasonable automated alternative.</p>
            <p style="font-size:0.82rem;font-weight:700;color:#FFD700;margin:0.6rem 0 0.25rem;">AGILE TERMINOLOGY — NO EXCEPTIONS</p>
            <p style="color:var(--muted);margin-bottom:0;"><strong style="color:#f1f5f9;">Task</strong> = TA-xxx backlog item · <strong style="color:#f1f5f9;">Subtask</strong> = checklist item under a task · <strong style="color:#f1f5f9;">Blocker</strong> = active impediment (P1/P2) · <strong style="color:#f1f5f9;">Issue</strong> = unplanned operational event — NOT a synonym for task.</p>
            <p style="font-size:0.82rem;font-weight:700;color:#FFD700;margin:0.6rem 0 0.25rem;">COMMUNICATION RULES</p>
            <p style="color:var(--muted);margin-bottom:0;">Don't summarize what you just did · Don't push forward to next task · Don't ask questions answerable by reading the code · Report back after EVERY single action · One task per session.</p>
            <p style="font-size:0.82rem;font-weight:700;color:#FFD700;margin:0.6rem 0 0.25rem;">DASHBOARD RULES</p>
            <p style="color:var(--muted);margin-bottom:0;">Deploy: gh-pages branch only · No localStorage · No dynamic fetching · All data hardcoded · Only change exactly what was asked · Dashboard structure is locked.</p>
            <p style="font-size:0.82rem;font-weight:700;color:#FFD700;margin:0.6rem 0 0.25rem;">GIT / DEPLOY</p>
            <pre style="background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.1);border-radius:0.35rem;padding:0.6rem 0.75rem;font-size:0.7rem;color:#10b981;margin-top:0.35rem;overflow-x:auto;white-space:pre-wrap;">git checkout gh-pages
git show master:Dashboard/index.html > index.html
git add index.html && git commit -m "Deploy: ..."
git checkout master
git push origin master && git push origin gh-pages</pre>
            <p style="color:var(--muted);margin:0.4rem 0 0;font-size:0.74rem;">EC2 SSH: <code style="background:rgba(255,255,255,0.08);padding:0.1rem 0.35rem;border-radius:0.2rem;font-size:0.7rem;">ssh -i /c/Users/april/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249</code></p>
        </div>
    </div>

    <!-- §5 PROJECT OVERVIEW -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§5 — Project Overview &amp; Architecture</h3>
        <div style="font-size:0.78rem;line-height:1.8;color:var(--muted);">
            <p><strong style="color:#f1f5f9;">Project:</strong> H.C. Lombardo NFL Analytics App — Senior Capstone, Olympic College, Spring 2026 (Apr 6 – Jun 13, 2026)</p>
            <p><strong style="color:#f1f5f9;">Student / PM:</strong> April V. Sykes &nbsp;·&nbsp; <strong style="color:#f1f5f9;">Advisor:</strong> Richard Becker</p>
            <p><strong style="color:#f1f5f9;">Goal:</strong> Public-release-ready NFL analytics application. Self-directed; April submits performance reports and measurable deliverables.</p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-top:0.6rem;">
                <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border-subtle);border-radius:0.4rem;padding:0.6rem;">
                    <p style="color:#FFD700;font-weight:700;font-size:0.74rem;margin:0 0 0.3rem;">FRONTEND</p>
                    <p style="margin:0;font-size:0.74rem;">React (port 3000) &rarr; AWS Amplify<br>master.d2tamnlcbzo0d5.amplifyapp.com</p>
                </div>
                <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border-subtle);border-radius:0.4rem;padding:0.6rem;">
                    <p style="color:#FFD700;font-weight:700;font-size:0.74rem;margin:0 0 0.3rem;">BACKEND</p>
                    <p style="margin:0;font-size:0.74rem;">Flask API (port 5000) &rarr; EC2<br>ubuntu@34.198.25.249</p>
                </div>
                <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border-subtle);border-radius:0.4rem;padding:0.6rem;">
                    <p style="color:#FFD700;font-weight:700;font-size:0.74rem;margin:0 0 0.3rem;">DATABASE</p>
                    <p style="margin:0;font-size:0.74rem;">PostgreSQL EC2 localhost:5432 · Schema: hcl<br>7,263+ games (1999–2025)</p>
                </div>
                <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border-subtle);border-radius:0.4rem;padding:0.6rem;">
                    <p style="color:#FFD700;font-weight:700;font-size:0.74rem;margin:0 0 0.3rem;">ML MODELS</p>
                    <p style="margin:0;font-size:0.74rem;">XGBoost winner + spread (ml/)<br>xgb_winner.pkl · xgb_spread.pkl · Dec 19 2025</p>
                </div>
            </div>
            <p style="margin-top:0.75rem;"><strong style="color:#f1f5f9;">Backend:</strong> api_server.py · api_routes_hcl.py · api_routes_ml.py · api_routes_live_scores.py · db_config.py · background_updater.py</p>
            <p style="margin-bottom:0;"><strong style="color:#f1f5f9;">Frontend (frontend/src/):</strong> App.js · Analytics.js · MLPredictions.js · MLPredictionsRedesign.js · MatchupAnalyzer.js · TeamComparison.js · LiveScores.js · ModelPerformance.js · Admin.js</p>
        </div>
    </div>

    <!-- §6 SPRINT SCHEDULE -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§6 — Sprint Schedule</h3>
        <table style="width:100%;border-collapse:collapse;font-size:0.78rem;">
            <thead><tr style="border-bottom:1px solid var(--border);">
                <th style="text-align:left;padding:0.35rem 0.6rem;color:var(--muted);font-weight:600;">Sprint</th>
                <th style="text-align:left;padding:0.35rem 0.6rem;color:var(--muted);font-weight:600;">Dates</th>
                <th style="text-align:left;padding:0.35rem 0.6rem;color:var(--muted);font-weight:600;">Theme</th>
                <th style="text-align:left;padding:0.35rem 0.6rem;color:var(--muted);font-weight:600;">Status</th>
            </tr></thead>
            <tbody>
                <tr style="border-bottom:1px solid var(--border-subtle);">
                    <td style="padding:0.4rem 0.6rem;color:#f1f5f9;font-weight:700;">S1–S11</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">Sep 2025 – Apr 5</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">App Build</td>
                    <td style="padding:0.4rem 0.6rem;"><span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.1rem 0.5rem;font-size:0.68rem;font-weight:700;">Completed</span></td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);background:rgba(255,255,255,0.02);">
                    <td style="padding:0.4rem 0.6rem;color:#f1f5f9;font-weight:700;">S12</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">Apr 6–19, 2026</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">Diagnose &amp; Restore</td>
                    <td style="padding:0.4rem 0.6rem;"><span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.1rem 0.5rem;font-size:0.68rem;font-weight:700;">Closed GREEN</span></td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);">
                    <td style="padding:0.4rem 0.6rem;color:#FFD700;font-weight:700;">S13</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">Apr 20–May 2, 2026</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">Data &amp; Clean</td>
                    <td style="padding:0.4rem 0.6rem;"><span style="background:rgba(251,191,36,0.15);color:#fbbf24;border:1px solid rgba(251,191,36,0.3);border-radius:9999px;padding:0.1rem 0.5rem;font-size:0.68rem;font-weight:700;">Active</span></td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);background:rgba(255,255,255,0.02);">
                    <td style="padding:0.4rem 0.6rem;color:#f1f5f9;">S14</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">May 4–16, 2026</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">ML Retrain</td>
                    <td style="padding:0.4rem 0.6rem;"><span style="background:rgba(148,163,184,0.1);color:#94a3b8;border:1px solid rgba(148,163,184,0.2);border-radius:9999px;padding:0.1rem 0.5rem;font-size:0.68rem;font-weight:700;">Upcoming</span></td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);">
                    <td style="padding:0.4rem 0.6rem;color:#f1f5f9;">S15</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">May 18–30, 2026</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">UI &amp; UX Polish</td>
                    <td style="padding:0.4rem 0.6rem;"><span style="background:rgba(148,163,184,0.1);color:#94a3b8;border:1px solid rgba(148,163,184,0.2);border-radius:9999px;padding:0.1rem 0.5rem;font-size:0.68rem;font-weight:700;">Upcoming</span></td>
                </tr>
                <tr>
                    <td style="padding:0.4rem 0.6rem;color:#f1f5f9;">S16</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">Jun 1–13, 2026</td>
                    <td style="padding:0.4rem 0.6rem;color:var(--muted);">Hardening &amp; Release</td>
                    <td style="padding:0.4rem 0.6rem;"><span style="background:rgba(148,163,184,0.1);color:#94a3b8;border:1px solid rgba(148,163,184,0.2);border-radius:9999px;padding:0.1rem 0.5rem;font-size:0.68rem;font-weight:700;">Upcoming</span></td>
                </tr>
            </tbody>
        </table>
        <p style="color:var(--muted);font-size:0.74rem;margin-top:0.6rem;margin-bottom:0;">Term ends Jun 13, 2026. Future sprint content decided at planning AFTER previous sprint closes — never pre-assign tasks.</p>
    </div>

    <!-- §7 SPRINT 12 FULL HISTORY -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.3rem;">§7 — Sprint 12 Full History (Apr 6–19, 2026)</h3>
        <p style="color:var(--muted);font-size:0.76rem;margin-bottom:0.9rem;">Theme: Diagnose &amp; Restore · Closed GREEN Apr 18 · 8 of 9 tasks delivered · Hours: 32 total</p>
        <div style="font-size:0.76rem;line-height:1.7;">
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-001 — SSH Access &amp; EC2 Service Verification</strong>
                    <span style="color:var(--muted);font-size:0.72rem;white-space:nowrap;">14 subtasks · P1 Critical</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);">SSH key confirmed · hc-lombardo.service active · Port 5000 listening · curl localhost:5000/health → healthy · <strong style="color:#f87171;">Disk: 88% full (5.9G/6.8G) — P1 blocker TA-063</strong> · .env confirmed · EC2 was found STOPPED at start of S12 — restarted via AWS CLI (root MFA lost, R-10 active).</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-002 — PostgreSQL Health Check &amp; Schema Validation</strong>
                    <span style="color:var(--muted);font-size:0.72rem;white-space:nowrap;">11 subtasks · P1</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);">PostgreSQL running · nfl_analytics DB · hcl schema · 7,269 games · 14,398 team-game records · ml_predictions and betting_lines present · Season coverage 1999–2025 confirmed.</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-003 — Test All 22 API Endpoints</strong>
                    <span style="color:var(--muted);font-size:0.72rem;white-space:nowrap;">22 subtasks · P1</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);">/health healthy · /api/hcl/teams → 4 of 32 (TA-052) · /api/hcl/summary → 404 (TA-053) · ML endpoints OK · /api/ml/season-ai-vs-vegas/2024 → AI 20.3% (52W) vs Vegas 13.3% (34W) · /api/elo/ratings/current → 32-team ELO · /api/elo/predict-week/2024/18 → "No games found" (TA-055).</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-004 — Frontend Production Walkthrough</strong>
                    <span style="color:var(--muted);font-size:0.72rem;white-space:nowrap;">17 subtasks · P1</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);">All 14 frontend routes confirmed loading · CORS and 404 errors noted · App.js routing bug: wrong components mapped to /game-statistics and /matchup-analyzer.</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-005 — Verify REACT_APP_API_URL in Amplify</strong>
                    <span style="color:var(--muted);font-size:0.72rem;">3 subtasks · P1</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);">REACT_APP_API_URL = http://34.198.25.249:5000 confirmed in Amplify env vars · Last build successful.</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-006 — CORS Configuration Fix</strong>
                    <span style="color:var(--muted);font-size:0.72rem;">4 subtasks · P1</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);">CORS preflight to Amplify origin → 200 OK · api_server.py line 51 — Amplify domain explicitly listed · 4 endpoints tested with Amplify origin — all correct CORS headers.</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-007 — Production Task Log Created</strong>
                    <span style="color:var(--muted);font-size:0.72rem;">12 subtasks · P2</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);"><strong style="color:#f87171;">Hardcoded DB passwords in api_server.py, api_routes_hcl.py, api_routes_live_scores.py (security)</strong> · <strong style="color:#f87171;">train_xgb_winner.py line 255: load_data(schema='hcl_test') — wrong schema</strong> · <strong style="color:#f87171;">train_xgb_spread.py lines 95–116: broken WINDOW clause</strong> · Default season 2025 hardcoded in 7+ endpoints · Models dated Dec 19, 2025.</div>
            </div>
            <div style="margin-bottom:1rem;">
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(248,113,113,0.15);color:#f87171;border:1px solid rgba(248,113,113,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">BLOCKED</span>
                    <strong style="color:#f1f5f9;">TA-008 — Live App URL Added to Dashboard</strong>
                    <span style="color:var(--muted);font-size:0.72rem;">1 subtask · P1 · Backlog</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(248,113,113,0.3);">Root MFA device lost — cannot access AWS console. <strong style="color:#fbbf24;">To unblock: call AWS Support 1-800-879-2747 to reset root MFA.</strong></div>
            </div>
            <div>
                <div style="display:flex;align-items:baseline;gap:0.6rem;margin-bottom:0.3rem;">
                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);border-radius:9999px;padding:0.08rem 0.5rem;font-size:0.66rem;font-weight:700;white-space:nowrap;">DONE</span>
                    <strong style="color:#f1f5f9;">TA-009 — CLAUDE.md Updated</strong>
                    <span style="color:var(--muted);font-size:0.72rem;">1 subtask · P2</span>
                </div>
                <div style="color:var(--muted);padding-left:0.6rem;border-left:2px solid rgba(16,185,129,0.3);">CLAUDE.md updated with current routes, deployment state, architecture, and Spring 2026 term details. Advisor changed from Dr. Foster to Richard Becker.</div>
            </div>
        </div>
    </div>

    <!-- §8 APR 19 DASHBOARD WORK -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.3rem;">§8 — Apr 19 Dashboard Work</h3>
        <p style="color:var(--muted);font-size:0.76rem;margin-bottom:0.75rem;">All in Dashboard/index.html · Committed and deployed to master + gh-pages · ~5 hours</p>
        <div style="font-size:0.78rem;line-height:1.9;color:var(--muted);">
            <p><strong style="color:#f1f5f9;">Product Backlog Tracker rebuilt:</strong> Removed two sub-tabs, unified into one panel. Sprint filter buttons auto-generated from SPRINT_SCHEDULE with date-gating. Status + priority filters stack with sprint filter. Print and CSV download (4 scope options each).</p>
            <p><strong style="color:#f1f5f9;">Dashboard home automation:</strong> "Last updated" bar reads document.lastModified. RAG "Next review" computed from SPRINT_SCHEDULE. P1 and open task counts driven from SPRINT_ARCHIVE. sprintEnd reads from SPRINT_SCHEDULE dynamically.</p>
            <p><strong style="color:#f1f5f9;">Sprint selector dropdown:</strong> Filters all charts/metrics by sprint. Drives SPRINT_ARCHIVE data for burndown, burnup, velocity, severity. getCurrentSprint() auto-detects active sprint by date.</p>
            <p><strong style="color:#f1f5f9;">Sprint board tab:</strong> initSprintBoardTab() generates sprint cards dynamically from SPRINT_SCHEDULE. Status computed by date.</p>
            <p><strong style="color:#f1f5f9;">Progress Reports rebuilt:</strong> Sprint filter (All | S12–S16). Sprint summary combines both weeks. Print button. Download (.txt). CSS fix: select option visibility (white-on-white was unreadable).</p>
            <p style="margin-bottom:0;"><strong style="color:#f1f5f9;">S13 planning:</strong> 8 tasks assigned (TA-010, 011, 012, 013, 057, 058, 059, 063). Sprint board S13 date-gated until Apr 20.</p>
        </div>
    </div>

    <!-- §9 SPRINT 13 PLAN -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.3rem;">§9 — Sprint 13 Plan (Apr 20 – May 2, 2026)</h3>
        <p style="color:var(--muted);font-size:0.76rem;margin-bottom:0.75rem;">Theme: Data &amp; Clean · Capacity: ~30 hours · 8 tasks assigned</p>
        <table style="width:100%;border-collapse:collapse;font-size:0.76rem;">
            <thead><tr style="border-bottom:1px solid var(--border);">
                <th style="text-align:left;padding:0.3rem 0.5rem;color:var(--muted);font-weight:600;">ID</th>
                <th style="text-align:left;padding:0.3rem 0.5rem;color:var(--muted);font-weight:600;">Task</th>
                <th style="text-align:left;padding:0.3rem 0.5rem;color:var(--muted);font-weight:600;">Pri</th>
            </tr></thead>
            <tbody>
                <tr style="border-bottom:1px solid var(--border-subtle);">
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-063</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">EC2 disk cleanup (88% — crash risk)</td>
                    <td style="padding:0.35rem 0.5rem;color:#f87171;font-weight:700;">Critical</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);background:rgba(255,255,255,0.02);">
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-010</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">Remove hardcoded credentials</td>
                    <td style="padding:0.35rem 0.5rem;color:#f87171;font-weight:700;">Critical</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);">
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-011</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">Move passwords to .env</td>
                    <td style="padding:0.35rem 0.5rem;color:#f87171;font-weight:700;">Critical</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);background:rgba(255,255,255,0.02);">
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-057</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">Fix ML training schema (hcl_test→hcl)</td>
                    <td style="padding:0.35rem 0.5rem;color:#f87171;font-weight:700;">Critical</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);">
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-058</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">Fix broken SQL in spread model</td>
                    <td style="padding:0.35rem 0.5rem;color:#f87171;font-weight:700;">Critical</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);background:rgba(255,255,255,0.02);">
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-059</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">Fix hardcoded season 2025 in backend</td>
                    <td style="padding:0.35rem 0.5rem;color:#fbbf24;font-weight:700;">High</td>
                </tr>
                <tr style="border-bottom:1px solid var(--border-subtle);">
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-012</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">Load 2025 NFL season data</td>
                    <td style="padding:0.35rem 0.5rem;color:#f87171;font-weight:700;">Critical</td>
                </tr>
                <tr>
                    <td style="padding:0.35rem 0.5rem;color:#FFD700;font-weight:700;">TA-013</td>
                    <td style="padding:0.35rem 0.5rem;color:#f1f5f9;">Validate data integrity</td>
                    <td style="padding:0.35rem 0.5rem;color:#fbbf24;font-weight:700;">High</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- §10 KNOWN BLOCKERS -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§10 — Known Blockers (as of Apr 19, 2026)</h3>
        <div style="font-size:0.78rem;line-height:1.8;">
            <div style="background:rgba(248,113,113,0.06);border:1px solid rgba(248,113,113,0.25);border-radius:0.4rem;padding:0.65rem 0.85rem;margin-bottom:0.65rem;">
                <strong style="color:#f87171;">TA-008 / R-10 — AWS Console Locked (Root MFA Lost)</strong><br>
                <span style="color:var(--muted);">P1 · Sprint: Backlog · To unblock: Call AWS Support 1-800-879-2747 to reset root MFA.</span>
            </div>
            <div style="background:rgba(248,113,113,0.06);border:1px solid rgba(248,113,113,0.25);border-radius:0.4rem;padding:0.65rem 0.85rem;margin-bottom:0.65rem;">
                <strong style="color:#f87171;">R-09 — EC2 Disk at 88% (Critical)</strong><br>
                <span style="color:var(--muted);">P1 · TA-063 in S13 · SSH in, run df -h, clean logs/tmp/old backups before crash.</span>
            </div>
            <div style="background:rgba(248,113,113,0.06);border:1px solid rgba(248,113,113,0.25);border-radius:0.4rem;padding:0.65rem 0.85rem;">
                <strong style="color:#fbbf24;">ML Pipeline Blockers (TA-057, TA-058)</strong><br>
                <span style="color:var(--muted);">train_xgb_winner.py uses wrong schema 'hcl_test' (line 255). train_xgb_spread.py has broken WINDOW clause (lines 95–116). Both block all ML retraining.</span>
            </div>
        </div>
    </div>

    <!-- §11 DASHBOARD ARCHITECTURE -->
    <div style="background:var(--card);border:1px solid var(--border);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#FFD700;margin:0 0 0.75rem;">§11 — Dashboard Architecture</h3>
        <p style="color:var(--muted);font-size:0.76rem;margin-bottom:0.6rem;">Single-file PM dashboard. All data hardcoded. No localStorage. Deployed to gh-pages only.</p>
        <div style="font-size:0.78rem;line-height:1.9;color:var(--muted);">
            <p><strong style="color:#f1f5f9;">Key Data Structures:</strong></p>
            <ul style="margin:0 0 0.75rem;padding-left:1.25rem;">
                <li><strong style="color:#FFD700;">SPRINT_SCHEDULE</strong> — single source of truth for sprint dates/themes. All date-gating reads from here.</li>
                <li><strong style="color:#FFD700;">SPRINT_ARCHIVE[N]</strong> — per-sprint: RAG, metrics, burndown, burnup, velocity, severity, p1Count, openCount. Update when sprint closes.</li>
                <li><strong style="color:#FFD700;">COMPLETED_TASKS</strong> — array of all completed subtask IDs. Add when done. Never remove.</li>
                <li><strong style="color:#FFD700;">TASK_DETAILS</strong> — resolution text + date for every subtask.</li>
                <li><strong style="color:#FFD700;">PB_ITEMS</strong> — all backlog items with sprint/status/priority. Flip Backlog &rarr; In Sprint at sprint start.</li>
                <li><strong style="color:#FFD700;">HOURS_DATA</strong> — 10-week array. hours:0 and notes:'' for future weeks.</li>
                <li><strong style="color:#FFD700;">getCurrentSprint()</strong> — reads today vs SPRINT_SCHEDULE, returns active sprint number.</li>
            </ul>
            <p><strong style="color:#f1f5f9;">Sprint Transition Checklist (when April says "close S-X, open S-X+1"):</strong></p>
            <p><em>CLOSE:</em> SPRINT_ARCHIVE[N] full metrics · COMPLETED_TASKS subtask IDs · PB_ITEMS flip Done · HOURS_DATA update · About tab increment sprints count</p>
            <p style="margin-bottom:0;"><em>OPEN:</em> SPRINT_ARCHIVE[N+1] kickoff data · PB_ITEMS flip Backlog &rarr; In Sprint · Build sprint board cards. April provides hours, tasks, blockers, decisions. Read the code first. Always.</p>
        </div>
    </div>

    <!-- §12 WHAT NOT TO DO -->
    <div style="background:rgba(248,113,113,0.05);border:1px solid rgba(248,113,113,0.3);border-radius:0.75rem;padding:1.25rem;margin-bottom:1.25rem;">
        <h3 style="font-size:0.9rem;font-weight:700;color:#f87171;margin:0 0 0.75rem;">§12 — What Went Wrong in S12 (Learn From These)</h3>
        <div style="font-size:0.78rem;line-height:1.9;color:var(--muted);">
            <p><strong style="color:#f1f5f9;">Built in the wrong location</strong> — Sprint metrics built in Sprint Backlog tab instead of Dashboard home. Full reversal required. Root cause: did not read the code first.</p>
            <p><strong style="color:#f1f5f9;">Pre-assigned S13 tasks before planning</strong> — TA-057/058/059/060/063/065 assigned before sprint planning. April was extremely frustrated. Rule: sprint content decided at planning AFTER previous sprint closes.</p>
            <p><strong style="color:#f1f5f9;">Changed TA-008 sprint field without permission</strong> — Changed sprint:'S12' to sprint:'TBD' without authorization. Always ask before changing existing data.</p>
            <p><strong style="color:#f1f5f9;">Select option visibility bug — 20 minutes wasted</strong> — Dropdown options were white-on-white. Claude overcomplicated the fix by suggesting a custom dropdown replacement. Fix was one CSS rule: select option &#123; background: #1e293b; color: #f1f5f9; &#125;</p>
            <p><strong style="color:#f1f5f9;">Not reporting back after actions</strong> — Contract requires reporting after EVERY single action. User had to demand status reports multiple times.</p>
            <p style="margin-bottom:0;"><strong style="color:#f1f5f9;">Making changes without authorization</strong> — Changed default sprint filter, TA-008 sprint field, other items without explicit go-ahead. Rule: no code, no changes, no GitHub — nothing without April's explicit go-ahead.</p>
        </div>
    </div>

    <div style="padding:0.5rem 0;font-size:0.64rem;color:#484f58;text-align:center;">
      Auto-generated """ + today_str + """ &middot; pre-commit hook
    </div>
  </div>
"""

new_section = f"""<div id="tab-ailog" class="tab-panel">

<style>
#frag-log-wrap {{
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.84rem;
  line-height: 1.6;
  color: #c9d1d9;
}}
#frag-log-wrap .ln {{padding:0.04rem 1rem;white-space:pre-wrap;word-break:break-all}}
#frag-log-wrap .ln:hover {{background:#161b22}}
#frag-log-wrap .ln-sep {{height:3px;background:#161b22;margin:1px 0}}
#frag-log-wrap .ln-commit {{border-left:3px solid #30363d}}
#frag-log-wrap .c-key .ln-commit,#frag-log-wrap .ln-keylabel {{border-left-color:#f0883e!important}}
#frag-log-wrap .c-bug {{border-left-color:#f85149!important}}
#frag-log-wrap .c-fix {{border-left-color:#3fb950!important}}
#frag-log-wrap .ln-add {{background:rgba(63,185,80,0.04)}}
#frag-log-wrap .ln-del {{background:rgba(248,81,73,0.04)}}
#frag-log-wrap .hidden {{display:none!important}}
#frag-log-wrap .ts {{color:#484f58;user-select:none}}
#frag-log-wrap .lbl-key {{color:#f0883e;font-weight:700}}
#frag-log-wrap .lbl-bug {{color:#f85149;font-weight:700}}
#frag-log-wrap .lbl-fix {{color:#3fb950;font-weight:700}}
#frag-log-wrap .lbl-nrm {{color:#6e7681}}
#frag-log-wrap .lbl-file {{color:#d29922}}
#frag-log-wrap .lbl-add {{color:#3fb950}}
#frag-log-wrap .lbl-del {{color:#f85149}}
#frag-log-wrap .c-hash {{color:#3fb950;font-weight:700}}
#frag-log-wrap .c-msg {{color:#e6edf3}}
#frag-log-wrap .c-keylabel {{color:#f0883e;font-weight:700}}
#frag-log-wrap .c-fname {{color:#e6edf3}}
#frag-log-wrap .c-difffile {{color:#d29922;font-weight:700}}
#frag-log-wrap .d-add {{color:#3fb950}}
#frag-log-wrap .d-del {{color:#f85149}}
#frag-log-wrap mark.hl {{background:#f0883e;color:#000;border-radius:1px}}
#frag-log-wrap mark.hl.cur {{background:#ffd700}}
</style>

<div style="display:flex;height:calc(100vh - 120px);overflow:hidden;gap:0;">

  <!-- ── LEFT: Searchable terminal log ── -->
  <div id="frag-log-wrap" style="flex:1 1 0;overflow-y:auto;overflow-x:hidden;background:#0d1117;display:flex;flex-direction:column;">

    <!-- Search bar pinned at top -->
    <div style="position:sticky;top:0;z-index:10;background:#161b22;border-bottom:2px solid #f0883e;
                padding:0.5rem 0.75rem;display:flex;align-items:center;gap:0.4rem;flex-wrap:wrap;">
      <span style="color:#f0883e;font-weight:700;font-size:0.78rem;white-space:nowrap;">PROJECT LOGBOOK</span>
      <input id="frag-q" type="text" placeholder="Search commits, files, dates, errors..."
        style="flex:1;min-width:180px;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
               border-radius:3px;padding:0.3rem 0.6rem;font-size:0.76rem;
               font-family:'Courier New',monospace;outline:none;"
        autocomplete="off" spellcheck="false">
      <button id="frag-prev" style="background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
              border-radius:3px;padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#8593;</button>
      <button id="frag-next" style="background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
              border-radius:3px;padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#8595;</button>
      <button id="frag-clr" style="background:transparent;color:#8b949e;border:1px solid #30363d;
              border-radius:3px;padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#10005;</button>
      <span id="frag-cnt" style="color:#8b949e;font-size:0.68rem;white-space:nowrap;">{ln_count:,} lines</span>
      <span style="color:#484f58;font-size:0.68rem;white-space:nowrap;margin-left:auto;">Oct 2025 &ndash; {today_str}</span>
    </div>

    <!-- Filter buttons -->
    <div style="background:#0d1117;border-bottom:1px solid #21262d;padding:0.35rem 0.75rem;
                display:flex;gap:0.3rem;flex-wrap:wrap;">
      <button onclick="fragFilter('')"       class="ff-btn" data-f=""
        style="background:#1f6feb;color:#fff;border:1px solid #1f6feb;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">All</button>
      <button onclick="fragFilter('key')"    class="ff-btn" data-f="key"
        style="background:#0d1117;color:#ffd700;border:1px solid #30363d;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">&#9733; Key</button>
      <button onclick="fragFilter('bug')"    class="ff-btn" data-f="bug"
        style="background:#0d1117;color:#f85149;border:1px solid #30363d;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">Bug</button>
      <button onclick="fragFilter('fix')"    class="ff-btn" data-f="fix"
        style="background:#0d1117;color:#3fb950;border:1px solid #30363d;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">Fix</button>
      <button onclick="fragFilter('commit')" class="ff-btn" data-f="commit"
        style="background:#0d1117;color:#79c0ff;border:1px solid #30363d;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">Commits only</button>
      <button onclick="fragFilter('file')"   class="ff-btn" data-f="file"
        style="background:#0d1117;color:#d29922;border:1px solid #30363d;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">Files only</button>
      <button onclick="document.getElementById('frag-log-wrap').scrollTop=0"
        style="margin-left:auto;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">&#8679; Top</button>
      <button onclick="(function(){{var w=document.getElementById('frag-log-wrap');w.scrollTop=w.scrollHeight;}})()"
        style="background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
               border-radius:3px;padding:0.18rem 0.45rem;font-size:0.68rem;cursor:pointer;">&#8681; Latest</button>
    </div>

    <!-- Log lines -->
    <div id="frag-log-body" style="flex:1;padding-bottom:2rem;">
{log_fragment}
    </div>
  </div>

{RIGHT_PANEL_HTML}

</div>

<script>
(function(){{
  var wrap  = document.getElementById('frag-log-wrap');
  var body  = document.getElementById('frag-log-body');
  var qEl   = document.getElementById('frag-q');
  var cntEl = document.getElementById('frag-cnt');
  var all   = Array.from(body.querySelectorAll('.ln'));
  var activeFilter = '';
  var matches = [], matchIdx = -1;

  function clearMarks() {{
    body.querySelectorAll('mark.hl').forEach(function(m) {{
      m.parentNode.replaceChild(document.createTextNode(m.textContent), m);
      m.parentNode.normalize();
    }});
    matches = []; matchIdx = -1;
  }}

  function applyFilter() {{
    var q = qEl ? qEl.value.trim().toLowerCase() : '';
    clearMarks();
    var visible = [];
    all.forEach(function(el) {{
      var typeOk = true;
      if (activeFilter === 'key')         typeOk = el.classList.contains('c-key') || el.classList.contains('ln-keylabel');
      else if (activeFilter === 'bug')    typeOk = el.classList.contains('c-bug');
      else if (activeFilter === 'fix')    typeOk = el.classList.contains('c-fix');
      else if (activeFilter === 'commit') typeOk = el.classList.contains('ln-commit');
      else if (activeFilter === 'file')   typeOk = el.classList.contains('ln-file');
      var textOk = !q || (el.dataset.text || '').includes(q);
      if (typeOk && textOk) {{
        el.classList.remove('hidden');
        visible.push(el);
      }} else {{
        el.classList.add('hidden');
      }}
    }});
    if (q && visible.length) {{
      visible.forEach(function(el) {{
        var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
        var nodes = []; var n;
        while ((n = walker.nextNode())) nodes.push(n);
        nodes.forEach(function(tn) {{
          var t = tn.textContent, tl = t.toLowerCase(), idx;
          var parts = []; var last = 0;
          while ((idx = tl.indexOf(q, last)) !== -1) {{
            if (idx > last) parts.push(document.createTextNode(t.slice(last, idx)));
            var mark = document.createElement('mark');
            mark.className = 'hl';
            mark.textContent = t.slice(idx, idx + q.length);
            parts.push(mark);
            last = idx + q.length;
          }}
          if (last < t.length) parts.push(document.createTextNode(t.slice(last)));
          if (parts.length > 1) {{
            var frag = document.createDocumentFragment();
            parts.forEach(function(p) {{ frag.appendChild(p); }});
            tn.parentNode.replaceChild(frag, tn);
          }}
        }});
      }});
      matches = Array.from(body.querySelectorAll('mark.hl'));
      matchIdx = 0;
      scrollToMatch();
    }}
    if (cntEl) {{
      if (q) cntEl.textContent = matches.length ? (matchIdx+1)+'/'+matches.length+' matches' : '0 results';
      else   cntEl.textContent = visible.length.toLocaleString() + ' lines';
    }}
  }}

  function scrollToMatch() {{
    if (!matches.length) return;
    matches[matchIdx].scrollIntoView({{block:'center'}});
    if (cntEl) cntEl.textContent = (matchIdx+1)+'/'+matches.length+' matches';
  }}

  if (qEl) {{
    qEl.addEventListener('input', applyFilter);
    qEl.addEventListener('keydown', function(e) {{
      if (e.key === 'Enter') {{ matchIdx = (matchIdx+1) % (matches.length||1); scrollToMatch(); }}
    }});
  }}

  document.getElementById('frag-prev').addEventListener('click', function() {{
    if (!matches.length) return;
    matchIdx = (matchIdx - 1 + matches.length) % matches.length;
    scrollToMatch();
  }});
  document.getElementById('frag-next').addEventListener('click', function() {{
    if (!matches.length) return;
    matchIdx = (matchIdx + 1) % matches.length;
    scrollToMatch();
  }});
  document.getElementById('frag-clr').addEventListener('click', function() {{
    if (qEl) qEl.value = '';
    activeFilter = '';
    document.querySelectorAll('.ff-btn').forEach(function(b) {{
      b.style.background  = b.dataset.f === '' ? '#1f6feb' : '#0d1117';
      b.style.borderColor = b.dataset.f === '' ? '#1f6feb' : '#30363d';
    }});
    applyFilter();
  }});

  window.fragFilter = function(f) {{
    activeFilter = f;
    document.querySelectorAll('.ff-btn').forEach(function(b) {{
      var on = b.dataset.f === f;
      b.style.background  = on ? '#1f6feb' : '#0d1117';
      b.style.borderColor = on ? '#1f6feb' : '#30363d';
    }});
    applyFilter();
  }};

  window._devlogSetQuery = function(q) {{
    if (qEl) {{ qEl.value = q; applyFilter(); }}
  }};

  if (cntEl) cntEl.textContent = all.length.toLocaleString() + ' lines';
}})();
</script>

</div><!-- /tab-ailog -->
"""

new_lines = lines[:start_line] + [new_section] + lines[end_line+1:]

with open(DASHBOARD, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

size = os.path.getsize(DASHBOARD)
print(f"Done. Dashboard is now {size:,} bytes ({size//1024} KB)")
