import html
import os
import subprocess

REPO = "c:/ReactGitEC2/IS330/H.C Lombardo App"

KEY_COMMITS = {
    # ── PHASE 0-1: INITIAL BUILD ──────────────────────────────────────────────
    '63d729e6': 'INITIAL COMMIT — first line of code, Flask/SQLite, app.py 56 lines, templates/index.html',
    'f984bb4a': 'POSTGRESQL MIGRATION — SQLite abandoned, db_config.py created, all 32 teams, ESPN logos',
    # ── PHASE 2: REACT + ANALYTICS ───────────────────────────────────────────
    '9caf343e': 'ANALYTICS API — api_routes_hcl.py, 4 analytical views (betting/weather/rest/referees), 5 endpoints',
    '0982849b': 'ANALYTICS DASHBOARD — Analytics.js created, 6 tabs in React, stat legends, dropdown styling fixed',
    # ── PHASE 3: HISTORICAL DATA + ML ────────────────────────────────────────
    'c08685c8': '7,263 GAMES LOADED — full 1999-2025 dataset, 14,312 team-game records, 4min 23sec, 100% EPA',
    '3c9f7a03': 'ML PERFORMANCE TRACKING — 54.6% vs Vegas 52.5%, ModelPerformance.js, 692 games, 3 seasons tracked',
    'a8f9aa8e': 'SCORE AND SPREAD MODEL — point spread regression added, 10.35 MAE, dual model architecture',
    '5253d026': 'LIVE SCORES TICKER — LiveGamesTicker.js created, drag-to-scroll, AI predictions, team logos',
    # ── PHASE 4: RENDER/RAILWAY FAILURE SEQUENCE (14 attempts, all failed) ───
    '1d80012c': 'RENDER ATTEMPT 1 — add python-dotenv to GitHub Actions (start of 14-commit failure sequence)',
    '3da12a16': 'RENDER ATTEMPT 2 — move python-dotenv first to force workflow refresh',
    '53c06ac0': 'RENDER ATTEMPT 3 — make dotenv import optional for GitHub Actions',
    '9147217a': 'RENDER ATTEMPT 4 — add SSL requirement for Render database connections',
    '440d24b5': 'RENDER ATTEMPT 5 — replace entire workflow file to clear GitHub cache',
    'c7f4bd6d': 'RENDER ATTEMPT 6 — add gssencmode=disable for PostgreSQL SSL',
    '2bdbe90f': 'RENDER ATTEMPT 7 — add verification step to confirm gssencmode in code',
    '2969e68e': 'RENDER FINAL ATTEMPT — MAJOR FIX: remove ALL Render refs, but SSH heredoc still broken',
    '6b28364a': 'EC2 PERMANENT FIX — ALL Render/Railway removed, 19 files deleted, SSH single-line commands, THIS IS THE ARCHITECTURE TODAY',
    # ── PHASE 5: XGBOOST TRAINING SEQUENCE ───────────────────────────────────
    '6587f437': 'XGBOOST ATTEMPT 1 — update ML scripts to 2020-2025 seasons',
    'e15d4d9c': 'XGBOOST ATTEMPT 2 — hardcoded passwords replaced with db_config (was aprilv120 hardcoded)',
    '73c2e67e': 'XGBOOST ATTEMPT 3 — add sys.path for db_config import',
    '87c40faf': 'XGBOOST ATTEMPT 4 — fix import order for db_config',
    '7607e3a6': 'XGBOOST ATTEMPT 5 — fix spread training script encoding',
    '80f3155a': 'XGBOOST ATTEMPT 6 — clean up orphaned CTE code from spread query',
    '150177f2': 'XGBOOST ATTEMPT 7 — fix spread model save path to ml/models/',
    '79f92425': 'XGBOOST ATTEMPT 8 — first working models, 61% winner 11.1 MAE, no data leakage',
    '114f8772': 'XGBOOST ATTEMPT 9 — switch to production hcl schema (had been using hcl_test)',
    '03313def': 'XGBOOST FINAL — 46-feature set, 60.7% winner accuracy, 11.6 MAE spread, THESE ARE THE MODELS ON EC2 TODAY',
    '63148f67': 'hcl_test SCHEMA ORIGIN — TEST workflow hardcodes hcl_test; later train_xgb_winner.py kept it — became TA-057',
    # ── PHASE 5: ELO + COLOR UNIFICATION ─────────────────────────────────────
    '1d7554e4': 'ELO RATING SYSTEM — ml/elo_ratings.py created, 252 lines, FiveThirtyEight-style, PHI(1768) top rated',
    'f6cf12a3': 'VERSION v0.1.0 ALPHA — color scheme unification complete, first version tag',
    # ── PHASE 5: NFLVERSE BACKGROUND UPDATER FIXES (Dec 21) ──────────────────
    '5d2e5dbf': 'BACKGROUND UPDATER FIX 1 — standalone service added (fixes multi-worker gunicorn issue)',
    'a9cf27c3': 'BACKGROUND UPDATER FIX 2 — fix method name run_full_update vs run_update',
    '799bfd80': 'BACKGROUND UPDATER FIX 3 — fix import path for multi_source_data_fetcher',
    '2a436850': 'BACKGROUND UPDATER FIX 4 — add game-level data updates to background service',
    '555b828f': 'BACKGROUND UPDATER FIX 5 — add nfl_data_py dependency',
    '1137baea': 'BACKGROUND UPDATER FIX 6 — fix database connection to use environment variables',
    '435f24a9': 'BACKGROUND UPDATER FIX 7 — fix NFLverse with inline implementation and error handling',
    '83a2b97c': 'BACKGROUND UPDATER FINAL — simplified to team standings only, game data is complete for season',
    # ── PHASE 6: SPRING 2026 CAPSTONE KICKOFF ────────────────────────────────
    '1cc206ac': 'SPRING 2026 CAPSTONE KICKOFF — PM dashboard built from scratch, 1 commit, full dashboard',
    '2c69668e': 'REMOVE ALL LOCALSTORAGE — everything hardcoded and publicly visible, no exceptions',
    '08773fa7': 'HARDCODE HOURS/RETRO/REPORT — localStorage eliminated from these sections',
    '61d5f532': 'WEEKLY REPORT — remove all inputs/localStorage, auto-renders from hardcoded data',
    # ── SPRINT 12 ─────────────────────────────────────────────────────────────
    '0dba4f20': 'S12 BUG FIXES — App.js routing fixed (wrong components), aprilv120 password removed, broken import fixed',
    '66e4e2ce': 'EXECUTIVE DARK OVERHAUL — 38 files, 1441 insertions, 11739 DELETIONS, all light-mode CSS gone forever',
    '5f5f3444': 'TASK RESOLUTION MODAL — click task title to see resolution, TASK_DETAILS data structure, 267 lines added',
    '6d5c66e7': 'SPRINT 12 CLOSED GREEN — 8 of 9 tasks, 32 hours, TA-008 blocked AWS MFA locked',
    '6e141424': 'PRODUCT BACKLOG TRACKER — unified from 2 sub-tabs, sprint filter, print/CSV, date-gating',
    '7d59f65e': 'AI PROJECT LOG v1 — first version deployed (reformatted summary, NOT a real log — replaced by this)',
}


