"""
Replace §13 section in Dashboard/index.html with the generated terminal dev log.
Replaces from line 3168 (SECTION 13 comment) through line 3948 (just before /tab-ailog).
"""
import sys

DASHBOARD = "c:/ReactGitEC2/IS330/H.C Lombardo App/Dashboard/index.html"
DEVLOG = "c:/ReactGitEC2/IS330/H.C Lombardo App/devlog_output.html"

with open(DASHBOARD, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(DEVLOG, 'r', encoding='utf-8') as f:
    devlog_content = f.read()

# Find section 13 start and end
start_line = None
end_line = None
for i, line in enumerate(lines):
    if '<!-- ─── SECTION 13:' in line:
        start_line = i
    if '</div><!-- /tab-ailog -->' in line:
        end_line = i
        break

if start_line is None or end_line is None:
    print(f"ERROR: Could not find markers. start={start_line} end={end_line}")
    sys.exit(1)

print(f"Replacing lines {start_line+1} to {end_line} ({end_line - start_line} lines)")

# Build new content
new_section = (
    '    <!-- ─── SECTION 13: COMPLETE DEVELOPER LOG (AUTO-GENERATED FROM GIT) ─── -->\n'
    '    <div style="background:var(--card); border:1px solid var(--border); border-radius:0.75rem; padding:1.5rem; margin-bottom:1.5rem;">\n'
    '        <h3 style="font-size:1rem; font-weight:700; color:#FFD700; margin:0 0 0.5rem;">§13 — Complete Developer Log (Oct 7, 2025 – Apr 19, 2026)</h3>\n'
    '        <p style="color:var(--muted); font-size:0.8rem; margin-bottom:1rem;">369 commits. Every file. Every line number. Every bug and fix. Key commits include full code diffs.<br>'
    'GREEN text = additions &nbsp;·&nbsp; RED text = deletions &nbsp;·&nbsp; BLUE text = line numbers (@@ markers)<br>'
    'Full 24MB raw diff log: <code style="background:rgba(255,255,255,0.08); padding:0.1rem 0.4rem; border-radius:0.25rem; font-size:0.78rem;">docs/ai_reference/DEV_LOG_FULL.txt</code></p>\n'
    '        <details open>\n'
    '        <summary style="cursor:pointer; color:#79c0ff; font-size:0.82rem; font-weight:700; margin-bottom:0.75rem;">▼ Click to collapse / expand log</summary>\n'
    '        <div style="overflow-x:auto; max-height:80vh; overflow-y:auto;">\n'
    + devlog_content + '\n'
    '        </div>\n'
    '        </details>\n'
    '    </div>\n'
    '\n'
    '</div>\n'
    '</div><!-- /tab-ailog -->\n'
)

new_lines = lines[:start_line] + [new_section]
# Skip original lines from start_line to end_line (inclusive)
new_lines += lines[end_line+1:]

with open(DASHBOARD, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

import os
size = os.path.getsize(DASHBOARD)
print(f"Done. Dashboard is now {size:,} bytes ({size//1024} KB)")
