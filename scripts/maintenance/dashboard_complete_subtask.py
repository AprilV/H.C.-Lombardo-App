#!/usr/bin/env python3
"""Automate dashboard bookkeeping for one completed subtask.

This updater writes completion state into pmforge_dashboard/index.html by:
- adding subtask to COMPLETED_TASKS
- removing subtask from BLOCKED_TASKS (if present)
- upserting TASK_DETAILS entry
- syncing parent PB item status for the ticket

Use dashboard_closure_receipt.ps1 immediately after this script to enforce
pass/fail closure checks.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import pathlib
import re
import shutil
import sys
from typing import Optional, Tuple


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import dashboard_closure_gate as gate  # noqa: E402


DEFAULT_BACKUP_ROOT = pathlib.Path("backups") / "dashboard_automation"


def parse_args() -> argparse.Namespace:
    now = dt.datetime.now()
    default_date = f"{now.strftime('%b')} {now.day}, {now.year}"
    default_timestamp = now.strftime("%Y-%m-%dT%H:%M")

    parser = argparse.ArgumentParser(
        description="Update dashboard bookkeeping for one completed subtask"
    )
    parser.add_argument("--sprint", type=int, required=True, help="Sprint number")
    parser.add_argument("--subtask", required=True, help="Subtask id, e.g. s19_2")
    parser.add_argument(
        "--resolution",
        required=True,
        help="Resolution text to write into TASK_DETAILS",
    )
    parser.add_argument(
        "--date",
        default=default_date,
        help="Completion date label, e.g. May 5, 2026",
    )
    parser.add_argument(
        "--timestamp",
        default=default_timestamp,
        help="Completion timestamp in local ISO minute format",
    )
    parser.add_argument(
        "--updated-by",
        default="Copilot (automation)",
        help="Value for TASK_DETAILS.updatedBy",
    )
    parser.add_argument(
        "--file",
        default="pmforge_dashboard/index.html",
        help="Path to dashboard source file",
    )
    parser.add_argument(
        "--backup-dir",
        default=str(DEFAULT_BACKUP_ROOT),
        help="Directory for pre-write backup snapshots",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show intended updates without writing the file",
    )
    return parser.parse_args()


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def ensure_parent_dir(path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def compute_sha256_file(path: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def create_dashboard_backup(
    source_path: pathlib.Path,
    backup_root: pathlib.Path,
) -> Tuple[pathlib.Path, str]:
    backup_root.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_name = f"{source_path.stem}_{timestamp}.bak{source_path.suffix}"
    backup_path = backup_root / backup_name
    suffix = 1
    while backup_path.exists():
        backup_name = f"{source_path.stem}_{timestamp}_{suffix}.bak{source_path.suffix}"
        backup_path = backup_root / backup_name
        suffix += 1

    shutil.copy2(source_path, backup_path)
    return backup_path, compute_sha256_file(backup_path)


def write_text(path: pathlib.Path, text: str) -> None:
    ensure_parent_dir(path)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(text, encoding="utf-8", newline="\n")
    tmp_path.replace(path)


def find_enclosed_bounds(
    text: str,
    marker: str,
    open_char: str,
    close_char: str,
    start_idx: int = 0,
) -> Tuple[int, int]:
    marker_pos = text.find(marker, start_idx)
    if marker_pos < 0:
        raise ValueError(f"Could not find marker: {marker}")

    open_pos = text.find(open_char, marker_pos)
    if open_pos < 0:
        raise ValueError(f"Could not find '{open_char}' after marker: {marker}")

    depth = 0
    in_string: Optional[str] = None
    in_line_comment = False
    in_block_comment = False

    i = open_pos
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_string:
            if ch == "\\":
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue

        if ch == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue
        if ch in ("'", '"', "`"):
            in_string = ch
            i += 1
            continue

        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return (open_pos, i)

        i += 1

    raise ValueError(f"Unbalanced block for marker: {marker}")


def replace_enclosed_body(
    text: str,
    marker: str,
    open_char: str,
    close_char: str,
    new_body: str,
    start_idx: int = 0,
) -> str:
    open_pos, close_pos = find_enclosed_bounds(
        text,
        marker,
        open_char,
        close_char,
        start_idx=start_idx,
    )
    return text[: open_pos + 1] + new_body + text[close_pos:]


def escape_js_single(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\r", " ")
        .replace("\n", " ")
        .strip()
    )


def add_completed_task(text: str, subtask: str) -> Tuple[str, bool]:
    body = gate.extract_enclosed_block(text, "const COMPLETED_TASKS =", "[", "]")
    existing = {m.group(1).strip() for m in re.finditer(r"'([^']+)'", body)}
    if subtask in existing:
        return text, False

    new_body = body.rstrip() + f"\n    '{subtask}',\n"
    updated = replace_enclosed_body(text, "const COMPLETED_TASKS =", "[", "]", new_body)
    return updated, True


def remove_blocked_task(text: str, subtask: str) -> Tuple[str, bool]:
    try:
        body = gate.extract_enclosed_block(text, "const BLOCKED_TASKS =", "[", "]")
    except ValueError:
        return text, False

    pattern = re.compile(rf"(?m)^\s*'{re.escape(subtask)}',\s*(//.*)?\n?")
    new_body = pattern.sub("", body)
    if new_body == body:
        return text, False

    updated = replace_enclosed_body(text, "const BLOCKED_TASKS =", "[", "]", new_body)
    return updated, True


def upsert_task_detail(
    text: str,
    subtask: str,
    resolution: str,
    date_label: str,
    timestamp: str,
    updated_by: str,
) -> Tuple[str, bool]:
    body = gate.extract_enclosed_block(text, "const TASK_DETAILS =", "{", "}")
    entry = (
        f"    {subtask}: {{ resolution:'{escape_js_single(resolution)}', "
        f"date:'{escape_js_single(date_label)}', "
        f"timestamp:'{escape_js_single(timestamp)}', "
        f"updatedBy:'{escape_js_single(updated_by)}' }},"
    )

    line_re = re.compile(rf"(?m)^\s*{re.escape(subtask)}\s*:\s*\{{.*?\}},\s*$")
    if line_re.search(body):
        new_body = line_re.sub(entry, body, count=1)
        if new_body == body:
            return text, False
        updated = replace_enclosed_body(text, "const TASK_DETAILS =", "{", "}", new_body)
        return updated, True

    new_body = body.rstrip() + "\n" + entry + "\n"
    updated = replace_enclosed_body(text, "const TASK_DETAILS =", "{", "}", new_body)
    return updated, True


def set_parent_ticket_status(
    text: str,
    parent_ticket: str,
    desired_status: str,
) -> Tuple[str, bool]:
    line_re = re.compile(
        rf"(?m)^(\s*\{{\s*id:'{re.escape(parent_ticket)}'[^\n]*?status:')([^']*)('.*)$"
    )
    m = line_re.search(text)
    if not m:
        raise ValueError(f"Could not find PB item line for parent ticket: {parent_ticket}")

    current_status = m.group(2).strip()
    if current_status == desired_status:
        return text, False

    updated = line_re.sub(rf"\1{desired_status}\3", text, count=1)
    return updated, True


def choose_parent_status(current_status: str, all_done: bool) -> str:
    cur = (current_status or "").strip().lower()
    if all_done:
        return "Done"
    if cur in {"done", "backlog", "tbd"}:
        return "In Sprint"
    if cur == "in progress":
        return "In Sprint"
    return current_status


def get_parent_status(text: str, parent_ticket: str) -> str:
    line_re = re.compile(
        rf"(?m)^\s*\{{\s*id:'{re.escape(parent_ticket)}'[^\n]*?status:'([^']*)'"
    )
    m = line_re.search(text)
    if not m:
        raise ValueError(f"Could not read parent status for ticket: {parent_ticket}")
    return m.group(1).strip()


def main() -> int:
    args = parse_args()
    dashboard_path = pathlib.Path(args.file).resolve()
    if not dashboard_path.exists():
        print(f"Error: dashboard file not found: {dashboard_path}")
        return 2

    text = read_text(dashboard_path)
    board = gate.parse_sprint_board(text, args.sprint)

    subtask = args.subtask.strip()
    if subtask not in set(board.subtask_ids):
        print(f"Error: subtask {subtask} is not on Sprint {args.sprint} board")
        return 2

    parent_ticket = board.subtask_to_ticket.get(subtask)
    if not parent_ticket:
        print(f"Error: could not determine parent ticket for subtask {subtask}")
        return 2

    changed_completed = False
    changed_blocked = False
    changed_details = False
    changed_parent = False
    backup_path: Optional[pathlib.Path] = None
    backup_sha256: Optional[str] = None
    dashboard_sha256_after: Optional[str] = None

    text, changed_completed = add_completed_task(text, subtask)
    text, changed_blocked = remove_blocked_task(text, subtask)
    text, changed_details = upsert_task_detail(
        text,
        subtask,
        args.resolution,
        args.date,
        args.timestamp,
        args.updated_by,
    )

    completed_after = gate.parse_completed_tasks(text)
    parent_subtasks = board.ticket_to_subtasks.get(parent_ticket, [])
    all_done = bool(parent_subtasks) and all(
        st in completed_after for st in parent_subtasks
    )

    current_parent_status = get_parent_status(text, parent_ticket)
    desired_parent_status = choose_parent_status(current_parent_status, all_done)
    text, changed_parent = set_parent_ticket_status(
        text,
        parent_ticket,
        desired_parent_status,
    )

    has_changes = any(
        [changed_completed, changed_blocked, changed_details, changed_parent]
    )

    if args.dry_run:
        print("DRY RUN: no file write performed")
    elif has_changes:
        backup_root = pathlib.Path(args.backup_dir).resolve()
        backup_path, backup_sha256 = create_dashboard_backup(dashboard_path, backup_root)
        write_text(dashboard_path, text)
        dashboard_sha256_after = compute_sha256_file(dashboard_path)
    else:
        print("NO CHANGES: dashboard file already aligned; no file write performed")

    print(f"sprint={args.sprint}")
    print(f"subtask={subtask}")
    print(f"parent_ticket={parent_ticket}")
    print(f"parent_all_subtasks_done={all_done}")
    print(f"parent_status_before={current_parent_status}")
    print(f"parent_status_after={desired_parent_status}")
    print(f"changed_completed_tasks={changed_completed}")
    print(f"changed_blocked_tasks={changed_blocked}")
    print(f"changed_task_details={changed_details}")
    print(f"changed_parent_status={changed_parent}")
    print(f"wrote_file={not args.dry_run and has_changes}")
    print(f"backup_created={backup_path is not None}")
    if backup_path is not None:
        print(f"backup_path={backup_path.as_posix()}")
        print(f"backup_sha256={backup_sha256}")
    if dashboard_sha256_after is not None:
        print(f"dashboard_sha256_after={dashboard_sha256_after}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
