"""
Replace the entire Project Logbook tab in Dashboard/index.html with the
generated terminal dev log, using a split-screen layout.

Start marker : <div id="tab-ailog"   (replaces entire tab content)
End marker   : </div><!-- /tab-ailog -->
"""
import os
import sys

DASHBOARD = "c:/ReactGitEC2/IS330/H.C Lombardo App/Dashboard/index.html"
DEVLOG    = "c:/ReactGitEC2/IS330/H.C Lombardo App/devlog_output.html"

with open(DASHBOARD, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(DEVLOG, 'r', encoding='utf-8') as f:
    devlog_content = f.read()

# Find start (the opening <div id="tab-ailog") and end markers
start_line = None
end_line   = None
for i, line in enumerate(lines):
    if start_line is None and '<div id="tab-ailog"' in line:
        start_line = i
    if '</div><!-- /tab-ailog -->' in line:
        end_line = i
        break

if start_line is None or end_line is None:
    print(f"ERROR: Could not find markers. start={start_line} end={end_line}")
    sys.exit(1)

print(f"Replacing lines {start_line+1} to {end_line+1} ({end_line - start_line + 1} lines)")

today_str = "Apr 19, 2026"

new_section = f"""<div id="tab-ailog" class="tab-panel">
<div style="display:flex;height:calc(100vh - 120px);overflow:hidden;gap:0;font-family:'Courier New',monospace;">

  <!-- LEFT: Log lines -->
  <div id="frag-log-wrap" style="flex:1 1 65%;overflow-y:auto;overflow-x:auto;background:#0d1117;padding:0.75rem 0.5rem;">
    <!-- ─── SECTION 13: COMPLETE DEVELOPER LOG (AUTO-GENERATED FROM GIT) ─── -->
{devlog_content}
  </div>

  <!-- RIGHT: Controls panel -->
  <div style="flex:0 0 310px;min-width:240px;background:#161b22;border-left:1px solid #30363d;
       display:flex;flex-direction:column;overflow:hidden;">

    <!-- Search at top -->
    <div style="padding:0.75rem;border-bottom:1px solid #30363d;">
      <div style="font-size:0.7rem;font-weight:700;color:#f0883e;letter-spacing:0.08em;margin-bottom:0.4rem;">PROJECT LOGBOOK</div>
      <input id="frag-q" type="text" placeholder="Search commits, files, errors..."
        style="width:100%;box-sizing:border-box;background:#0d1117;color:#c9d1d9;
               border:1px solid #30363d;border-radius:3px;padding:0.35rem 0.6rem;
               font-size:0.76rem;font-family:'Courier New',monospace;outline:none;"
        autocomplete="off" spellcheck="false">
      <div style="display:flex;gap:0.3rem;margin-top:0.35rem;align-items:center;">
        <button id="frag-prev" title="Previous match"
          style="background:#0d1117;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;
                 padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#8593;</button>
        <button id="frag-next" title="Next match"
          style="background:#0d1117;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;
                 padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#8595;</button>
        <button id="frag-clr" title="Clear search"
          style="background:transparent;color:#8b949e;border:1px solid #30363d;border-radius:3px;
                 padding:0.25rem 0.5rem;font-size:0.72rem;cursor:pointer;">&#10005;</button>
        <span id="frag-cnt" style="color:#8b949e;font-size:0.68rem;margin-left:auto;"></span>
      </div>
    </div>

    <!-- Filter buttons -->
    <div style="padding:0.6rem 0.75rem;border-bottom:1px solid #30363d;">
      <div style="font-size:0.68rem;color:#8b949e;margin-bottom:0.35rem;letter-spacing:0.06em;">FILTER BY TYPE</div>
      <div style="display:flex;flex-wrap:wrap;gap:0.3rem;">
        <button onclick="fragFilter('')"    class="ff-btn" data-f=""    style="background:#1f6feb;color:#fff;border:1px solid #1f6feb;border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">All</button>
        <button onclick="fragFilter('key')" class="ff-btn" data-f="key" style="background:#0d1117;color:#ffd700;border:1px solid #30363d;border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">&#9733; Key</button>
        <button onclick="fragFilter('bug')" class="ff-btn" data-f="bug" style="background:#0d1117;color:#f85149;border:1px solid #30363d;border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Bug</button>
        <button onclick="fragFilter('fix')" class="ff-btn" data-f="fix" style="background:#0d1117;color:#3fb950;border:1px solid #30363d;border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Fix</button>
        <button onclick="fragFilter('add')" class="ff-btn" data-f="add" style="background:#0d1117;color:#3fb950;border:1px solid #30363d;border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Add</button>
        <button onclick="fragFilter('del')" class="ff-btn" data-f="del" style="background:#0d1117;color:#f85149;border:1px solid #30363d;border-radius:3px;padding:0.22rem 0.5rem;font-size:0.7rem;cursor:pointer;">Del</button>
      </div>
    </div>

    <!-- Stats -->
    <div style="padding:0.6rem 0.75rem;border-bottom:1px solid #30363d;">
      <div style="font-size:0.68rem;color:#8b949e;margin-bottom:0.4rem;letter-spacing:0.06em;">REPOSITORY STATS</div>
      <table style="width:100%;font-size:0.74rem;border-collapse:collapse;">
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Total commits</td><td style="color:#c9d1d9;text-align:right;">372</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Key milestones</td><td style="color:#ffd700;text-align:right;">48</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Bugs logged</td><td style="color:#f85149;text-align:right;">21</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Fixes applied</td><td style="color:#3fb950;text-align:right;">105</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Log lines</td><td style="color:#c9d1d9;text-align:right;">17,121</td></tr>
        <tr><td style="color:#8b949e;padding:0.1rem 0;">Period</td><td style="color:#c9d1d9;text-align:right;">Oct 7 – {today_str}</td></tr>
      </table>
    </div>

    <!-- Scroll controls -->
    <div style="padding:0.6rem 0.75rem;border-bottom:1px solid #30363d;display:flex;gap:0.4rem;">
      <button onclick="document.getElementById('frag-log-wrap').scrollTop=0"
        style="flex:1;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;
               padding:0.3rem;font-size:0.72rem;cursor:pointer;">&#8679; Top</button>
      <button onclick="var w=document.getElementById('frag-log-wrap');w.scrollTop=w.scrollHeight"
        style="flex:1;background:#0d1117;color:#c9d1d9;border:1px solid #30363d;border-radius:3px;
               padding:0.3rem;font-size:0.72rem;cursor:pointer;">&#8681; Bottom</button>
    </div>

    <!-- Open full logbook link -->
    <div style="padding:0.75rem;">
      <a href="docs/devlog/index.html" target="_blank"
        style="display:block;text-align:center;background:#1f6feb;color:#fff;border-radius:3px;
               padding:0.45rem;font-size:0.76rem;font-family:'Courier New',monospace;
               text-decoration:none;font-weight:700;">
        &#8599; Open Full Logbook</a>
      <div style="color:#8b949e;font-size:0.66rem;text-align:center;margin-top:0.35rem;">
        Includes Live Feed + Calendar archive
      </div>
    </div>

    <!-- Scroll to bottom filler -->
    <div style="flex:1;"></div>

    <!-- Footer -->
    <div style="padding:0.5rem 0.75rem;border-top:1px solid #30363d;font-size:0.65rem;color:#484f58;text-align:center;">
      Auto-generated {today_str} · pre-commit hook
    </div>
  </div>

</div>

<script>
(function(){{
  var wrap  = document.getElementById('frag-log-wrap');
  var qEl   = document.getElementById('frag-q');
  var cntEl = document.getElementById('frag-cnt');
  var all   = Array.from(document.querySelectorAll('#frag-log-wrap .ln'));
  var activeFilter = '';
  var matches = [], matchIdx = -1;

  function clearMarks() {{
    document.querySelectorAll('#frag-log-wrap mark.hl').forEach(function(m) {{
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
      var typeOk = !activeFilter || (el.classList.contains('ln-' + activeFilter));
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
            mark.style.cssText = 'background:#ffd700;color:#000;border-radius:2px;';
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
      matches = Array.from(document.querySelectorAll('#frag-log-wrap mark.hl'));
      matchIdx = 0;
      scrollToMatch();
    }}
    if (cntEl) {{
      if (q) cntEl.textContent = matches.length ? (matchIdx+1)+'/'+matches.length : '0 results';
      else cntEl.textContent = visible.length + ' lines';
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
      b.style.background = b.dataset.f === '' ? '#1f6feb' : '#0d1117';
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

  // Initial count
  if (cntEl) cntEl.textContent = all.length + ' lines';
}})();
</script>

</div><!-- /tab-ailog -->
"""

new_lines = lines[:start_line] + [new_section]
new_lines += lines[end_line+1:]

with open(DASHBOARD, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

size = os.path.getsize(DASHBOARD)
print(f"Done. Dashboard is now {size:,} bytes ({size//1024} KB)")
