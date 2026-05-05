#!/usr/bin/env python3
"""Fail-closed closure gate for dashboard sprint/subtask bookkeeping.

This checker prevents silent drift between:
- Sprint board checkbox IDs
- COMPLETED_TASKS entries
- TASK_DETAILS entries
- PB_ITEMS parent ticket status

Examples:
  python scripts/maintenance/dashboard_closure_gate.py check --sprint 14
  python scripts/maintenance/dashboard_closure_gate.py subtask --sprint 14 --subtask s19_1
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Optional, Sequence, Set, Tuple


TOKEN_RE = re.compile(
    r'<div class="task-group-label">(?P<label>.*?)</div>|<input type="checkbox"\s+id="(?P<id>[^"]+)"',
    re.S | re.I,
)

TA_RE = re.compile(r"TA-\d+", re.I)


@dataclass
class BoardData:
    subtask_ids: List[str]
    subtask_to_ticket: Dict[str, str]
    ticket_to_subtasks: Dict[str, List[str]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail-closed dashboard closure gate"
    )
    parser.add_argument(
        "command",
        choices=["check", "subtask"],
        help="check full sprint bookkeeping or validate one subtask closure",
    )
    parser.add_argument(
        "--sprint",
        type=int,
        required=True,
        help="target sprint number, e.g. 14",
    )
    parser.add_argument(
        "--subtask",
        help="subtask id (required for subtask command), e.g. s19_1",
    )
    parser.add_argument(
        "--ticket",
        help="optional explicit parent ticket for subtask command, e.g. TA-019",
    )
    parser.add_argument(
        "--file",
        default="pmforge_dashboard/index.html",
        help="path to dashboard index file",
    )
    return parser.parse_args()


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def find_div_block(text: str, div_id: str) -> Optional[Tuple[int, int]]:
    marker = f'<div id="{div_id}"'
    start = text.find(marker)
    if start < 0:
        return None

    depth = 0
    in_string: Optional[str] = None
    in_line_comment = False
    in_block_comment = False

    i = start
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

        if text.startswith("<div", i):
            depth += 1
        elif text.startswith("</div", i):
            depth -= 1
            if depth == 0:
                end = text.find(">", i)
                if end < 0:
                    return None
                return (start, end + 1)

        i += 1

    return None


def extract_enclosed_block(
    text: str,
    marker: str,
    open_char: str,
    close_char: str,
    start_idx: int = 0,
) -> str:
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
                return text[open_pos + 1 : i]

        i += 1

    raise ValueError(f"Unbalanced block for marker: {marker}")


def parse_completed_tasks(text: str) -> Set[str]:
    body = extract_enclosed_block(text, "const COMPLETED_TASKS =", "[", "]")
    return {m.group(1).strip() for m in re.finditer(r"'([^']+)'", body)}


def parse_task_details_keys(text: str) -> Set[str]:
    body = extract_enclosed_block(text, "const TASK_DETAILS =", "{", "}")
    keys: Set[str] = set()

    depth_brace = 0
    depth_bracket = 0
    in_string: Optional[str] = None
    in_line_comment = False
    in_block_comment = False

    i = 0
    while i < len(body):
        ch = body[i]
        nxt = body[i + 1] if i + 1 < len(body) else ""

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

        if ch == "{":
            depth_brace += 1
            i += 1
            continue
        if ch == "}":
            depth_brace = max(0, depth_brace - 1)
            i += 1
            continue
        if ch == "[":
            depth_bracket += 1
            i += 1
            continue
        if ch == "]":
            depth_bracket = max(0, depth_bracket - 1)
            i += 1
            continue

        if depth_brace == 0 and depth_bracket == 0 and (ch.isalpha() or ch == "_"):
            start = i
            i += 1
            while i < len(body) and (body[i].isalnum() or body[i] == "_"):
                i += 1
            key = body[start:i]

            j = i
            while j < len(body) and body[j].isspace():
                j += 1
            if j < len(body) and body[j] == ":":
                keys.add(key)
            continue

        i += 1

    return keys


def parse_pb_status_map(text: str) -> Dict[str, str]:
    backlog_fn_pos = text.find("(function buildProductBacklog()")
    if backlog_fn_pos < 0:
        raise ValueError("Could not locate buildProductBacklog function")

    body = extract_enclosed_block(
        text,
        "var items = [",
        "[",
        "]",
        start_idx=backlog_fn_pos,
    )
    status_map: Dict[str, str] = {}

    for obj in split_top_level_objects(body):
        id_match = re.search(r"\bid\s*:\s*'([^']+)'", obj)
        status_match = re.search(r"\bstatus\s*:\s*'([^']+)'", obj)
        if not id_match or not status_match:
            continue

        ticket_id = id_match.group(1).strip().upper()
        status = status_match.group(1).strip()
        if ticket_id.startswith("TA-"):
            status_map[ticket_id] = status

    return status_map


def split_top_level_objects(array_body: str) -> List[str]:
    objects: List[str] = []
    in_string: Optional[str] = None
    in_line_comment = False
    in_block_comment = False

    depth = 0
    start_idx: Optional[int] = None
    i = 0

    while i < len(array_body):
        ch = array_body[i]
        nxt = array_body[i + 1] if i + 1 < len(array_body) else ""

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

        if ch == "{":
            if depth == 0:
                start_idx = i
            depth += 1
            i += 1
            continue

        if ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start_idx is not None:
                    objects.append(array_body[start_idx : i + 1])
                    start_idx = None
            i += 1
            continue

        i += 1

    return objects


def parse_sprint_board(text: str, sprint_num: int) -> BoardData:
    block = find_div_block(text, f"sprint-board-{sprint_num}")
    if not block:
        raise ValueError(f'Could not locate div id="sprint-board-{sprint_num}"')

    block_text = text[block[0] : block[1]]
    subtask_ids: List[str] = []
    subtask_to_ticket: Dict[str, str] = {}
    ticket_to_subtasks: DefaultDict[str, List[str]] = defaultdict(list)

    current_ticket: Optional[str] = None
    for token in TOKEN_RE.finditer(block_text):
        label = token.group("label")
        task_id = token.group("id")

        if label is not None:
            cleaned = html.unescape(re.sub(r"<[^>]+>", " ", label))
            ticket_match = TA_RE.search(cleaned)
            if ticket_match:
                current_ticket = ticket_match.group(0).upper()
            continue

        if task_id is not None:
            task_id = task_id.strip()
            subtask_ids.append(task_id)
            if current_ticket:
                subtask_to_ticket[task_id] = current_ticket
                ticket_to_subtasks[current_ticket].append(task_id)

    return BoardData(
        subtask_ids=subtask_ids,
        subtask_to_ticket=subtask_to_ticket,
        ticket_to_subtasks=dict(ticket_to_subtasks),
    )


def normalize_ticket_id(ticket_id: str) -> str:
    return ticket_id.strip().upper()


def print_list(label: str, values: Sequence[str]) -> None:
    if not values:
        return
    print(f"- {label} ({len(values)}):")
    for value in values:
        print(f"  - {value}")


def evaluate_parent_status(
    ticket_to_subtasks: Dict[str, List[str]],
    completed: Set[str],
    pb_status: Dict[str, str],
) -> Tuple[List[str], List[str], List[str]]:
    missing_parent: List[str] = []
    parent_should_be_done: List[str] = []
    parent_should_not_be_done: List[str] = []

    for ticket, subtasks in sorted(ticket_to_subtasks.items()):
        status = pb_status.get(ticket)
        if status is None:
            missing_parent.append(ticket)
            continue

        done_count = sum(1 for subtask in subtasks if subtask in completed)
        all_done = done_count == len(subtasks) and len(subtasks) > 0
        status_norm = status.strip().lower()

        if all_done and status_norm != "done":
            parent_should_be_done.append(
                f"{ticket} status='{status}' but {done_count}/{len(subtasks)} subtasks are complete"
            )
        if not all_done and status_norm == "done":
            parent_should_not_be_done.append(
                f"{ticket} status='Done' but only {done_count}/{len(subtasks)} subtasks are complete"
            )

    return missing_parent, parent_should_be_done, parent_should_not_be_done


def check_command(args: argparse.Namespace, text: str) -> int:
    board = parse_sprint_board(text, args.sprint)
    completed = parse_completed_tasks(text)
    details = parse_task_details_keys(text)
    pb_status = parse_pb_status_map(text)

    board_set = set(board.subtask_ids)
    completed_on_board = sorted(task for task in board.subtask_ids if task in completed)
    details_on_board = sorted(task for task in board.subtask_ids if task in details)

    details_without_completed = sorted(task for task in board.subtask_ids if task in details and task not in completed)
    completed_without_details = sorted(task for task in board.subtask_ids if task in completed and task not in details)

    missing_parent, parent_should_be_done, parent_should_not_be_done = evaluate_parent_status(
        board.ticket_to_subtasks,
        completed,
        pb_status,
    )

    print(f"Sprint {args.sprint} closure gate")
    print(f"- Sprint board subtasks: {len(board_set)}")
    print(f"- Completed subtasks on board: {len(completed_on_board)}")
    print(f"- TASK_DETAILS entries on board: {len(details_on_board)}")

    failed = False

    if details_without_completed:
        failed = True
        print_list("TASK_DETAILS present but missing from COMPLETED_TASKS", details_without_completed)

    if completed_without_details:
        failed = True
        print_list("COMPLETED_TASKS present but missing TASK_DETAILS", completed_without_details)

    if missing_parent:
        failed = True
        print_list("Parent TA missing from PB_ITEMS", missing_parent)

    if parent_should_be_done:
        failed = True
        print_list("Parent TA status should be Done", parent_should_be_done)

    if parent_should_not_be_done:
        failed = True
        print_list("Parent TA status should not be Done", parent_should_not_be_done)

    if failed:
        print("\nFAIL: Closure gate failed. Fix dashboard bookkeeping before moving on.")
        return 1

    print("\nPASS: Closure gate passed. Sprint bookkeeping is aligned.")
    return 0


def subtask_command(args: argparse.Namespace, text: str) -> int:
    if not args.subtask:
        print("Error: --subtask is required for subtask command")
        return 2

    subtask_id = args.subtask.strip()
    board = parse_sprint_board(text, args.sprint)
    completed = parse_completed_tasks(text)
    details = parse_task_details_keys(text)
    pb_status = parse_pb_status_map(text)

    exists_on_board = subtask_id in set(board.subtask_ids)
    parent_ticket = board.subtask_to_ticket.get(subtask_id)

    if args.ticket:
        expected_ticket = normalize_ticket_id(args.ticket)
        if parent_ticket and expected_ticket != parent_ticket:
            print(
                f"FAIL: Subtask {subtask_id} belongs to {parent_ticket}, not {expected_ticket}."
            )
            return 1
        if parent_ticket is None:
            parent_ticket = expected_ticket

    in_completed = subtask_id in completed
    in_details = subtask_id in details

    parent_coherent = False
    parent_msg = "Parent ticket could not be evaluated"

    if parent_ticket:
        subtasks = board.ticket_to_subtasks.get(parent_ticket, [])
        status = pb_status.get(parent_ticket)
        if status is None:
            parent_msg = f"Parent {parent_ticket} is missing in PB_ITEMS"
            parent_coherent = False
        else:
            done_count = sum(1 for task in subtasks if task in completed)
            all_done = done_count == len(subtasks) and len(subtasks) > 0
            status_norm = status.strip().lower()
            parent_coherent = (all_done and status_norm == "done") or (
                (not all_done) and status_norm != "done"
            )
            parent_msg = (
                f"Parent {parent_ticket} status='{status}' with {done_count}/{len(subtasks)} subtasks complete"
            )

    print(f"Subtask closure gate: {subtask_id} (Sprint {args.sprint})")
    print(f"- Exists on sprint board: {'PASS' if exists_on_board else 'FAIL'}")
    print(f"- Present in COMPLETED_TASKS: {'PASS' if in_completed else 'FAIL'}")
    print(f"- Present in TASK_DETAILS: {'PASS' if in_details else 'FAIL'}")
    print(f"- Parent status coherence: {'PASS' if parent_coherent else 'FAIL'}")
    print(f"  {parent_msg}")

    passed = exists_on_board and in_completed and in_details and parent_coherent
    if not passed:
        print("\nFAIL: Subtask closure gate failed.")
        return 1

    print("\nPASS: Subtask closure gate passed.")
    return 0


def main() -> int:
    args = parse_args()
    dashboard_path = pathlib.Path(args.file)

    if not dashboard_path.exists():
        print(f"Error: dashboard file not found: {dashboard_path}")
        return 2

    text = read_text(dashboard_path)

    try:
        if args.command == "check":
            return check_command(args, text)
        if args.command == "subtask":
            return subtask_command(args, text)
        print(f"Error: unknown command: {args.command}")
        return 2
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