def get_diff(commit_hash):
    result = subprocess.run(
        ['git', 'show', commit_hash, '--no-color'],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=REPO
    )
    return result.stdout


result = subprocess.run(
    ['git', 'log', '--reverse', '--stat',
     '--date=format:%Y-%m-%d %H:%M:%S',
     '--format=<<<COMMIT>>>|%H|%ad|%s'],
    capture_output=True, text=True, encoding='utf-8', errors='replace',
    cwd=REPO
)
log_text = result.stdout

lines = log_text.split('\n')
parts = []
current_commit = {}
current_stats = []

for line in lines:
    if line.startswith('<<<COMMIT>>>|'):
        if current_commit:
            parts.append((current_commit.copy(), current_stats.copy()))
        current_commit = {}
        current_stats = []
        tokens = line.split('|', 3)
        full_h = tokens[1].strip() if len(tokens) > 1 else ''
        current_commit['hash'] = full_h
        current_commit['short'] = full_h[:8]
        current_commit['date'] = tokens[2].strip() if len(tokens) > 2 else ''
        current_commit['msg'] = tokens[3].strip() if len(tokens) > 3 else ''
    elif current_commit and line.strip():
        current_stats.append(line)

if current_commit:
    parts.append((current_commit.copy(), current_stats.copy()))

out = []
out.append('<pre style="background:#0d1117; color:#c9d1d9; font-family:\'Courier New\',Courier,monospace; '
           'font-size:0.72rem; line-height:1.65; padding:1.5rem; border-radius:0.5rem; '
           'overflow-x:auto; white-space:pre; border:1px solid #30363d;">')
