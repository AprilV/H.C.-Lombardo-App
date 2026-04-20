import html
import os
import subprocess

REPO = "c:/ReactGitEC2/IS330/H.C Lombardo App"

KEY_COMMITS = {
    '63d729e6': 'INITIAL COMMIT — first line of code ever written, Flask/SQLite, app.py 56 lines',
    'f984bb4a': 'POSTGRESQL MIGRATION — SQLite abandoned, db_config.py born, all 32 teams',
    '9caf343e': 'ANALYTICS API — api_routes_hcl.py feature engineering views, 5 new endpoints',
    'c08685c8': '7,263 GAMES LOADED — full 1999-2025 historical dataset, 4min 23sec load time',
    '3c9f7a03': 'ML PERFORMANCE TRACKING — 54.6% accuracy vs Vegas 52.5%, ModelPerformance.js created',
    'a8f9aa8e': 'SCORE AND SPREAD MODEL — point spread regression, 10.35 MAE, dual model architecture',
    '6b28364a': 'EC2 PERMANENT FIX — all Render/Railway refs removed, 19 files deleted, this is the architecture today',
    '63148f67': 'hcl_test SCHEMA WORKFLOW — TEST workflow created; train_xgb_winner.py hardcoded this schema, became TA-057',
    'e15d4d9c': 'ML CREDS FIX — hardcoded passwords replaced with db_config environment variables',
    '03313def': 'XGBOOST 46-FEATURE — 60.7% winner accuracy 11.6 MAE spread, these model files still on EC2 today',
    '1d7554e4': 'ELO RATING SYSTEM — FiveThirtyEight-style 252-line class, PHI(1768) BAL(1705) BUF(1702) top 3',
    '83a2b97c': 'BACKGROUND UPDATER SIMPLIFIED — team standings only, game data complete for season',
    '1cc206ac': 'SPRING 2026 CAPSTONE KICKOFF — PM dashboard created from scratch, all data hardcoded',
    '0dba4f20': 'S12 BUG FIXES — App.js routing fixed, hardcoded aprilv120 password removed, broken import fixed',
    '66e4e2ce': 'EXECUTIVE DARK OVERHAUL — 38 files, 1441 insertions 11739 deletions, light mode CSS deleted forever',
    '6d5c66e7': 'SPRINT 12 CLOSED GREEN — 8 of 9 tasks delivered, TA-008 blocked AWS MFA',
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
