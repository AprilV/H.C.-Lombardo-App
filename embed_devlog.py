"""
Replace the Project Logbook tab in Dashboard/index.html.

Extracts ONLY the .ln div lines from devlog_output.html (not the full
standalone page), adds scoped CSS, and builds a clean split-screen layout:
  LEFT  (flex:1)  — scrollable log lines with sticky mini-header
  RIGHT (300px)   — search, filters, stats, scroll buttons, open link
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

# ── Extract only the .ln div lines (each is a single line in the output) ──
ln_lines = re.findall(r'<div class="ln[^>]*>.*?</div>', devlog_raw)
ln_count = len(ln_lines)
log_fragment = '\n'.join(ln_lines)

# Stats for the right-panel table
commit_count  = sum(1 for l in ln_lines if 'ln-commit' in l)
key_count     = sum(1 for l in ln_lines if 'c-key' in l or 'ln-keylabel' in l)
bug_count     = sum(1 for l in ln_lines if ' c-bug' in l)
fix_count     = sum(1 for l in ln_lines if ' c-fix' in l)
today_str     = date.today().strftime('%b %d, %Y')

# ── Find start/end markers in dashboard ──
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

new_section = f"""<div id="tab-ailog" class="tab-panel">

<style>
/* ── Scoped logbook CSS — no position:fixed, no html/body resets ── */
#frag-log-wrap {{
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.84rem;
  line-height: 1.6;
  color: #c9d1d9;
}}
#frag-log-wrap .ln {{padding:0.05rem 1rem;white-space:pre-wrap;word-break:break-all}}
#frag-log-wrap .ln:hover {{background:#161b22}}
#frag-log-wrap .ln-sep {{height:3px;background:#161b22;margin:1px 0}}
#frag-log-wrap .ln-commit {{border-left:3px solid #30363d}}
#frag-log-wrap .c-key .ln-commit,#frag-log-wrap .ln-keylabel {{border-left-color:#f0883e!important}}
#frag-log-wrap .c-bug {{border-left-color:#f85149!important}}
#frag-log-wrap .c-fix {{border-left-color:#3fb950!important}}
#frag-log-wrap .ln-add {{background:rgba(63,185,80,0.04)}}
#frag-log-wrap .ln-del {{background:rgba(248,81,73,0.04)}}
#frag-log-wrap .ln-live {{border-left:3px solid #58a6ff;background:rgba(88,166,255,0.04)}}
#frag-log-wrap .hidden {{display:none!important}}
#frag-log-wrap .ts {{color:#484f58;user-select:none}}
#frag-log-wrap .lbl-key {{color:#f0883e;font-weight:700}}
#frag-log-wrap .lbl-bug {{color:#f85149;font-weight:700}}
#frag-log-wrap .lbl-fix {{color:#3fb950;font-weight:700}}
#frag-log-wrap .lbl-nrm {{color:#6e7681}}
#frag-log-wrap .lbl-stat {{color:#79c0ff}}
#frag-log-wrap .lbl-file {{color:#d29922}}
#frag-log-wrap .lbl-add {{color:#3fb950}}
#frag-log-wrap .lbl-del {{color:#f85149}}
#frag-log-wrap .lbl-meta,#frag-log-wrap .c-meta {{color:#484f58}}
#frag-log-wrap .lbl-live {{color:#58a6ff;font-weight:700}}
#frag-log-wrap .c-hash {{color:#3fb950;font-weight:700}}
#frag-log-wrap .c-msg {{color:#e6edf3}}
#frag-log-wrap .c-keylabel {{color:#f0883e;font-weight:700}}
#frag-log-wrap .c-stat {{color:#79c0ff}}
#frag-log-wrap .c-fname,#frag-log-wrap .c-livefile {{color:#e6edf3}}
#frag-log-wrap .c-difffile {{color:#d29922;font-weight:700}}
#frag-log-wrap .c-hunk {{color:#79c0ff}}
#frag-log-wrap .d-add {{color:#3fb950}}
#frag-log-wrap .d-del {{color:#f85149}}
#frag-log-wrap mark.hl {{background:#f0883e;color:#000;border-radius:1px}}
#frag-log-wrap mark.hl.cur {{background:#ffd700}}
</style>