out.append(html.escape('=' * 80) + '\n')
out.append('<span style="color:#f0883e;font-weight:bold;">H.C. LOMBARDO NFL ANALYTICS — COMPLETE DEVELOPER LOG</span>\n')
out.append(html.escape('Total: ' + str(len(parts)) + ' commits | Oct 7, 2025 – Apr 19, 2026') + '\n')
out.append(html.escape('Every commit. Every file. Every change. Every bug. Every failed attempt. Every fix.') + '\n')
out.append(html.escape('Timestamps: local time (PDT/PST). Author: AprilV (ChatGPT-assisted Oct 2025, Claude Code Nov 2025+).') + '\n')
out.append(html.escape('FULL 24MB DIFF LOG (all diffs, all line numbers): docs/ai_reference/DEV_LOG_FULL.txt') + '\n')
out.append(html.escape('=' * 80) + '\n\n')

for commit, cstats in parts:
    h = commit.get('short', '')
    full_h = commit.get('hash', '')
    date = commit.get('date', '')
    msg = commit.get('msg', '')

    is_key = h in KEY_COMMITS

    if is_key:
        label = KEY_COMMITS[h]
        out.append('\n<span style="color:#f0883e;">' + html.escape('▓' * 80) + '</span>\n')
        out.append('<span style="color:#f0883e;font-weight:bold;">KEY: ' + html.escape(label) + '</span>\n')
        out.append('<span style="color:#f0883e;">' + html.escape(date) + '</span>'
                   ' | <span style="color:#3fb950;font-weight:bold;">' + html.escape(h) + '</span>'
                   ' | <span style="color:#79c0ff;">' + html.escape(msg) + '</span>\n')
    else:
        out.append('<span style="color:#21262d;">' + html.escape('─' * 80) + '</span>\n')
        out.append('<span style="color:#8b949e;">' + html.escape(date) + '</span>'
                   ' | <span style="color:#3fb950;">' + html.escape(h) + '</span>'
                   ' | ' + html.escape(msg) + '\n')

    for s in cstats:
        s = s.rstrip()
        if not s:
            continue
        if ' changed,' in s:
            out.append('<span style="color:#79c0ff;">  ' + html.escape(s) + '</span>\n')
        elif 'Bin ' in s:
            out.append('<span style="color:#6e7681;">  ' + html.escape(s) + '</span>\n')
        elif '|' in s:
            fname_part, rest_part = s.split('|', 1)
            colored_rest = ''
            for ch in rest_part:
                if ch == '+':
                    colored_rest += '<span style="color:#3fb950;">+</span>'
                elif ch == '-':
                    colored_rest += '<span style="color:#f85149;">-</span>'
                else:
                    colored_rest += html.escape(ch)
            out.append('  <span style="color:#e6edf3;">' + html.escape(fname_part) + '</span>|' + colored_rest + '\n')
        else:
            out.append('  ' + html.escape(s) + '\n')

    if is_key and full_h:
        diff = get_diff(full_h)
        if diff:
            out.append('\n<span style="color:#58a6ff;">' + html.escape('┌' + '─' * 78) + '</span>\n')
            out.append('<span style="color:#58a6ff;">│ ACTUAL CODE: git show ' + html.escape(h) + '</span>\n')
            out.append('<span style="color:#58a6ff;">' + html.escape('└' + '─' * 78) + '</span>\n')
            diff_lines = diff.split('\n')
            shown = 0
            MAX_DIFF = 500
            in_diff = False
            for dl in diff_lines:
                if dl.startswith('diff --git'):
                    in_diff = True
                if not in_diff:
                    continue
                if shown >= MAX_DIFF:
                    out.append('<span style="color:#8b949e;">  ... [see docs/ai_reference/DEV_LOG_FULL.txt for complete diff]</span>\n')
                    break
                if dl.startswith('+') and not dl.startswith('+++'):
                    out.append('<span style="color:#3fb950;">' + html.escape(dl) + '</span>\n')
                elif dl.startswith('-') and not dl.startswith('---'):
                    out.append('<span style="color:#f85149;">' + html.escape(dl) + '</span>\n')
                elif dl.startswith('@@'):
                    out.append('<span style="color:#79c0ff;">' + html.escape(dl) + '</span>\n')
                elif dl.startswith('diff --git'):
                    out.append('\n<span style="color:#d29922;">' + html.escape(dl) + '</span>\n')
                elif dl.startswith(('---', '+++', 'index ', 'new file', 'deleted file', 'Binary')):
                    out.append('<span style="color:#6e7681;">' + html.escape(dl) + '</span>\n')
                else:
                    out.append(html.escape(dl) + '\n')
                shown += 1
            out.append('<span style="color:#58a6ff;">' + html.escape('─' * 80) + '</span>\n')

    out.append('\n')

out.append('</pre>')

outpath = 'c:/ReactGitEC2/IS330/H.C Lombardo App/devlog_output.html'
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(''.join(out))

size = os.path.getsize(outpath)
print(f"Generated: {size:,} bytes ({size//1024} KB), {len(parts)} commits processed")
