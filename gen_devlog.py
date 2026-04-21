"""
gen_devlog.py — H.C. Lombardo NFL Analytics
Generates:
  docs/devlog/index.html          — Project Logbook (standalone page)
  docs/devlog/CLAUDE_SESSION_BRIEF.md — Machine-readable session brief for Claude
  devlog_output.html              — Fragment embedded in Dashboard §13

Run via pre-commit hook or manually.
"""
import html
import json
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

REPO          = "c:/ReactGitEC2/IS330/H.C Lombardo App"
LOGBOOK_OUT   = "c:/ReactGitEC2/IS330/H.C Lombardo App/docs/devlog/index.html"
BRIEF_OUT     = "c:/ReactGitEC2/IS330/H.C Lombardo App/docs/devlog/CLAUDE_SESSION_BRIEF.md"
FRAGMENT_OUT  = "c:/ReactGitEC2/IS330/H.C Lombardo App/devlog_output.html"
ARCHIVE_DIR   = Path("c:/ReactGitEC2/IS330/H.C Lombardo App/docs/devlog/archive")
MAX_DIFF      = 300

KEY_COMMITS = {
    '63d729e6': 'INITIAL COMMIT — first line of code, Flask/SQLite, app.py 56 lines',
    'f984bb4a': 'POSTGRESQL MIGRATION — SQLite abandoned, db_config.py created, all 32 teams',
    '9caf343e': 'ANALYTICS API — api_routes_hcl.py, 4 analytical views, 5 endpoints',
    '0982849b': 'ANALYTICS DASHBOARD — Analytics.js, 6 tabs in React, stat legends',
    'c08685c8': '7,263 GAMES LOADED — full 1999-2025 dataset, 14,312 records, 4m 23s load',
    '3c9f7a03': 'ML PERFORMANCE TRACKING — 54.6% vs Vegas 52.5%, ModelPerformance.js',
    'a8f9aa8e': 'SCORE AND SPREAD MODEL — point spread regression, 10.35 MAE',
    '5253d026': 'LIVE SCORES TICKER — LiveGamesTicker.js, drag-to-scroll, AI predictions',
    '1d80012c': 'RENDER ATTEMPT #1  — add python-dotenv (start of 14-commit failure sequence)',
    '3da12a16': 'RENDER ATTEMPT #2  — move python-dotenv first',
    '53c06ac0': 'RENDER ATTEMPT #3  — make dotenv import optional',
    '9147217a': 'RENDER ATTEMPT #4  — add SSL requirement',
    '440d24b5': 'RENDER ATTEMPT #5  — replace entire workflow file',
    'c7f4bd6d': 'RENDER ATTEMPT #6  — add gssencmode=disable',
    '2bdbe90f': 'RENDER ATTEMPT #7  — add gssencmode verification step',
    '2969e68e': 'RENDER ATTEMPT #8  — remove all Render refs, SSH heredoc still broken',
    '6b28364a': 'EC2 FIX — all Render/Railway removed, 19 files deleted, THIS IS THE ARCH TODAY',
    '6587f437': 'XGBOOST #1 — update ML scripts to 2020-2025 seasons',
    'e15d4d9c': 'XGBOOST #2 — FIX: hardcoded password aprilv120 replaced with db_config',
    '73c2e67e': 'XGBOOST #3 — add sys.path for db_config import',
    '87c40faf': 'XGBOOST #4 — fix import order for db_config',
    '7607e3a6': 'XGBOOST #5 — FIX: spread training script encoding error',
    '80f3155a': 'XGBOOST #6 — FIX: clean up orphaned CTE code from spread query',
    '150177f2': 'XGBOOST #7 — FIX: spread model save path to ml/models/',
    '79f92425': 'XGBOOST #8 — WORKING: 61% winner accuracy, 11.1 MAE, no data leakage',
    '114f8772': 'XGBOOST #9 — FIX: switch to production hcl schema (was hcl_test)',
    '03313def': 'XGBOOST FINAL — 46-feature set, 60.7% winner, 11.6 MAE — models on EC2 today',
    '63148f67': 'BUG ORIGIN: hcl_test SCHEMA — workflow hardcodes hcl_test — became TA-057',
    '1d7554e4': 'ELO SYSTEM — ml/elo_ratings.py 252 lines, FiveThirtyEight-style',
    'f6cf12a3': 'v0.1.0 ALPHA — color scheme unification, first version tag',
    '5d2e5dbf': 'BGUPD FIX #1 — standalone service, fixes multi-worker gunicorn',
    'a9cf27c3': 'BGUPD FIX #2 — wrong method name run_full_update vs run_update',
    '799bfd80': 'BGUPD FIX #3 — wrong import path for multi_source_data_fetcher',
    '2a436850': 'BGUPD FIX #4 — add game-level data updates',
    '555b828f': 'BGUPD FIX #5 — add missing nfl_data_py dependency',
    '1137baea': 'BGUPD FIX #6 — fix DB connection, env vars not hardcoded',
    '435f24a9': 'BGUPD FIX #7 — fix NFLverse inline implementation',
    '83a2b97c': 'BGUPD FINAL — simplified to team standings only',
    '1cc206ac': 'SPRING 2026 KICKOFF — PM dashboard built from scratch, all hardcoded',
    '2c69668e': 'REMOVE LOCALSTORAGE — hardcoded only, no exceptions',
    '08773fa7': 'HARDCODE HOURS/RETRO/REPORT — localStorage fully eliminated',
    '61d5f532': 'WEEKLY REPORT — remove all inputs/localStorage, auto-renders',
    '0dba4f20': 'FIX S12 — App.js wrong components, hardcoded password removed',
    '66e4e2ce': 'DARK OVERHAUL — 38 files, 1441 insertions, 11739 DELETIONS',
    '5f5f3444': 'TASK MODAL — click task title, TASK_DETAILS struct, 267 lines added',
    '6d5c66e7': 'SPRINT 12 CLOSED GREEN — 8/9 tasks, 32 hours, TA-008 blocked',
    '6e141424': 'PRODUCT BACKLOG TRACKER — sprint filter, print/CSV, date-gating',
    '7d59f65e': 'AI LOG v1 — summary only, replaced by this',
}

FIX_RE = re.compile(r'\b(fix|fixed|fixes|resolved|corrected|working|final)\b', re.I)
BUG_RE = re.compile(r'\b(fix|bug|error|broken|fail|wrong|crash|except|traceback|missing|attempt|retry|revert)\b', re.I)