<div style="display:flex;height:calc(100vh - 120px);overflow:hidden;gap:0;">

  <!-- ── LEFT: Log lines (clean embed — no sub-tabs, no position:fixed) ── -->
  <div id="frag-log-wrap" style="flex:1 1 0;overflow-y:auto;overflow-x:hidden;background:#0d1117;">

    <!-- Sticky mini-header inside the scroll container -->
    <div style="position:sticky;top:0;z-index:10;background:#0d1117;
                border-bottom:2px solid #f0883e;padding:0.4rem 1rem;
                display:flex;align-items:center;gap:1rem;">
      <span style="color:#f0883e;font-weight:700;font-size:0.82rem;white-space:nowrap;">PROJECT LOGBOOK</span>
      <span style="color:#484f58;font-size:0.7rem;white-space:nowrap;">{commit_count} commits &middot; {ln_count:,} lines</span>
      <span style="color:#484f58;font-size:0.7rem;margin-left:auto;white-space:nowrap;">Oct 2025 &ndash; {today_str}</span>
    </div>

    <!-- Log lines -->
    <div id="frag-log-body" style="padding-bottom:2rem;">
{log_fragment}
    </div>
  </div>

  <!-- ── RIGHT: Controls panel ── -->
  <div style="flex:0 0 300px;min-width:220px;background:#161b22;
              border-left:1px solid #30363d;display:flex;flex-direction:column;overflow:hidden;">

    <!-- Search (top of right panel) -->
    <div style="padding:0.75rem;border-bottom:1px solid #30363d;">
      <div style="font-size:0.68rem;font-weight:700;color:#f0883e;
                  letter-spacing:0.08em;margin-bottom:0.4rem;">SEARCH LOG</div>
      <input id="frag-q" type="text" placeholder="commits, files, errors..."
        style="width:100%;box-sizing:border-box;background:#0d1117;color:#c9d1d9;
               border:1px solid #30363d;border-radius:3px;padding:0.35rem 0.6rem;
               font-size:0.76rem;font-family:'Courier New',monospace;outline:none;"
        autocomplete="off" spellcheck="false">
      <div style="display:flex;gap:0.3rem;margin-top:0.35rem;align-items:center;">
        <button id="frag-prev" title="Previous match"
          style="background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
                 border-radius:3px;padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#8593;</button>
        <button id="frag-next" title="Next match"
          style="background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
                 border-radius:3px;padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#8595;</button>
        <button id="frag-clr" title="Clear"
          style="background:transparent;color:#8b949e;border:1px solid #30363d;
                 border-radius:3px;padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#10005;</button>
        <span id="frag-cnt"
          style="color:#8b949e;font-size:0.68rem;margin-left:auto;">{ln_count:,} lines</span>
      </div>
    </div>

    <!-- Filter buttons -->
    <div style="padding:0.6rem 0.75rem;border-bottom:1px solid #30363d;">
      <div style="font-size:0.68rem;color:#8b949e;margin-bottom:0.35rem;
                  letter-spacing:0.06em;">FILTER BY TYPE</div>
      <div style="display:flex;flex-wrap:wrap;gap:0.3rem;">
        <button onclick="fragFilter('')"       class="ff-btn" data-f=""
          style="background:#1f6feb;color:#fff;border:1px solid #1f6feb;
                 border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">All</button>
        <button onclick="fragFilter('key')"    class="ff-btn" data-f="key"
          style="background:#0d1117;color:#ffd700;border:1px solid #30363d;
                 border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">&#9733; Key</button>
        <button onclick="fragFilter('bug')"    class="ff-btn" data-f="bug"
          style="background:#0d1117;color:#f85149;border:1px solid #30363d;
                 border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Bug</button>
        <button onclick="fragFilter('fix')"    class="ff-btn" data-f="fix"
          style="background:#0d1117;color:#3fb950;border:1px solid #30363d;
                 border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Fix</button>
        <button onclick="fragFilter('commit')" class="ff-btn" data-f="commit"
          style="background:#0d1117;color:#79c0ff;border:1px solid #30363d;
                 border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Commits</button>
        <button onclick="fragFilter('file')"   class="ff-btn" data-f="file"
          style="background:#0d1117;color:#d29922;border:1px solid #30363d;
                 border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Files</button>
      </div>
    </div>

    <!-- Repository stats -->
    <div style="padding:0.6rem 0.75rem;border-bottom:1px solid #30363d;">
      <div style="font-size:0.68rem;color:#8b949e;margin-bottom:0.4rem;
                  letter-spacing:0.06em;">REPOSITORY STATS</div>
      <table style="width:100%;font-size:0.74rem;border-collapse:collapse;">
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Total commits</td>
            <td style="color:#c9d1d9;text-align:right;">{commit_count}</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Key milestones</td>
            <td style="color:#ffd700;text-align:right;">{key_count}</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Bugs logged</td>
            <td style="color:#f85149;text-align:right;">{bug_count}</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Fixes applied</td>
            <td style="color:#3fb950;text-align:right;">{fix_count}</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Log lines</td>
            <td style="color:#c9d1d9;text-align:right;">{ln_count:,}</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Period</td>
            <td style="color:#c9d1d9;text-align:right;">Oct 2025&ndash;now</td></tr>
      </table>
    </div>

    <!-- Scroll controls -->
    <div style="padding:0.6rem 0.75rem;border-bottom:1px solid #30363d;display:flex;gap:0.4rem;">
      <button onclick="document.getElementById('frag-log-wrap').scrollTop=0"
        style="flex:1;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
               border-radius:3px;padding:0.3rem;font-size:0.72rem;cursor:pointer;">&#8679; Top</button>
      <button onclick="(function(){{var w=document.getElementById('frag-log-wrap');w.scrollTop=w.scrollHeight;}})()"
        style="flex:1;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
               border-radius:3px;padding:0.3rem;font-size:0.72rem;cursor:pointer;">&#8681; Latest</button>
    </div>

    <!-- Open full logbook -->
    <div style="padding:0.75rem;">
      <a href="docs/devlog/index.html" target="_blank"
        style="display:block;text-align:center;background:#1f6feb;color:#fff;
               border-radius:3px;padding:0.45rem;font-size:0.76rem;
               font-family:'Courier New',monospace;text-decoration:none;font-weight:700;">
        &#8599; Open Full Logbook</a>
      <div style="color:#8b949e;font-size:0.66rem;text-align:center;margin-top:0.35rem;">
        Live Feed + Calendar in full view
      </div>
    </div>

    <div style="flex:1;"></div>

    <div style="padding:0.5rem 0.75rem;border-top:1px solid #30363d;
                font-size:0.65rem;color:#484f58;text-align:center;">
      Auto-generated {today_str} &middot; pre-commit hook
    </div>
  </div>

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
      var typeOk = !activeFilter || el.classList.contains('ln-' + activeFilter);
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
      if (q) cntEl.textContent = matches.length ? (matchIdx+1)+'/'+matches.length : '0 results';
      else   cntEl.textContent = visible.length.toLocaleString() + ' lines';
    }}
  }}

  function scrollToMatch() {{
    if (!matches.length) return;
    matches[matchIdx].scrollIntoView({{block:'center'}});
    if (cntEl) cntEl.textContent = (matchIdx+1)+'/'+matches.length;
  }}

  if (qEl) {{
    qEl.addEventListener('input', applyFilter);
    qEl.addEventListener('keydown', function(e) {{
      if (e.key === 'Enter') {{
        matchIdx = (matchIdx + 1) % (matches.length || 1);
        scrollToMatch();
      }}
    }});
  }}

  var prev = document.getElementById('frag-prev');
  var next = document.getElementById('frag-next');
  var clr  = document.getElementById('frag-clr');
  if (prev) prev.addEventListener('click', function() {{
    if (!matches.length) return;
    matchIdx = (matchIdx - 1 + matches.length) % matches.length;
    scrollToMatch();
  }});
  if (next) next.addEventListener('click', function() {{
    if (!matches.length) return;
    matchIdx = (matchIdx + 1) % matches.length;
    scrollToMatch();
  }});
  if (clr) clr.addEventListener('click', function() {{
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
      var active = b.dataset.f === f;
      b.style.background  = active ? '#1f6feb' : '#0d1117';
      b.style.borderColor = active ? '#1f6feb' : '#30363d';
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
