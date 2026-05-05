#!/usr/bin/env python3
"""Automate PM dashboard sprint board rollover scaffolding.

This script reads sprint schedule and backlog ticket assignments from
pmforge_dashboard/index.html, then either:

1) checks whether the target sprint board matches assigned tickets, or
2) replaces the target sprint placeholder board with generated subtasks.

Examples:
  python scripts/maintenance/dashboard_sprint_rollover.py check --sprint 15
  python scripts/maintenance/dashboard_sprint_rollover.py apply --sprint 15
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import pathlib
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple


SCHEDULE_RE = re.compile(
    r"\{\s*num:\s*(?P<num>\d+),\s*start:\s*'(?P<start>[^']+)',\s*end:\s*'(?P<end>[^']+)',\s*theme:\s*'(?P<theme>[^']+)',\s*displayDates:\s*'(?P<displayDates>[^']+)'\s*\}"
)

TICKET_RE = re.compile(
    r"\{\s*id:'(?P<id>[^']+)'.*?feature:'(?P<feature>[^']*)'.*?cat:'(?P<cat>[^']*)'.*?pri:'(?P<pri>[^']*)'.*?effort:'(?P<effort>[^']*)'.*?sprint:'(?P<sprint>[^']*)'.*?status:'(?P<status>[^']*)'.*?\}",
    re.S,
)

DIV_TAG_RE = re.compile(r"</?div\b[^>]*>", re.I)
TICKET_ID_RE = re.compile(r"^TA-(\d+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dashboard sprint rollover automation")
    parser.add_argument(
        "command",
        choices=["check", "apply"],
        help="check sprint-board coverage or apply generated sprint board",
    )
    parser.add_argument(
        "--sprint",
        type=int,
        required=True,
        help="target sprint number, e.g. 15",
    )
    parser.add_argument(
        "--file",
        default="pmforge_dashboard/index.html",
        help="path to dashboard index file",
    )
    parser.add_argument(
        "--include-done",
        action="store_true",
        help="include Done tickets assigned to the sprint when generating/checking board groups",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow replacing a non-placeholder sprint board",
    )
    return parser.parse_args()


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def parse_schedule(text: str) -> Dict[int, Dict[str, str]]:
    out: Dict[int, Dict[str, str]] = {}
    for m in SCHEDULE_RE.finditer(text):
        num = int(m.group("num"))
        out[num] = {
            "start": m.group("start"),
            "end": m.group("end"),
            "theme": m.group("theme"),
            "displayDates": m.group("displayDates"),
        }
    return out


def parse_tickets(text: str) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for m in TICKET_RE.finditer(text):
        items.append({
            "id": m.group("id"),
            "feature": m.group("feature"),
            "cat": m.group("cat"),
            "pri": m.group("pri"),
            "effort": m.group("effort"),
            "sprint": m.group("sprint"),
            "status": m.group("status"),
        })
    return items


def collect_sprint_tickets(
    items: Sequence[Dict[str, str]], sprint_num: int, include_done: bool
) -> List[Dict[str, str]]:
    sprint_tag = f"S{sprint_num}".upper()
    selected: List[Dict[str, str]] = []
    for item in items:
        if str(item.get("sprint", "")).strip().upper() != sprint_tag:
            continue
        ticket_id = str(item.get("id", "")).strip().upper()
        if not TICKET_ID_RE.match(ticket_id):
            continue
        status = str(item.get("status", "")).strip().lower()
        if not include_done and status == "done":
            continue
        selected.append(item)
    return selected


def find_div_block(text: str, div_id: str) -> Optional[Tuple[int, int]]:
    marker = f'<div id="{div_id}"'
    start = text.find(marker)
    if start < 0:
        return None

    depth = 0
    for m in DIV_TAG_RE.finditer(text, start):
        token = m.group(0).lower()
        if token.startswith("<div"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return (start, m.end())
    return None


def find_comment_start(text: str, sprint_num: int, div_start: int) -> int:
    lookback_start = max(0, div_start - 260)
    fragment = text[lookback_start:div_start]
    matches = list(re.finditer(rf"<!--\s*Sprint\s+{sprint_num}[^>]*-->", fragment, re.I))
    if not matches:
        return div_start
    return lookback_start + matches[-1].start()


def extract_board_ticket_ids(text: str, sprint_num: int) -> List[str]:
    block = find_div_block(text, f"sprint-board-{sprint_num}")
    if not block:
        return []
    block_text = text[block[0] : block[1]]
    ticket_ids = sorted(set(re.findall(r"TA-\d+", block_text.upper())), key=ticket_sort_key)
    return ticket_ids


def ticket_sort_key(ticket_id: str) -> Tuple[int, str]:
    m = re.search(r"(\d+)", ticket_id)
    return (int(m.group(1)) if m else 999999, ticket_id)


def is_placeholder_board(board_text: str, sprint_num: int) -> bool:
    return f'id="sprint{sprint_num}-board"' not in board_text


def format_date_range(start_iso: str, end_iso: str) -> str:
    start = dt.date.fromisoformat(start_iso)
    end = dt.date.fromisoformat(end_iso)
    if start.year == end.year and start.month == end.month:
        return f"{start.strftime('%b')} {start.day} - {end.day}, {start.year}"
    if start.year == end.year:
        return f"{start.strftime('%b')} {start.day} - {end.strftime('%b')} {end.day}, {start.year}"
    return f"{start.strftime('%b')} {start.day}, {start.year} - {end.strftime('%b')} {end.day}, {end.year}"


def sprint_status(start_iso: str, end_iso: str) -> str:
    today = dt.date.today()
    start = dt.date.fromisoformat(start_iso)
    end = dt.date.fromisoformat(end_iso)
    if today < start:
        return "upcoming"
    if today > end:
        return "completed"
    return "active"


def choose_area(cat: str) -> Tuple[str, str]:
    c = cat.strip().lower()
    if c == "ml":
        return ("ml", "ML Execution")
    if c in {"frontend", "backend", "data", "security", "qa"}:
        return ("app", "App/Data Execution")
    return ("platform", "Platform/Delivery")


def build_subtasks(ticket: Dict[str, str]) -> List[str]:
    ticket_id = ticket["id"]
    feature = ticket["feature"].strip()
    cat = ticket["cat"].strip().lower()
    lowered = feature.lower()

    if "duplicate of" in lowered or "consolidated" in lowered:
        return [
            f"Confirm existing evidence fully covers {ticket_id} duplicate scope",
            "Validate no remaining mismatch/regression exists in active execution paths",
            "Record duplicate consolidation evidence in TASK_DETAILS and parent ticket status",
        ]

    if cat == "ml":
        return [
            f"Confirm {ticket_id} inputs/dependencies and baseline expectations",
            "Implement model/pipeline changes for this ticket scope",
            "Run validation checks (metrics/endpoints) and capture outputs",
            "Record completion evidence in TASK_DETAILS and parent ticket",
        ]

    if cat == "infrastructure":
        return [
            f"Confirm environment/access prerequisites for {ticket_id}",
            "Execute infrastructure/runtime changes in controlled sequence",
            "Validate service health/operations after changes",
            "Document commands, evidence, and rollback notes in TASK_DETAILS",
        ]

    if cat == "frontend":
        return [
            f"Confirm UX/API acceptance scope for {ticket_id}",
            "Implement UI/runtime updates for the ticket",
            "Verify behavior on target pages and resolve regressions",
            "Capture validation evidence in TASK_DETAILS and parent ticket",
        ]

    return [
        f"Confirm acceptance scope and dependencies for {ticket_id}",
        "Implement core ticket changes",
        "Validate results against acceptance criteria",
        "Record evidence in TASK_DETAILS and parent ticket",
    ]


def safe_text(value: str) -> str:
    return html.escape(value, quote=True)


def build_board_html(
    sprint_num: int,
    schedule: Dict[str, str],
    tickets: Sequence[Dict[str, str]],
) -> str:
    status = sprint_status(schedule["start"], schedule["end"])
    theme = schedule["theme"]
    date_label = format_date_range(schedule["start"], schedule["end"])

    if status == "active":
        status_label = "Active"
        status_style = ' style="color:#10b981; border-color:#10b981;"'
        subtitle = f"Sprint {sprint_num} is active. Execute the committed ticket plan and track progress here."
    elif status == "completed":
        status_label = "Completed"
        status_style = ' style="color:#10b981; border-color:#10b981;"'
        subtitle = f"Sprint {sprint_num} completed. Board is retained as archive history."
    else:
        status_label = "Upcoming"
        status_style = ""
        subtitle = f"Starts {dt.date.fromisoformat(schedule['start']).strftime('%b %d, %Y')}. Board activates at sprint kickoff."

    area_order = ["ml", "app", "platform"]
    area_titles = {
        "ml": "ML Execution",
        "app": "App/Data Execution",
        "platform": "Platform/Delivery",
    }

    grouped: Dict[str, List[Tuple[Dict[str, str], List[str]]]] = {k: [] for k in area_order}
    total_subtasks = 0

    for ticket in tickets:
        area_key, _ = choose_area(ticket["cat"])
        subtasks = build_subtasks(ticket)
        grouped[area_key].append((ticket, subtasks))
        total_subtasks += len(subtasks)

    lines: List[str] = []
    lines.append(f"    <!-- Sprint {sprint_num} board -->")
    lines.append(f"    <div id=\"sprint-board-{sprint_num}\" style=\"display:none;\">")
    lines.append("        <div class=\"pm-panel\">")
    lines.append(
        "            <div class=\"pm-header\"><div><h2>Sprint "
        + str(sprint_num)
        + " - "
        + safe_text(theme)
        + "</h2><p>"
        + safe_text(subtitle)
        + "</p></div><div class=\"sprint-meta\"><span class=\"meta-pill\">"
        + safe_text(date_label)
        + "</span><span class=\"meta-pill\""
        + status_style
        + ">"
        + status_label
        + "</span></div></div>"
    )
    lines.append("")
    lines.append("            <div style=\"max-width:940px; margin:0 0 1rem;\">")
    lines.append(
        f"                <div class=\"progress-label\"><span>Sprint {sprint_num} Progress</span><span id=\"s{sprint_num}-pct\">0%</span></div>"
    )
    lines.append(
        f"                <div class=\"progress-bar-wrap\"><div class=\"progress-bar-fill\" id=\"s{sprint_num}-fill\" style=\"width:0%\"></div></div>"
    )
    lines.append(
        f"                <div style=\"font-size:0.75rem;color:var(--muted);margin-top:0.4rem;\" id=\"s{sprint_num}-count\">0 of {total_subtasks} Sprint {sprint_num} subtasks complete</div>"
    )
    lines.append("            </div>")
    lines.append("")
    lines.append(f"            <div class=\"area-grid\" id=\"sprint{sprint_num}-board\">")
    lines.append("")

    for area_key in area_order:
        groups = grouped[area_key]
        if not groups:
            continue

        area_total = sum(len(s) for _, s in groups)
        area_id = f"s{sprint_num}-{area_key}"
        area_title = area_titles[area_key]

        lines.append("                <div class=\"area-card\">")
        lines.append(
            f"                    <div class=\"area-header\" onclick=\"toggleArea('{area_id}')\">"
        )
        lines.append(
            f"                        <div class=\"area-title\">{safe_text(area_title)} <span class=\"area-count\" id=\"count-{area_id}\">0/{area_total}</span></div>"
        )
        lines.append(f"                        <span id=\"arrow-{area_id}\">▾</span>")
        lines.append("                    </div>")
        lines.append(f"                    <div class=\"area-body\" id=\"{area_id}\">")

        for ticket, subtasks in groups:
            ticket_id = ticket["id"]
            ticket_feature = safe_text(ticket["feature"])
            lines.append(f"                        <div class=\"task-group-label\">{ticket_id} - {ticket_feature}</div>")

            num_match = TICKET_ID_RE.match(ticket_id)
            ta_num = num_match.group(1) if num_match else ticket_id.replace("-", "")

            for idx, subtask in enumerate(subtasks, start=1):
                subtask_id = f"sp{sprint_num}_ta{ta_num}_{idx}"
                lines.append(
                    "                        <label class=\"task-item task-sub-item\"><input type=\"checkbox\" id=\""
                    + subtask_id
                    + "\" onchange=\"updateSprintBoardProgress("
                    + str(sprint_num)
                    + ")\"><span class=\"task-text\">"
                    + safe_text(subtask)
                    + "</span></label>"
                )

            lines.append("")

        lines.append("                    </div>")
        lines.append("                </div>")
        lines.append("")

    lines.append("            </div>")
    lines.append("        </div>")
    lines.append("    </div>")

    return "\n".join(lines) + "\n"


def check_mode(
    text: str,
    sprint_num: int,
    tickets: Sequence[Dict[str, str]],
    include_done: bool,
) -> int:
    sprint_tickets = collect_sprint_tickets(tickets, sprint_num, include_done=include_done)
    assigned_ids = sorted({t["id"].upper() for t in sprint_tickets}, key=ticket_sort_key)
    board_ids = extract_board_ticket_ids(text, sprint_num)

    assigned_set = set(assigned_ids)
    board_set = set(board_ids)

    missing = sorted(assigned_set - board_set, key=ticket_sort_key)
    extra = sorted(board_set - assigned_set, key=ticket_sort_key)

    print(f"Sprint {sprint_num} assigned tickets ({len(assigned_ids)}): {', '.join(assigned_ids) if assigned_ids else 'none'}")
    print(f"Sprint {sprint_num} board ticket groups ({len(board_ids)}): {', '.join(board_ids) if board_ids else 'none'}")

    progress_ids_ok = all(
        f'id="s{sprint_num}-{suffix}"' in text for suffix in ("fill", "pct", "count")
    )
    board_inner_ok = f'id="sprint{sprint_num}-board"' in text

    if missing:
        print("Missing ticket groups:", ", ".join(missing))
    if extra:
        print("Extra board ticket groups:", ", ".join(extra))

    print(
        "Progress widgets present:",
        "yes" if progress_ids_ok else "no",
        "| Sprint board container present:",
        "yes" if board_inner_ok else "no",
    )

    if missing or not progress_ids_ok or not board_inner_ok:
        print("Check result: FAIL")
        return 2

    print("Check result: PASS")
    return 0


def apply_mode(
    text: str,
    sprint_num: int,
    schedule_map: Dict[int, Dict[str, str]],
    tickets: Sequence[Dict[str, str]],
    include_done: bool,
    force: bool,
) -> Tuple[str, str]:
    if sprint_num not in schedule_map:
        raise ValueError(f"Sprint {sprint_num} is not defined in SPRINT_SCHEDULE")

    sprint_tickets = collect_sprint_tickets(tickets, sprint_num, include_done=include_done)
    if not sprint_tickets:
        raise ValueError(
            f"No sprint-assigned TA tickets found for S{sprint_num}. Assign tickets in PB_ITEMS first."
        )

    div_block = find_div_block(text, f"sprint-board-{sprint_num}")
    if not div_block:
        raise ValueError(f"Could not locate div id=\"sprint-board-{sprint_num}\" in dashboard file")

    current_block = text[div_block[0] : div_block[1]]
    if not force and not is_placeholder_board(current_block, sprint_num):
        raise ValueError(
            f"Sprint {sprint_num} already has a populated board. Use --force to replace it intentionally."
        )

    comment_start = find_comment_start(text, sprint_num, div_block[0])
    generated = build_board_html(sprint_num, schedule_map[sprint_num], sprint_tickets)

    updated = text[:comment_start] + generated + text[div_block[1] :]
    summary = f"Generated Sprint {sprint_num} board with {len(sprint_tickets)} ticket groups"
    return updated, summary


def main() -> int:
    args = parse_args()
    dashboard_path = pathlib.Path(args.file)

    if not dashboard_path.exists():
        print(f"Error: dashboard file not found: {dashboard_path}")
        return 1

    text = read_text(dashboard_path)
    schedule_map = parse_schedule(text)
    tickets = parse_tickets(text)

    if args.command == "check":
        return check_mode(text, args.sprint, tickets, include_done=args.include_done)

    try:
        updated, summary = apply_mode(
            text,
            args.sprint,
            schedule_map,
            tickets,
            include_done=args.include_done,
            force=args.force,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    write_text(dashboard_path, updated)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