CONTRACT_TEXT = """STATUS: ACTIVE — NON-NEGOTIABLE
APPLIES TO: ALL AI ASSISTANTS — PRIORITY: ABSOLUTE

1. FULL INGESTION REQUIRED — Read all docs before responding. No skimming.
2. AUTHORITY ORDER — AI_EXECUTION_CONTRACT > READ_THIS_FIRST > BEST_PRACTICES > codebase
3. NO ASSUMPTIONS — Ask if anything is unclear. Never guess intent or scope.
4. CORRECTNESS OVER SPEED — Best effort is not acceptable.
5. SYSTEM-WIDE AWARENESS — Identify ALL affected files before any change.
6. MANDATORY CLEANUP — Remove dead code. No commented-out code. No parallel implementations.
7. QUESTION-FIRST — Ambiguous? Stop. Ask. Wait.
8. TEST LOCALLY — Show April. Get approval. Then commit. Never skip.
9. RESPONSE FORMAT — State: documents read / files reviewed / files impacted / changes proposed / open questions.
10. FINAL DIRECTIVE — The AI is not here to be fast. The AI is here to be correct.

Full contract: docs/ai_reference/AI_EXECUTION_CONTRACT.md"""


# ── Git helpers ───────────────────────────────────────────────────────────────

def git(*args):
    r = subprocess.run(['git'] + list(args),
        capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=REPO)
    return r.stdout


def parse_log():
    raw = git('log', '--reverse', '--patch', '--stat',
              '--date=format:%Y-%m-%d %H:%M:%S',
              '--format=COMMIT_START|%H|%ad|%s')
    commits, cur, stat_lines, diff_lines, in_diff = [], None, [], [], False
    for line in raw.split('\n'):
        if line.startswith('COMMIT_START|'):
            if cur:
                cur['stat'] = stat_lines[:]
                cur['diff'] = diff_lines[:]
                commits.append(cur)
            parts = line.split('|', 3)
            full_h = parts[1].strip() if len(parts) > 1 else ''
            cur = {'hash': full_h, 'short': full_h[:8],
                   'date': parts[2].strip() if len(parts) > 2 else '',
                   'msg':  parts[3].strip() if len(parts) > 3 else ''}
            stat_lines, diff_lines, in_diff = [], [], False
        elif cur:
            if line.startswith('diff --git'):
                in_diff = True
            if in_diff:
                diff_lines.append(line)
            elif line.strip() and line.strip() != '---':
                stat_lines.append(line)
    if cur:
        cur['stat'] = stat_lines[:]
        cur['diff'] = diff_lines[:]
        commits.append(cur)
    return commits


def classify(commit):
    h, msg = commit['short'], commit['msg'].lower()
    if h in KEY_COMMITS:
        lbl = KEY_COMMITS[h].upper()
        if 'ATTEMPT' in lbl or 'BUG' in lbl or 'FAIL' in lbl:
            return 'bug'
        if 'FIX' in lbl or 'WORKING' in lbl or 'FINAL' in lbl:
            return 'fix'
        return 'key'
    if FIX_RE.search(msg):
        return 'fix'
    if BUG_RE.search(msg):
        return 'bug'
    return 'normal'


def e(s):
    return html.escape(str(s))


# ── Build terminal log lines ──────────────────────────────────────────────────

def build_log_lines(commits):
    lines = []
    for c in commits:
        h, date, msg = c['short'], c['date'], c['msg']
        ctype  = classify(c)
        is_key = h in KEY_COMMITS

        TYPE_LABELS = {'key': 'COMMIT ', 'bug': 'BUG    ', 'fix': 'FIX    ', 'normal': 'COMMIT '}
        TYPE_CLASSES = {'key': 'lbl-key', 'bug': 'lbl-bug', 'fix': 'lbl-fix', 'normal': 'lbl-nrm'}

        lines.append(
            f'<div class="ln ln-commit c-{ctype}" data-ts="{e(date)}" '
            f'data-text="{e((h+" "+msg).lower())}">'
            f'<span class="ts">[{e(date)}]</span> '
            f'<span class="{TYPE_CLASSES[ctype]}">{TYPE_LABELS[ctype]}</span> '
            f'<span class="c-hash">{e(h)}</span> &mdash; '
            f'<span class="c-msg">{e(msg)}</span>'
            f'</div>'
        )

        if is_key:
            lines.append(
                f'<div class="ln ln-keylabel" data-ts="{e(date)}" data-text="{e(KEY_COMMITS[h].lower())}">'
                f'<span class="ts">[{e(date)}]</span> '
                f'<span class="lbl-key">*** KEY </span>'
                f'<span class="c-keylabel">{e(KEY_COMMITS[h])}</span>'
                f'</div>'
            )

        for s in c['stat']:
            s = s.rstrip()
            if not s:
                continue
            if ' changed,' in s:
                lines.append(
                    f'<div class="ln ln-stat" data-ts="{e(date)}" data-text="{e(s.lower())}">'
                    f'<span class="ts">[{e(date)}]</span> '
                    f'<span class="lbl-stat">STAT   </span>'
                    f'<span class="c-stat">{e(s.strip())}</span>'
                    f'</div>'
                )
            elif '|' in s and 'Bin ' not in s:
                fname, rest = s.split('|', 1)
                cr = ''.join(
                    f'<span class="d-add">+</span>' if ch == '+' else
                    f'<span class="d-del">-</span>' if ch == '-' else
                    e(ch) for ch in rest
                )
                lines.append(
                    f'<div class="ln ln-file" data-ts="{e(date)}" data-text="{e(s.lower())}">'
                    f'<span class="ts">[{e(date)}]</span> '
                    f'<span class="lbl-file">FILE   </span>'
                    f'<span class="c-fname">{e(fname)}</span>|{cr}'
                    f'</div>'
                )

        if c['diff']:
            shown = 0
            for dl in c['diff']:
                if shown >= MAX_DIFF:
                    lines.append(
                        f'<div class="ln ln-trunc" data-ts="{e(date)}" data-text="truncated">'
                        f'<span class="ts">[{e(date)}]</span> '
                        f'<span class="lbl-meta">...    </span>'
                        f'<span class="c-meta">diff truncated — full: docs/ai_reference/DEV_LOG_FULL.txt</span>'
                        f'</div>'
                    )
                    break
                if dl.startswith('diff --git'):
                    fname = dl.split(' b/', 1)[1] if ' b/' in dl else dl
                    lines.append(
                        f'<div class="ln ln-difffile" data-ts="{e(date)}" data-text="{e(dl.lower())}">'
                        f'<span class="ts">[{e(date)}]</span> '
                        f'<span class="lbl-file">DIFF   </span>'
                        f'<span class="c-difffile">{e(fname)}</span>'
                        f'</div>'
                    )
                elif is_key or ctype in ('bug', 'fix'):
                    if dl.startswith('+') and not dl.startswith('+++'):
                        lines.append(
                            f'<div class="ln ln-add" data-ts="{e(date)}" data-text="{e(dl.lower())}">'
                            f'<span class="ts">[{e(date)}]</span> '
                            f'<span class="lbl-add">+      </span>'
                            f'<span class="d-add">{e(dl)}</span>'
                            f'</div>'
                        )
                    elif dl.startswith('-') and not dl.startswith('---'):
                        lines.append(
                            f'<div class="ln ln-del" data-ts="{e(date)}" data-text="{e(dl.lower())}">'
                            f'<span class="ts">[{e(date)}]</span> '
                            f'<span class="lbl-del">-      </span>'
                            f'<span class="d-del">{e(dl)}</span>'
                            f'</div>'
                        )
                    elif dl.startswith('@@'):
                        lines.append(
                            f'<div class="ln ln-hunk" data-ts="{e(date)}" data-text="{e(dl.lower())}">'
                            f'<span class="ts">[{e(date)}]</span> '
                            f'<span class="lbl-meta">@@     </span>'
                            f'<span class="c-hunk">{e(dl)}</span>'
                            f'</div>'
                        )
                shown += 1

        lines.append('<div class="ln ln-sep"></div>')
    return lines


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#0d1117;color:#c9d1d9;
  font-family:'Courier New',Courier,monospace;font-size:0.84rem;line-height:1.6;
  overflow-x:hidden}

/* ── Header ── */
#hdr{position:fixed;top:0;left:0;right:0;z-index:300;
  background:#0d1117;border-bottom:2px solid #f0883e;padding:0.45rem 1rem;
  display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap}
#hdr-title{color:#f0883e;font-weight:700;font-size:0.85rem;white-space:nowrap}
#hdr-meta{color:#484f58;font-size:0.72rem;white-space:nowrap}
#hdr-search{flex:1;min-width:200px;background:#161b22;color:#c9d1d9;
  border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.6rem;
  font-size:0.76rem;font-family:inherit;outline:none}
#hdr-search:focus{border-color:#f0883e}
#hdr-range{background:#161b22;color:#c9d1d9;border:1px solid #30363d;
  border-radius:3px;padding:0.3rem 0.6rem;font-size:0.76rem;cursor:pointer}
#live-ind{font-size:0.68rem;padding:0.15rem 0.5rem;border-radius:3px;
  border:1px solid #30363d;color:#484f58;white-space:nowrap}
#hdr-cnt{color:#484f58;font-size:0.7rem;white-space:nowrap;margin-left:auto}

/* ── Contract banner ── */
#contract{background:#161b22;border-bottom:1px solid rgba(251,191,36,0.3);
  padding:0;margin-top:42px}
#contract-toggle{padding:0.4rem 1rem;cursor:pointer;color:#fbbf24;
  font-size:0.76rem;font-weight:700;user-select:none;
  display:flex;align-items:center;gap:0.5rem}
#contract-toggle:hover{background:rgba(251,191,36,0.05)}
#contract-body{display:none;padding:0.75rem 1rem 1rem;color:#c9d1d9;
  font-size:0.74rem;line-height:1.8;white-space:pre-wrap;
  border-top:1px solid rgba(251,191,36,0.2)}
#contract-body.open{display:block}

/* ── Tabs ── */
#tabs{display:flex;background:#0d1117;border-bottom:1px solid #30363d;
  position:sticky;top:42px;z-index:200}
.tab{background:none;border:none;border-bottom:2px solid transparent;
  color:#8b949e;padding:0.5rem 1.25rem;font-size:0.78rem;font-family:inherit;
  cursor:pointer;white-space:nowrap}
.tab:hover{color:#c9d1d9;background:#161b22}
.tab.active{color:#f0883e;border-bottom-color:#f0883e}

/* ── Tab panels ── */
.panel{display:none;min-height:calc(100vh - 120px)}
.panel.active{display:block}

/* ── Log lines ── */
#log-body{padding-bottom:3rem}
.ln{padding:0.05rem 1rem;white-space:pre-wrap;word-break:break-all}
.ln:hover{background:#161b22}
.ln-sep{height:3px;background:#161b22;margin:1px 0}
.ln-commit{border-left:3px solid #30363d}
.c-key .ln-commit,.ln-keylabel{border-left-color:#f0883e!important}
.c-bug{border-left-color:#f85149!important}
.c-fix{border-left-color:#3fb950!important}
.ln-add{background:rgba(63,185,80,0.04)}
.ln-del{background:rgba(248,81,73,0.04)}
.ln-live{border-left:3px solid #58a6ff;background:rgba(88,166,255,0.04)}
.hidden{display:none!important}

/* ── Colors ── */
.ts{color:#484f58;user-select:none}
.lbl-key{color:#f0883e;font-weight:700}
.lbl-bug{color:#f85149;font-weight:700}
.lbl-fix{color:#3fb950;font-weight:700}
.lbl-nrm{color:#6e7681}
.lbl-stat{color:#79c0ff}
.lbl-file{color:#d29922}
.lbl-add{color:#3fb950}
.lbl-del{color:#f85149}
.lbl-meta,.c-meta{color:#484f58}
.lbl-live{color:#58a6ff;font-weight:700}
.c-hash{color:#3fb950;font-weight:700}
.c-msg{color:#e6edf3}
.c-keylabel{color:#f0883e;font-weight:700}
.c-stat{color:#79c0ff}
.c-fname,.c-livefile{color:#e6edf3}
.c-difffile{color:#d29922;font-weight:700}
.c-hunk{color:#79c0ff}
.d-add{color:#3fb950}.d-del{color:#f85149}
mark.hl{background:#f0883e;color:#000;border-radius:1px}
mark.hl.cur{background:#ffd700}

/* ── Calendar ── */
#cal-wrap{padding:1rem}
#cal-range-bar{display:flex;gap:0.5rem;align-items:center;
  margin-bottom:1rem;flex-wrap:wrap}
#cal-range-bar label{color:#8b949e;font-size:0.74rem}
#cal-range-bar input,#cal-range-bar button{background:#161b22;color:#c9d1d9;
  border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.6rem;
  font-size:0.76rem;font-family:inherit;cursor:pointer}
#cal-grid{display:flex;gap:1.5rem;flex-wrap:wrap}
.cal-month{min-width:200px}
.cal-month h4{color:#f0883e;margin-bottom:0.5rem;font-size:0.78rem}
.cal-days{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.cal-day-hdr{color:#484f58;font-size:0.65rem;text-align:center;padding:2px 0}
.cal-day{font-size:0.7rem;text-align:center;padding:3px 2px;
  border-radius:2px;cursor:default;color:#484f58}
.cal-day.has-data{color:#c9d1d9;cursor:pointer;background:#161b22}
.cal-day.has-data:hover{background:#30363d;color:#f0883e}
.cal-day.selected{background:#f0883e!important;color:#000!important}
.cal-day.today{border:1px solid #3fb950}
#cal-day-log{margin-top:1rem;border:1px solid #30363d;border-radius:4px;
  max-height:60vh;overflow-y:auto;background:#0d1117}
#cal-day-log-hdr{padding:0.4rem 1rem;border-bottom:1px solid #30363d;
  color:#f0883e;font-weight:700;font-size:0.76rem;
  position:sticky;top:0;background:#0d1117}

/* ── Status bar ── */
#statusbar{position:fixed;bottom:0;left:0;right:0;background:#0d1117;
  border-top:1px solid #30363d;padding:0.2rem 1rem;
  display:flex;justify-content:space-between;font-size:0.68rem;color:#484f58;
  z-index:200}
"""


# ── JavaScript ────────────────────────────────────────────────────────────────

def make_js(total_commits, total_lines):
    return f"""
(function(){{
  var ARCHIVE_URL = 'archive/';          /* static git-history JSON files */
  var WATCHER_URL = 'http://localhost:8765/archive/'; /* live file-watcher (log_watcher.py) */
  var TODAY    = new Date().toISOString().slice(0,10);

  /* ── Tabs ── */
  document.querySelectorAll('.tab').forEach(function(btn){{
    btn.addEventListener('click', function(){{
      document.querySelectorAll('.tab').forEach(function(b){{ b.classList.remove('active'); }});
      document.querySelectorAll('.panel').forEach(function(p){{ p.classList.remove('active'); }});
      btn.classList.add('active');
      document.getElementById('panel-'+btn.dataset.tab).classList.add('active');
      if(btn.dataset.tab==='live') startLive();
      else stopLive();
    }});
  }});

  /* ── Contract toggle ── */
  document.getElementById('contract-toggle').addEventListener('click', function(){{
    document.getElementById('contract-body').classList.toggle('open');
  }});

  /* ── Search ── */
  var searchEl = document.getElementById('hdr-search');
  var rangeEl  = document.getElementById('hdr-range');
  var cntEl    = document.getElementById('hdr-cnt');
  var btnPrev  = document.getElementById('btn-prev');
  var btnNext  = document.getElementById('btn-next');
  var btnClr   = document.getElementById('btn-clr');
  var all      = Array.from(document.querySelectorAll('#log-body .ln'));
  var matches  = [];
  var matchIdx = -1;

  function clearMarks(){{
    document.querySelectorAll('#log-body mark.hl').forEach(function(m){{
      m.parentNode.replaceChild(document.createTextNode(m.textContent),m);
      m.parentNode.normalize();
    }});
    matches=[]; matchIdx=-1;
  }}

  function applySearch(){{
    clearMarks();
    var q  = searchEl.value.trim().toLowerCase();
    var rv = rangeEl.value;
    var cutoff = null;
    if(rv==='7')  cutoff = new Date(Date.now()-7*86400000).toISOString().slice(0,10);
    if(rv==='30') cutoff = new Date(Date.now()-30*86400000).toISOString().slice(0,10);
    if(rv==='today') cutoff = TODAY;

    all.forEach(function(el){{
      var ts = el.dataset.ts||'';
      if(cutoff && ts.slice(0,10) < cutoff){{ el.classList.add('hidden'); return; }}
      el.classList.remove('hidden');
      if(!q) return;
      if(!(el.dataset.text||'').includes(q)){{ el.classList.add('hidden'); return; }}

      var walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,null,false);
      var nodes=[]; var n;
      while((n=walker.nextNode())) nodes.push(n);
      nodes.forEach(function(tn){{
        var t=tn.textContent, tl=t.toLowerCase(), idx=tl.indexOf(q);
        if(idx===-1) return;
        var frag=document.createDocumentFragment(), last=0;
        while(idx!==-1){{
          frag.appendChild(document.createTextNode(t.slice(last,idx)));
          var m=document.createElement('mark'); m.className='hl';
          m.textContent=t.slice(idx,idx+q.length);
          frag.appendChild(m); matches.push(m);
          last=idx+q.length; idx=tl.indexOf(q,last);
        }}
        frag.appendChild(document.createTextNode(t.slice(last)));
        tn.parentNode.replaceChild(frag,tn);
      }});
    }});

    var vis = all.filter(function(el){{ return !el.classList.contains('hidden'); }}).length;
    if(cntEl) cntEl.textContent = (q?matches.length+' matches / ':'')+vis+' lines shown / {total_commits} commits';
    if(matches.length>0){{ matchIdx=0; navTo(0); }}
  }}

  function navTo(idx){{
    if(!matches.length) return;
    matchIdx=((idx%matches.length)+matches.length)%matches.length;
    matches.forEach(function(m,i){{ m.className=i===matchIdx?'hl cur':'hl'; }});
    matches[matchIdx].scrollIntoView({{behavior:'smooth',block:'center'}});
    /* Switch to history tab if not already there */
    var histBtn=document.querySelector('.tab[data-tab="history"]');
    if(histBtn&&!histBtn.classList.contains('active')) histBtn.click();
  }}

  searchEl.addEventListener('input', applySearch);
  rangeEl.addEventListener('change', applySearch);
  if(btnPrev) btnPrev.addEventListener('click',function(){{ navTo(matchIdx-1); }});
  if(btnNext) btnNext.addEventListener('click',function(){{ navTo(matchIdx+1); }});
  if(btnClr)  btnClr.addEventListener('click',function(){{ searchEl.value=''; applySearch(); }});
  if(cntEl)   cntEl.textContent = '{total_lines:,} lines / {total_commits} commits';

  window._devlogSetQuery=function(q){{ searchEl.value=q; applySearch(); return matches.length; }};

  /* ── Auto-scroll ── */
  var scrolling=false, lastT=null, pauseTmr=null, SPEED=40;
  var scrollEl=document.getElementById('log-body');
  function scrollStep(ts){{
    if(!scrolling||!scrollEl) return;
    if(lastT!==null) scrollEl.parentElement.scrollBy(0,SPEED*(ts-lastT)/1000);
    lastT=ts; requestAnimationFrame(scrollStep);
  }}
  function startScroll(){{
    var btn=document.getElementById('btn-scroll');
    scrolling=true; lastT=null;
    if(btn){{ btn.textContent='Pause'; btn.style.color='#f0883e'; }}
  }}
  function pauseScroll(){{
    var btn=document.getElementById('btn-scroll');
    scrolling=false; lastT=null;
    if(btn){{ btn.textContent='Scroll'; btn.style.color=''; }}
  }}
  var scrBtn=document.getElementById('btn-scroll');
  if(scrBtn) scrBtn.addEventListener('click',function(){{ if(scrolling) pauseScroll(); else startScroll(); requestAnimationFrame(scrollStep); }});
  document.addEventListener('wheel',function(){{
    if(scrolling){{ pauseScroll(); clearTimeout(pauseTmr); pauseTmr=setTimeout(startScroll,5000); }}
  }},{{passive:true}});

  /* ── Live feed ── */
  var liveKnown=new Set(), liveTimer=null, liveFollow=true;
  var liveEl=document.getElementById('live-entries');
  var liveInd=document.getElementById('live-ind');

  function appendLiveEntry(entry){{
    if(!liveEl) return;
    var key=entry.ts+'|'+entry.file;
    if(liveKnown.has(key)) return;
    liveKnown.add(key);
    var labels={{'modified':'SAVE   ','created':'NEW    ','deleted':'DELETE ','renamed':'RENAME ','started':'WATCHER'}};
    var div=document.createElement('div');
    div.className='ln ln-live';
    div.innerHTML='<span class="ts">['+entry.ts+']</span> '+
      '<span class="lbl-live">'+(labels[entry.type]||entry.type.toUpperCase().padEnd(7))+'</span> '+
      '<span class="c-livefile">'+entry.file+'</span>'+
      (entry.from?' <span class="c-meta">(was '+entry.from+')</span>':'');
    liveEl.appendChild(div);
    if(liveFollow) div.scrollIntoView({{behavior:'smooth',block:'end'}});
  }}

  document.addEventListener('wheel',function(e){{ if(e.deltaY<0) liveFollow=false; }},{{passive:true}});

  function pollLive(){{
    fetch(WATCHER_URL+TODAY+'.json?t='+Date.now())
      .then(function(r){{ if(!r.ok) throw new Error(r.status); return r.json(); }})
      .then(function(entries){{
        if(liveInd){{ liveInd.textContent='LIVE'; liveInd.style.color='#3fb950'; liveInd.style.borderColor='#3fb950'; }}
        entries.forEach(appendLiveEntry);
      }})
      .catch(function(){{
        if(liveInd){{ liveInd.textContent='OFFLINE'; liveInd.style.color='#484f58'; liveInd.style.borderColor=''; }}
      }});
  }}

  function startLive(){{
    if(liveTimer) return;
    pollLive();
    liveTimer=setInterval(pollLive,5000);
  }}

  function stopLive(){{
    if(liveTimer){{ clearInterval(liveTimer); liveTimer=null; }}
  }}

  /* ── Calendar ── */
  var selectedDay=null;

  function buildCalendar(dates){{
    var grid=document.getElementById('cal-grid');
    if(!grid) return;
    grid.innerHTML='';

    var dateSet=new Set(dates);
    var todayStr=TODAY;

    var months={{}};
    dates.forEach(function(d){{
      var ym=d.slice(0,7);
      if(!months[ym]) months[ym]=[];
      months[ym].push(d);
    }});

    /* Also show current month even if no entries yet */
    var curYM=TODAY.slice(0,7);
    if(!months[curYM]) months[curYM]=[];

    var DAYS=['Su','Mo','Tu','We','Th','Fr','Sa'];

    Object.keys(months).sort().forEach(function(ym){{
      var parts=ym.split('-');
      var yr=parseInt(parts[0]), mo=parseInt(parts[1])-1;
      var firstDay=new Date(yr,mo,1).getDay();
      var daysInMonth=new Date(yr,mo+1,0).getDate();
      var monthNames=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

      var wrap=document.createElement('div');
      wrap.className='cal-month';

      var h4=document.createElement('h4');
      h4.textContent=monthNames[mo]+' '+yr;
      wrap.appendChild(h4);

      var calDays=document.createElement('div');
      calDays.className='cal-days';
      DAYS.forEach(function(d){{
        var hdr=document.createElement('div');
        hdr.className='cal-day-hdr';
        hdr.textContent=d;
        calDays.appendChild(hdr);
      }});

      for(var i=0;i<firstDay;i++){{
        var blank=document.createElement('div');
        blank.className='cal-day';
        calDays.appendChild(blank);
      }}

      for(var day=1;day<=daysInMonth;day++){{
        var dateStr=ym+'-'+(day<10?'0':'')+day;
        var cell=document.createElement('div');
        cell.className='cal-day'+(dateSet.has(dateStr)?' has-data':'')+(dateStr===todayStr?' today':'');
        cell.textContent=day;
        if(dateSet.has(dateStr)){{
          (function(ds){{
            cell.addEventListener('click',function(){{
              document.querySelectorAll('.cal-day.selected').forEach(function(c){{ c.classList.remove('selected'); }});
              cell.classList.add('selected');
              loadDay(ds);
            }});
          }})(dateStr);
        }}
        calDays.appendChild(cell);
      }}
      wrap.appendChild(calDays);
      grid.appendChild(wrap);
    }});
  }}

  function loadDay(dateStr){{
    var dayLog=document.getElementById('cal-day-log');
    var hdr=document.getElementById('cal-day-log-hdr');
    var body=document.getElementById('cal-day-log-body');
    if(dayLog) dayLog.style.display='block';
    if(hdr) hdr.textContent='Log for '+dateStr+' (loading...)';
    if(body) body.innerHTML='';

    fetch(ARCHIVE_URL+dateStr+'.json?t='+Date.now())
      .then(function(r){{ if(!r.ok) throw new Error(r.status); return r.json(); }})
      .then(function(entries){{
        if(hdr) hdr.textContent='Log for '+dateStr+' \u2014 '+entries.length+' '+(entries.length===1?'entry':'entries');
        if(!body) return;
        if(entries.length===0){{
          body.innerHTML='<div class="ln" style="color:#484f58;padding:0.5rem 1rem;">No entries for this date.</div>';
          return;
        }}
        entries.forEach(function(entry){{
          var div=document.createElement('div');
          if(entry.type==='commit'){{
            /* Git history entry */
            var clsMap={{'key':'c-key','bug':'c-bug','fix':'c-fix','normal':'c-normal'}};
            var lblMap={{'key':'lbl-key','bug':'lbl-bug','fix':'lbl-fix','normal':'lbl-nrm'}};
            var cls=clsMap[entry.cls]||'c-normal';
            var lblCls=lblMap[entry.cls]||'lbl-nrm';
            div.className='ln ln-commit '+cls;
            var stats='';
            if(entry.files) stats+=' <span class="c-stat">'+entry.files+' file'+(entry.files!==1?'s':'')+'</span>';
            if(entry.ins)   stats+=' <span class="d-add">+'+entry.ins+'</span>';
            if(entry.dels)  stats+=' <span class="d-del">-'+entry.dels+'</span>';
            div.innerHTML=
              '<span class="ts">['+entry.ts+']</span> '+
              '<span class="'+lblCls+'">COMMIT </span> '+
              '<span class="c-hash">'+entry.hash+'</span> &mdash; '+
              '<span class="c-msg">'+entry.msg+'</span>'+
              (entry.label?'<br><span style="padding-left:2rem;color:#f0883e;font-size:0.8rem;">*** KEY '+entry.label+'</span>':'')+
              stats;
          }} else {{
            /* Live file-watcher entry */
            var labels={{'modified':'SAVE   ','created':'NEW    ','deleted':'DELETE ','renamed':'RENAME ','started':'WATCHER'}};
            div.className='ln ln-live';
            div.innerHTML=
              '<span class="ts">['+entry.ts+']</span> '+
              '<span class="lbl-live">'+(labels[entry.type]||entry.type.toUpperCase().padEnd(7))+'</span> '+
              '<span class="c-livefile">'+(entry.file||'')+'</span>'+
              (entry.from?' <span class="c-meta">(was '+entry.from+')</span>':'');
          }}
          body.appendChild(div);
        }});
      }})
      .catch(function(){{
        if(hdr) hdr.textContent='Log for '+dateStr+' \u2014 no data';
        if(body) body.innerHTML='<div class="ln" style="color:#484f58;padding:0.5rem 1rem;">No archive data for this date.</div>';
      }});
  }}

  /* Load calendar index from static archive files */
  fetch(ARCHIVE_URL+'index.json?t='+Date.now())
    .then(function(r){{ return r.json(); }})
    .then(function(dates){{ buildCalendar(dates); }})
    .catch(function(){{ buildCalendar([]); }});

  /* Date range filter for calendar */
  var calFrom=document.getElementById('cal-from');
  var calTo=document.getElementById('cal-to');
  var calFilter=document.getElementById('cal-apply');
  if(calFilter) calFilter.addEventListener('click',function(){{
    var from=calFrom?calFrom.value:'';
    var to=calTo?calTo.value:'';
    fetch(ARCHIVE_URL+'index.json?t='+Date.now())
      .then(function(r){{ return r.json(); }})
      .then(function(dates){{
        var filtered=dates.filter(function(d){{
          return (!from||d>=from)&&(!to||d<=to);
        }});
        buildCalendar(filtered);
      }});
  }});

}})();
"""


# ── Session brief (for Claude to read at session start) ──────────────────────

def gen_session_brief(commits):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    recent = commits[-10:]  # last 10 commits

    lines = [
        f"# Claude Session Brief",
        f"Generated: {now}",
        f"Read this at session start. It tells you exactly where the project is.",
        f"",
        f"## Project",
        f"H.C. Lombardo NFL Analytics App",
        f"Student/PM: April V. Sykes — Senior Capstone, Olympic College, Spring 2026",
        f"Advisor: Richard Becker",
        f"",
        f"## Architecture",
        f"Frontend : React (port 3000) -> AWS Amplify (auto-deploy from GitHub)",
        f"Backend  : Flask (port 5000) -> EC2 (auto-pull from GitHub)",
        f"Database : PostgreSQL on EC2 localhost, schema=hcl, ~7,263 games (1999-2025)",
        f"Dashboard: Dashboard/index.html -> gh-pages branch only",
        f"",
        f"## Critical Rules (full contract: docs/ai_reference/AI_EXECUTION_CONTRACT.md)",
        f"1. Test locally first. Show April. Get approval. Then commit.",
        f"2. No localStorage. Ever. All data hardcoded.",
        f"3. No assumptions. Ask if unclear.",
        f"4. Clean up old code. No dead code left behind.",
        f"5. Deploy: git push origin master && git push origin gh-pages",
        f"",
        f"## Last 10 Commits",
    ]

    for c in reversed(recent):
        stat_sum = next((s.strip() for s in c['stat'] if ' changed,' in s), '')
        lines.append(f"  {c['date']}  {c['short']}  {c['msg']}")
        if stat_sum:
            lines.append(f"    {stat_sum}")

    lines += [
        f"",
        f"## Last 3 Commits — Full Diff",
    ]

    for c in commits[-3:]:
        lines.append(f"\n### {c['short']} — {c['msg']}")
        lines.append(f"Date: {c['date']}")
        for s in c['stat']:
            if s.strip():
                lines.append(f"  {s.rstrip()}")
        lines.append("")
        shown = 0
        for dl in c['diff']:
            if shown >= 150:
                lines.append("  ... [truncated]")
                break
            lines.append(dl)
            shown += 1

    lines += [
        f"",
        f"## Open Known Issues (as of last commit)",
        f"  TA-063 : EC2 disk at 88% — CRITICAL, clean up before it fills",
        f"  TA-057 : train_xgb_winner.py line 255 hardcodes schema hcl_test instead of hcl",
        f"  TA-058 : train_xgb_spread.py broken WINDOW clause lines 95-116",
        f"  TA-059 : hardcoded season=2025 in 7+ API endpoints",
        f"  TA-008 : live Amplify URL blocked — AWS MFA locked",
        f"",
        f"## Key Files",
        f"  api_server.py            — main Flask app",
        f"  api_routes_hcl.py        — historical data endpoints",
        f"  api_routes_ml.py         — ML prediction endpoints",
        f"  frontend/src/App.js      — main React router",
        f"  Dashboard/index.html     — PM dashboard (gh-pages only)",
        f"  ml/                      — XGBoost models (60.7% accuracy)",
        f"  docs/devlog/index.html   — Project Logbook (this system)",
        f"",
        f"## Where To Look",
        f"  Git history  : docs/ai_reference/DEV_LOG_FULL.txt (24MB, all diffs)",
        f"  Daily logs   : docs/devlog/archive/YYYY-MM-DD.json",
        f"  Logbook page : docs/devlog/index.html (open in browser)",
        f"  Memory files : C:/Users/april/.claude/projects/.../memory/",
    ]

    return '\n'.join(lines)


# ── Build ─────────────────────────────────────────────────────────────────────

print("Parsing git log...")
commits = parse_log()
print(f"  {len(commits)} commits parsed")

key_count = sum(1 for c in commits if c['short'] in KEY_COMMITS)
bug_count = sum(1 for c in commits if classify(c) == 'bug')
fix_count = sum(1 for c in commits if classify(c) == 'fix')
d_first   = commits[0]['date'][:10]  if commits else '?'
d_last    = commits[-1]['date'][:10] if commits else '?'

print("Building log lines...")
log_lines = build_log_lines(commits)
log_html  = '\n'.join(log_lines)
print(f"  {len(log_lines):,} lines generated")

JS = make_js(len(commits), len(log_lines))

# ── Logbook page HTML ─────────────────────────────────────────────────────────

logbook = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project Logbook — H.C. Lombardo NFL Analytics</title>
<style>{CSS}</style>
</head>
<body>

<div id="hdr">
  <span id="hdr-title">PROJECT LOGBOOK</span>
  <span id="hdr-meta">H.C. Lombardo NFL Analytics &nbsp;·&nbsp; April V. Sykes &nbsp;·&nbsp; Spring 2026</span>
  <input id="hdr-search" type="text" placeholder="Search all logs — commits, files, code, errors, dates..." autocomplete="off" spellcheck="false">
  <select id="hdr-range">
    <option value="all">All time</option>
    <option value="today">Today</option>
    <option value="7">Last 7 days</option>
    <option value="30">Last 30 days</option>
  </select>
  <button id="btn-prev" style="background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.55rem;font-size:0.76rem;cursor:pointer;">&#8593;</button>
  <button id="btn-next" style="background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.55rem;font-size:0.76rem;cursor:pointer;">&#8595;</button>
  <button id="btn-clr"  style="background:transparent;color:#8b949e;border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.55rem;font-size:0.76rem;cursor:pointer;">&#10005;</button>
  <button id="btn-scroll" style="background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.55rem;font-size:0.76rem;cursor:pointer;">Scroll</button>
  <span id="live-ind">OFFLINE</span>
  <span id="hdr-cnt"></span>
</div>

<div id="contract">
  <div id="contract-toggle">&#9888; AI EXECUTION CONTRACT &nbsp;&nbsp;[click to expand]</div>
  <div id="contract-body">{html.escape(CONTRACT_TEXT)}</div>
</div>

<div id="tabs">
  <button class="tab active" data-tab="live">&#9889; Live Feed</button>
  <button class="tab" data-tab="calendar">&#128197; Calendar</button>
  <button class="tab" data-tab="history">&#128220; Git History</button>
</div>

<!-- LIVE TAB -->
<div id="panel-live" class="panel active">
  <div style="padding:0.5rem 1rem;border-bottom:1px solid #30363d;color:#58a6ff;font-size:0.74rem;">
    Real-time file activity &mdash; requires log_watcher.py running (start via START-DEV.bat)
  </div>
  <div id="live-entries" style="padding-bottom:3rem;"></div>
</div>

<!-- CALENDAR TAB -->
<div id="panel-calendar" class="panel">
  <div id="cal-wrap">
    <div id="cal-range-bar">
      <label>From:</label>
      <input type="date" id="cal-from" value="{d_first}">
      <label>To:</label>
      <input type="date" id="cal-to" value="{d_last}">
      <button id="cal-apply">Filter</button>
      <span style="color:#484f58;font-size:0.72rem;">Click any highlighted date to view that day's activity log</span>
    </div>
    <div id="cal-grid"></div>
    <div id="cal-day-log" style="display:none;">
      <div id="cal-day-log-hdr"></div>
      <div id="cal-day-log-body"></div>
    </div>
  </div>
</div>

<!-- GIT HISTORY TAB -->
<div id="panel-history" class="panel">
  <div style="padding:0.4rem 1rem;border-bottom:1px solid #30363d;color:#8b949e;font-size:0.72rem;">
    {len(commits)} commits &nbsp;·&nbsp; {d_first} &mdash; {d_last} &nbsp;·&nbsp;
    <span style="color:#f0883e;">*** {key_count} key</span> &nbsp;·&nbsp;
    <span style="color:#f85149;">BUG {bug_count}</span> &nbsp;·&nbsp;
    <span style="color:#3fb950;">FIX {fix_count}</span> &nbsp;·&nbsp;
    {len(log_lines):,} log lines
    &nbsp;|&nbsp;
    GREEN=additions &nbsp; RED=deletions &nbsp; BLUE=line numbers &nbsp; ORANGE=key milestones
  </div>
  <div id="log-body">
{log_html}
  </div>
</div>

<div id="statusbar">
  <span>PROJECT LOGBOOK &mdash; H.C. Lombardo NFL Analytics &mdash; AprilV &mdash; Spring 2026</span>
  <span><a href="../../Dashboard/index.html" style="color:#58a6ff;">&#8592; Dashboard</a></span>
</div>

<script>{JS}</script>
</body>
</html>"""

os.makedirs(os.path.dirname(LOGBOOK_OUT), exist_ok=True)
with open(LOGBOOK_OUT, 'w', encoding='utf-8') as f:
    f.write(logbook)
sz = os.path.getsize(LOGBOOK_OUT)
print(f"\nLogbook : {sz:,} bytes ({sz//1024} KB)")
print(f"  -> {LOGBOOK_OUT}")

# ── Session brief ─────────────────────────────────────────────────────────────

brief = gen_session_brief(commits)
with open(BRIEF_OUT, 'w', encoding='utf-8') as f:
    f.write(brief)
sz2 = os.path.getsize(BRIEF_OUT)
print(f"Brief   : {sz2:,} bytes")
print(f"  -> {BRIEF_OUT}")

# ── Dashboard fragment ────────────────────────────────────────────────────────

frag_ctrl = f"""
<div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;
  background:#0d1117;border:1px solid #30363d;border-radius:4px;
  padding:0.5rem 0.75rem;margin-bottom:0.5rem;
  font-family:'Courier New',monospace;">
  <span style="color:#f0883e;font-weight:700;font-size:0.76rem;">LOGBOOK</span>
  <input id="q" type="text" placeholder="Search commits, files, code, errors..."
    style="flex:1;min-width:180px;background:#161b22;color:#c9d1d9;border:1px solid #30363d;
    border-radius:3px;padding:0.3rem 0.55rem;font-size:0.76rem;font-family:inherit;outline:none;"
    autocomplete="off" spellcheck="false">
  <button id="btn-prev" style="background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.5rem;font-size:0.76rem;cursor:pointer;">&#8593;</button>
  <button id="btn-next" style="background:#161b22;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.5rem;font-size:0.76rem;cursor:pointer;">&#8595;</button>
  <button id="btn-clr"  style="background:transparent;color:#8b949e;border:1px solid #30363d;border-radius:3px;padding:0.3rem 0.5rem;font-size:0.76rem;cursor:pointer;">&#10005;</button>
  <a href="docs/devlog/index.html" target="_blank"
    style="background:#161b22;color:#58a6ff;border:1px solid #30363d;border-radius:3px;
    padding:0.3rem 0.55rem;font-size:0.76rem;text-decoration:none;white-space:nowrap;">
    &#8599; Open Logbook</a>
  <span id="cnt" style="color:#8b949e;font-size:0.7rem;margin-left:auto;white-space:nowrap;"></span>
</div>
"""

# Fragment JS (simplified — no tabs, no calendar, just search + scroll)
frag_js = f"""
(function(){{
  var qEl=document.getElementById('q');
  var cntEl=document.getElementById('cnt');
  var all=Array.from(document.querySelectorAll('#frag-log .ln'));
  var matches=[],matchIdx=-1;
  function clearMarks(){{
    document.querySelectorAll('#frag-log mark.hl').forEach(function(m){{
      m.parentNode.replaceChild(document.createTextNode(m.textContent),m);
      m.parentNode.normalize();
    }});
    matches=[]; matchIdx=-1;
  }}
  function doSearch(){{
    clearMarks();
    var q=qEl?qEl.value.trim().toLowerCase():'';
    all.forEach(function(el){{
      if(!q){{ el.classList.remove('hidden'); return; }}
      if(!(el.dataset.text||'').includes(q)){{ el.classList.add('hidden'); return; }}
      el.classList.remove('hidden');
      var walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,null,false);
      var nodes=[]; var n;
      while((n=walker.nextNode())) nodes.push(n);
      nodes.forEach(function(tn){{
        var t=tn.textContent,tl=t.toLowerCase(),idx=tl.indexOf(q);
        if(idx===-1) return;
        var frag=document.createDocumentFragment(),last=0;
        while(idx!==-1){{
          frag.appendChild(document.createTextNode(t.slice(last,idx)));
          var m=document.createElement('mark'); m.className='hl';
          m.textContent=t.slice(idx,idx+q.length);
          frag.appendChild(m); matches.push(m);
          last=idx+q.length; idx=tl.indexOf(q,last);
        }}
        frag.appendChild(document.createTextNode(t.slice(last)));
        tn.parentNode.replaceChild(frag,tn);
      }});
    }});
    if(cntEl) cntEl.textContent=(q?matches.length+' matches / ':'')+'{len(commits)} commits';
    if(matches.length>0){{ matchIdx=0; navTo(0); }}
    return matches.length;
  }}
  function navTo(idx){{
    if(!matches.length) return;
    matchIdx=((idx%matches.length)+matches.length)%matches.length;
    matches.forEach(function(m,i){{ m.className=i===matchIdx?'hl cur':'hl'; }});
    matches[matchIdx].scrollIntoView({{behavior:'smooth',block:'center'}});
  }}
  if(qEl) qEl.addEventListener('input',doSearch);
  document.getElementById('btn-prev').addEventListener('click',function(){{ navTo(matchIdx-1); }});
  document.getElementById('btn-next').addEventListener('click',function(){{ navTo(matchIdx+1); }});
  document.getElementById('btn-clr').addEventListener('click',function(){{ if(qEl) qEl.value=''; doSearch(); }});
  if(cntEl) cntEl.textContent='{len(commits)} commits / {len(log_lines):,} lines';
  window._devlogSetQuery=function(q){{ if(qEl) qEl.value=q; return doSearch(); }};
}})();
"""

fragment = (
    f'<style>{CSS}#hdr{{display:none}}#tabs{{display:none}}#statusbar{{display:none}}'
    f'#contract{{margin-top:0}}</style>\n'
    + frag_ctrl
    + f'<div id="frag-log" style="max-height:65vh;overflow-y:auto;'
      f'border:1px solid #30363d;border-radius:4px;">\n'
    + f'<div style="padding:0.3rem 1rem;border-bottom:1px solid #30363d;'
      f'color:#8b949e;font-size:0.7rem;">'
      f'{len(commits)} commits &nbsp;·&nbsp; {d_first} &mdash; {d_last} &nbsp;·&nbsp; '
      f'{len(log_lines):,} lines</div>\n'
    + log_html + '\n'
    + '</div>\n'
    + f'<script>{frag_js}</script>\n'
)

with open(FRAGMENT_OUT, 'w', encoding='utf-8') as f:
    f.write(fragment)
sz3 = os.path.getsize(FRAGMENT_OUT)
print(f"Fragment: {sz3:,} bytes")
print(f"  -> {FRAGMENT_OUT}")

# ── Write per-date archive JSON from git history ──────────────────────────────
print("\nWriting date archives...")
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

from collections import defaultdict
by_date = defaultdict(list)
for c in commits:
    day = c['date'][:10]
    # Parse stat lines to count files/insertions/deletions
    files_changed = 0
    insertions = 0
    deletions = 0
    for sl in c.get('stat', []):
        m = re.search(r'(\d+) file', sl)
        if m:
            files_changed = int(m.group(1))
        m2 = re.search(r'(\d+) insertion', sl)
        if m2:
            insertions = int(m2.group(1))
        m3 = re.search(r'(\d+) deletion', sl)
        if m3:
            deletions = int(m3.group(1))
    cls = classify(c)
    entry = {
        'ts':    c['date'],
        'type':  'commit',
        'hash':  c['short'],
        'msg':   c['msg'],
        'cls':   cls,
        'label': KEY_COMMITS.get(c['short'], ''),
        'files': files_changed,
        'ins':   insertions,
        'dels':  deletions,
    }
    by_date[day].append(entry)

dates_written = []
for day, entries in sorted(by_date.items()):
    path = ARCHIVE_DIR / f"{day}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False)
    dates_written.append(day)

# Merge with any existing live-watcher dates in index.json
index_path = ARCHIVE_DIR / 'index.json'
existing = []
if index_path.exists():
    try:
        existing = json.loads(index_path.read_text(encoding='utf-8'))
    except Exception:
        existing = []
all_dates = sorted(set(dates_written) | set(existing))
index_path.write_text(json.dumps(all_dates, ensure_ascii=False), encoding='utf-8')
print(f"  {len(dates_written)} date archives written ({dates_written[0]} to {dates_written[-1]})")
print(f"  index.json: {len(all_dates)} total dates")
print(f"  -> {ARCHIVE_DIR}/")

print(f"\nDone. {len(commits)} commits / {key_count} key / {bug_count} bugs / {fix_count} fixes / {len(log_lines):,} lines")
