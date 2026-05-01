"""Dashboard persistence API for teacher-facing automation.

This module provides persisted CRUD endpoints and aggregate endpoints used by the
dashboard automation phases. It is intentionally self-contained so `api_server.py`
can import `register_dashboard_routes` directly in production startup.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import psycopg2
from flask import Blueprint, jsonify, request
from psycopg2.extras import RealDictCursor

from db_config import DATABASE_CONFIG


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard/v1")
_DB_READY = False


def _json_ok(data: Any, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def _json_error(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def _normalize_status(raw: Optional[str]) -> str:
    val = str(raw or "").strip().lower()
    mapping = {
        "to do": "todo",
        "todo": "todo",
        "backlog": "todo",
        "tbd": "todo",
        "in sprint": "in_progress",
        "in progress": "in_progress",
        "in_progress": "in_progress",
        "blocked": "blocked",
        "done": "done",
    }
    return mapping.get(val, "todo")


def _normalize_priority(raw: Optional[str]) -> str:
    val = str(raw or "").strip().lower()
    return val if val in {"critical", "high", "medium", "low"} else "medium"


def _normalize_effort(raw: Optional[str]) -> str:
    val = str(raw or "").strip().lower()
    return val if val in {"xs", "s", "m", "l", "xl"} else "m"


def _normalize_source(raw: Optional[str]) -> str:
    val = str(raw or "").strip().lower()
    return val if val in {"ui", "migration", "system", "api"} else "api"


def _normalize_sprint(raw: Optional[str]) -> str:
    clean = str(raw or "").strip().upper()
    return clean if clean else "TBD"


def _serialize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _serialize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _serialize(v) for k, v in row.items()}


def _connect():
    return psycopg2.connect(**DATABASE_CONFIG)


def _fetch_one(cur, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    cur.execute(query, params)
    row = cur.fetchone()
    return _serialize_row(row) if row else None


def _fetch_all(cur, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    cur.execute(query, params)
    return [_serialize_row(r) for r in cur.fetchall()]


def _record_event(cur, entity_type: str, entity_id: str, action: str, message: str, actor: str, source: str = "api"):
    cur.execute(
        """
        INSERT INTO dashboard_activity_events (
            entity_type, entity_id, action, message, actor, occurred_at, source
        ) VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """,
        (entity_type, entity_id, action, message, actor, _normalize_source(source)),
    )


def _ensure_db_objects():
    global _DB_READY
    if _DB_READY:
        return

    ddl = [
        """
        CREATE TABLE IF NOT EXISTS dashboard_tickets (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'Project Management',
            priority TEXT NOT NULL DEFAULT 'medium',
            effort TEXT NOT NULL DEFAULT 'm',
            status TEXT NOT NULL DEFAULT 'todo',
            assignee TEXT NOT NULL DEFAULT 'Unassigned',
            sprint_code TEXT NOT NULL DEFAULT 'TBD',
            due_date DATE NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_subtasks (
            id TEXT PRIMARY KEY,
            ticket_id TEXT NOT NULL REFERENCES dashboard_tickets(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            source_type TEXT NOT NULL DEFAULT 'board',
            sequence INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_task_details (
            subtask_id TEXT PRIMARY KEY REFERENCES dashboard_subtasks(id) ON DELETE CASCADE,
            resolution TEXT,
            detail_date DATE,
            detail_timestamp TIMESTAMPTZ,
            status_override TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_blockers (
            id TEXT PRIMARY KEY,
            ticket_id TEXT REFERENCES dashboard_tickets(id) ON DELETE SET NULL,
            summary TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'high',
            status TEXT NOT NULL DEFAULT 'open',
            sprint_code TEXT NOT NULL DEFAULT 'TBD',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_retro_notes (
            sprint_code TEXT PRIMARY KEY,
            went_well TEXT DEFAULT '',
            did_not_go_well TEXT DEFAULT '',
            improvements TEXT DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_dod_criteria (
            id TEXT PRIMARY KEY,
            sprint_code TEXT NOT NULL,
            criterion TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            sequence INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_hours_entries (
            week_num INTEGER PRIMARY KEY,
            date_range_label TEXT,
            sprint_code TEXT NOT NULL DEFAULT 'TBD',
            hours NUMERIC(8,2) NOT NULL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_risk_entries (
            id TEXT PRIMARY KEY,
            risk TEXT NOT NULL,
            likelihood TEXT NOT NULL DEFAULT 'M',
            impact TEXT NOT NULL DEFAULT 'M',
            mitigation TEXT DEFAULT '',
            sprint_code TEXT NOT NULL DEFAULT 'TBD',
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_decision_entries (
            id TEXT PRIMARY KEY,
            date_label TEXT,
            sprint_code TEXT NOT NULL DEFAULT 'TBD',
            title TEXT NOT NULL,
            chosen TEXT DEFAULT '',
            considered TEXT DEFAULT '',
            rationale TEXT DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_by TEXT NOT NULL DEFAULT 'system',
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_activity_events (
            id BIGSERIAL PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            action TEXT NOT NULL,
            message TEXT NOT NULL,
            actor TEXT NOT NULL,
            occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dashboard_ticket_comments (
            id BIGSERIAL PRIMARY KEY,
            ticket_id TEXT NOT NULL REFERENCES dashboard_tickets(id) ON DELETE CASCADE,
            comment_text TEXT NOT NULL,
            actor TEXT NOT NULL DEFAULT 'system',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            source TEXT NOT NULL DEFAULT 'api'
        )
        """,
    ]

    with _connect() as conn:
        with conn.cursor() as cur:
            for stmt in ddl:
                cur.execute(stmt)
    _DB_READY = True


def _get_actor_and_source(payload: Dict[str, Any]) -> tuple[str, str]:
    actor = str(payload.get("updated_by") or payload.get("actor") or "system")
    source = _normalize_source(payload.get("source"))
    return actor, source


@dashboard_bp.route("/health", methods=["GET"])
def dashboard_health():
    try:
        _ensure_db_objects()
        return _json_ok({"status": "healthy", "db_ready": True})
    except Exception as exc:
        return _json_error(f"dashboard api unavailable: {exc}", 500)


@dashboard_bp.route("/tickets", methods=["GET"])
def list_tickets():
    try:
        _ensure_db_objects()
        sprint_code = _normalize_sprint(request.args.get("sprint")) if request.args.get("sprint") else None
        status = _normalize_status(request.args.get("status")) if request.args.get("status") else None
        assignee = request.args.get("assignee")

        where = []
        params: List[Any] = []
        if sprint_code:
            where.append("sprint_code = %s")
            params.append(sprint_code)
        if status:
            where.append("status = %s")
            params.append(status)
        if assignee:
            where.append("assignee = %s")
            params.append(assignee)

        sql = "SELECT * FROM dashboard_tickets"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY updated_at DESC, id"

        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                rows = _fetch_all(cur, sql, tuple(params))
        return _json_ok({"items": rows, "count": len(rows)})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/tickets/<ticket_id>", methods=["GET"])
def get_ticket(ticket_id: str):
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                row = _fetch_one(cur, "SELECT * FROM dashboard_tickets WHERE id = %s", (ticket_id,))
        if not row:
            return _json_error("ticket not found", 404)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/tickets", methods=["POST"])
def create_ticket():
    payload = request.get_json(silent=True) or {}
    ticket_id = str(payload.get("id") or "").strip()
    title = str(payload.get("title") or payload.get("feature") or "").strip()
    if not ticket_id:
        return _json_error("id is required")
    if not title:
        return _json_error("title is required")

    actor, source = _get_actor_and_source(payload)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO dashboard_tickets (
                        id, title, description, category, priority, effort, status,
                        assignee, sprint_code, due_date, created_at, updated_at,
                        updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, NOW(), NOW(),
                        %s, %s
                    )
                    RETURNING *
                    """,
                    (
                        ticket_id,
                        title,
                        str(payload.get("description") or ""),
                        str(payload.get("category") or payload.get("cat") or "Project Management"),
                        _normalize_priority(payload.get("priority") or payload.get("pri")),
                        _normalize_effort(payload.get("effort")),
                        _normalize_status(payload.get("status")),
                        str(payload.get("assignee") or "Unassigned"),
                        _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")),
                        payload.get("due_date") or payload.get("dueDate"),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "ticket", ticket_id, "create", "Ticket created", actor, source)
        return _json_ok(row, 201)
    except psycopg2.errors.UniqueViolation:
        return _json_error("ticket id already exists", 409)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/tickets/<ticket_id>", methods=["PUT"])
def update_ticket(ticket_id: str):
    payload = request.get_json(silent=True) or {}
    actor, source = _get_actor_and_source(payload)
    try:
        _ensure_db_objects()
        fields = {
            "title": payload.get("title") or payload.get("feature"),
            "description": payload.get("description"),
            "category": payload.get("category") or payload.get("cat"),
            "priority": _normalize_priority(payload.get("priority") or payload.get("pri")) if (payload.get("priority") or payload.get("pri")) is not None else None,
            "effort": _normalize_effort(payload.get("effort")) if payload.get("effort") is not None else None,
            "status": _normalize_status(payload.get("status")) if payload.get("status") is not None else None,
            "assignee": payload.get("assignee"),
            "sprint_code": _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")) if (payload.get("sprint_code") is not None or payload.get("sprint") is not None) else None,
            "due_date": payload.get("due_date") if payload.get("due_date") is not None else payload.get("dueDate"),
        }
        set_parts = []
        values: List[Any] = []
        for key, value in fields.items():
            if value is None:
                continue
            set_parts.append(f"{key} = %s")
            values.append(value)
        set_parts.extend(["updated_at = NOW()", "updated_by = %s", "source = %s"])
        values.extend([actor, source, ticket_id])

        if not set_parts:
            return _json_error("no updatable fields supplied")

        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"UPDATE dashboard_tickets SET {', '.join(set_parts)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
                if not row:
                    return _json_error("ticket not found", 404)
                row = _serialize_row(row)
                _record_event(cur, "ticket", ticket_id, "update", "Ticket updated", actor, source)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/tickets/<ticket_id>/comments", methods=["GET"])
def list_ticket_comments(ticket_id: str):
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                ticket = _fetch_one(cur, "SELECT id FROM dashboard_tickets WHERE id = %s", (ticket_id,))
                if not ticket:
                    return _json_error("ticket not found", 404)
                rows = _fetch_all(
                    cur,
                    """
                    SELECT id, ticket_id, comment_text, actor, created_at, source
                    FROM dashboard_ticket_comments
                    WHERE ticket_id = %s
                    ORDER BY created_at DESC, id DESC
                    """,
                    (ticket_id,),
                )
        return _json_ok({"items": rows, "count": len(rows)})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/tickets/<ticket_id>/comments", methods=["POST"])
def create_ticket_comment(ticket_id: str):
    payload = request.get_json(silent=True) or {}
    comment_text = str(payload.get("comment_text") or payload.get("text") or "").strip()
    if not comment_text:
        return _json_error("comment_text is required")
    actor, source = _get_actor_and_source(payload)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                ticket = _fetch_one(cur, "SELECT id FROM dashboard_tickets WHERE id = %s", (ticket_id,))
                if not ticket:
                    return _json_error("ticket not found", 404)
                cur.execute(
                    """
                    INSERT INTO dashboard_ticket_comments (
                        ticket_id, comment_text, actor, created_at, source
                    ) VALUES (%s, %s, %s, NOW(), %s)
                    RETURNING id, ticket_id, comment_text, actor, created_at, source
                    """,
                    (ticket_id, comment_text, actor, source),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "ticket", ticket_id, "comment", "Ticket comment added", actor, source)
        return _json_ok(row, 201)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/tickets/<ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id: str):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_tickets WHERE id = %s RETURNING id", (ticket_id,))
                row = cur.fetchone()
                if not row:
                    return _json_error("ticket not found", 404)
                _record_event(cur, "ticket", ticket_id, "delete", "Ticket deleted", str(actor), source)
        return _json_ok({"id": ticket_id, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/subtasks", methods=["GET"])
def list_subtasks():
    try:
        _ensure_db_objects()
        ticket_id = request.args.get("ticket_id")
        params: tuple = ()
        query = "SELECT * FROM dashboard_subtasks"
        if ticket_id:
            query += " WHERE ticket_id = %s"
            params = (ticket_id,)
        query += " ORDER BY ticket_id, sequence, id"
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                rows = _fetch_all(cur, query, params)
        return _json_ok({"items": rows, "count": len(rows)})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/subtasks", methods=["POST"])
def create_subtask():
    payload = request.get_json(silent=True) or {}
    subtask_id = str(payload.get("id") or "").strip()
    ticket_id = str(payload.get("ticket_id") or "").strip()
    title = str(payload.get("title") or "").strip()
    if not subtask_id or not ticket_id or not title:
        return _json_error("id, ticket_id, and title are required")

    actor, source = _get_actor_and_source(payload)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO dashboard_subtasks (
                        id, ticket_id, title, status, source_type, sequence,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    ) RETURNING *
                    """,
                    (
                        subtask_id,
                        ticket_id,
                        title,
                        _normalize_status(payload.get("status")),
                        str(payload.get("source_type") or payload.get("sourceType") or "board"),
                        int(payload.get("sequence") or 0),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "subtask", subtask_id, "create", "Subtask created", actor, source)
        return _json_ok(row, 201)
    except psycopg2.errors.ForeignKeyViolation:
        return _json_error("ticket_id does not exist", 400)
    except psycopg2.errors.UniqueViolation:
        return _json_error("subtask id already exists", 409)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/subtasks/<subtask_id>/status", methods=["PUT"])
def update_subtask_status(subtask_id: str):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status is None:
        return _json_error("status is required")
    actor, source = _get_actor_and_source(payload)
    normalized = _normalize_status(status)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    UPDATE dashboard_subtasks
                    SET status = %s, updated_at = NOW(), updated_by = %s, source = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (normalized, actor, source, subtask_id),
                )
                row = cur.fetchone()
                if not row:
                    return _json_error("subtask not found", 404)
                row = _serialize_row(row)
                _record_event(cur, "subtask", subtask_id, "status_transition", f"Subtask status set to {normalized}", actor, source)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/subtasks/<subtask_id>", methods=["DELETE"])
def delete_subtask(subtask_id: str):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_subtasks WHERE id = %s RETURNING id", (subtask_id,))
                row = cur.fetchone()
                if not row:
                    return _json_error("subtask not found", 404)
                _record_event(cur, "subtask", subtask_id, "delete", "Subtask deleted", str(actor), source)
        return _json_ok({"id": subtask_id, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/task-details/<subtask_id>", methods=["GET"])
def get_task_detail(subtask_id: str):
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                row = _fetch_one(cur, "SELECT * FROM dashboard_task_details WHERE subtask_id = %s", (subtask_id,))
        if not row:
            return _json_error("task detail not found", 404)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/task-details/<subtask_id>", methods=["PUT"])
def upsert_task_detail(subtask_id: str):
    payload = request.get_json(silent=True) or {}
    actor, source = _get_actor_and_source(payload)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO dashboard_task_details (
                        subtask_id, resolution, detail_date, detail_timestamp, status_override,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    )
                    ON CONFLICT (subtask_id)
                    DO UPDATE SET
                        resolution = EXCLUDED.resolution,
                        detail_date = EXCLUDED.detail_date,
                        detail_timestamp = EXCLUDED.detail_timestamp,
                        status_override = EXCLUDED.status_override,
                        updated_at = NOW(),
                        updated_by = EXCLUDED.updated_by,
                        source = EXCLUDED.source
                    RETURNING *
                    """,
                    (
                        subtask_id,
                        payload.get("resolution"),
                        payload.get("detail_date") or payload.get("date"),
                        payload.get("detail_timestamp") or payload.get("timestamp"),
                        _normalize_status(payload.get("status_override")) if payload.get("status_override") is not None else None,
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "task_detail", subtask_id, "upsert", "Task detail updated", actor, source)
        return _json_ok(row)
    except psycopg2.errors.ForeignKeyViolation:
        return _json_error("subtask does not exist", 400)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/blockers", methods=["GET"])
def list_blockers():
    try:
        _ensure_db_objects()
        sprint_code = request.args.get("sprint_code")
        status = request.args.get("status")
        query = "SELECT * FROM dashboard_blockers"
        params: List[Any] = []
        clauses: List[str] = []
        if sprint_code:
            clauses.append("sprint_code = %s")
            params.append(_normalize_sprint(sprint_code))
        if status:
            clauses.append("status = %s")
            params.append(str(status).strip().lower())
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY updated_at DESC, id"
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                rows = _fetch_all(cur, query, tuple(params))
        return _json_ok({"items": rows, "count": len(rows)})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/blockers", methods=["POST"])
def create_blocker():
    payload = request.get_json(silent=True) or {}
    blocker_id = str(payload.get("id") or "").strip()
    summary = str(payload.get("summary") or "").strip()
    if not blocker_id or not summary:
        return _json_error("id and summary are required")
    actor, source = _get_actor_and_source(payload)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO dashboard_blockers (
                        id, ticket_id, summary, severity, status, sprint_code,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    ) RETURNING *
                    """,
                    (
                        blocker_id,
                        payload.get("ticket_id"),
                        summary,
                        str(payload.get("severity") or "high").strip().lower(),
                        str(payload.get("status") or "open").strip().lower(),
                        _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "blocker", blocker_id, "create", "Blocker created", actor, source)
        return _json_ok(row, 201)
    except psycopg2.errors.UniqueViolation:
        return _json_error("blocker id already exists", 409)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/blockers/<blocker_id>", methods=["PUT"])
def update_blocker(blocker_id: str):
    payload = request.get_json(silent=True) or {}
    actor, source = _get_actor_and_source(payload)
    fields = {
        "ticket_id": payload.get("ticket_id"),
        "summary": payload.get("summary"),
        "severity": str(payload.get("severity")).strip().lower() if payload.get("severity") is not None else None,
        "status": str(payload.get("status")).strip().lower() if payload.get("status") is not None else None,
        "sprint_code": _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")) if (payload.get("sprint_code") is not None or payload.get("sprint") is not None) else None,
    }
    set_parts = []
    values: List[Any] = []
    for key, value in fields.items():
        if value is None:
            continue
        set_parts.append(f"{key} = %s")
        values.append(value)
    if not set_parts:
        return _json_error("no updatable fields supplied")
    set_parts.extend(["updated_at = NOW()", "updated_by = %s", "source = %s"])
    values.extend([actor, source, blocker_id])
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"UPDATE dashboard_blockers SET {', '.join(set_parts)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
                if not row:
                    return _json_error("blocker not found", 404)
                row = _serialize_row(row)
                _record_event(cur, "blocker", blocker_id, "update", "Blocker updated", actor, source)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/blockers/<blocker_id>", methods=["DELETE"])
def delete_blocker(blocker_id: str):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_blockers WHERE id = %s RETURNING id", (blocker_id,))
                row = cur.fetchone()
                if not row:
                    return _json_error("blocker not found", 404)
                _record_event(cur, "blocker", blocker_id, "delete", "Blocker deleted", str(actor), source)
        return _json_ok({"id": blocker_id, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/retro/<sprint_code>", methods=["GET", "PUT"])
def retro_notes(sprint_code: str):
    normalized = _normalize_sprint(sprint_code)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if request.method == "GET":
                    row = _fetch_one(cur, "SELECT * FROM dashboard_retro_notes WHERE sprint_code = %s", (normalized,))
                    if not row:
                        return _json_ok({
                            "sprint_code": normalized,
                            "went_well": "",
                            "did_not_go_well": "",
                            "improvements": "",
                        })
                    return _json_ok(row)

                payload = request.get_json(silent=True) or {}
                actor, source = _get_actor_and_source(payload)
                cur.execute(
                    """
                    INSERT INTO dashboard_retro_notes (
                        sprint_code, went_well, did_not_go_well, improvements,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    )
                    ON CONFLICT (sprint_code)
                    DO UPDATE SET
                        went_well = EXCLUDED.went_well,
                        did_not_go_well = EXCLUDED.did_not_go_well,
                        improvements = EXCLUDED.improvements,
                        updated_at = NOW(),
                        updated_by = EXCLUDED.updated_by,
                        source = EXCLUDED.source
                    RETURNING *
                    """,
                    (
                        normalized,
                        str(payload.get("went_well") or ""),
                        str(payload.get("did_not_go_well") or ""),
                        str(payload.get("improvements") or ""),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "retro", normalized, "upsert", "Retro notes updated", actor, source)
                return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/retro/<sprint_code>", methods=["DELETE"])
def delete_retro_notes(sprint_code: str):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    normalized = _normalize_sprint(sprint_code)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_retro_notes WHERE sprint_code = %s RETURNING sprint_code", (normalized,))
                row = cur.fetchone()
                if not row:
                    return _json_error("retro notes not found", 404)
                _record_event(cur, "retro", normalized, "delete", "Retro notes deleted", str(actor), source)
        return _json_ok({"sprint_code": normalized, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/dod", methods=["GET", "POST"])
def dod_collection():
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if request.method == "GET":
                    sprint_code = request.args.get("sprint_code")
                    if sprint_code:
                        rows = _fetch_all(
                            cur,
                            "SELECT * FROM dashboard_dod_criteria WHERE sprint_code = %s ORDER BY sequence, id",
                            (_normalize_sprint(sprint_code),),
                        )
                    else:
                        rows = _fetch_all(cur, "SELECT * FROM dashboard_dod_criteria ORDER BY sprint_code, sequence, id")
                    return _json_ok({"items": rows, "count": len(rows)})

                payload = request.get_json(silent=True) or {}
                criterion_id = str(payload.get("id") or "").strip()
                if not criterion_id:
                    return _json_error("id is required")
                criterion = str(payload.get("criterion") or "").strip()
                if not criterion:
                    return _json_error("criterion is required")
                actor, source = _get_actor_and_source(payload)
                cur.execute(
                    """
                    INSERT INTO dashboard_dod_criteria (
                        id, sprint_code, criterion, status, sequence,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    ) RETURNING *
                    """,
                    (
                        criterion_id,
                        _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")),
                        criterion,
                        _normalize_status(payload.get("status")),
                        int(payload.get("sequence") or 0),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "dod", criterion_id, "create", "DoD criterion created", actor, source)
                return _json_ok(row, 201)
    except psycopg2.errors.UniqueViolation:
        return _json_error("dod criterion id already exists", 409)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/dod/<criterion_id>", methods=["PUT"])
def update_dod(criterion_id: str):
    payload = request.get_json(silent=True) or {}
    actor, source = _get_actor_and_source(payload)
    fields = {
        "sprint_code": _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")) if (payload.get("sprint_code") is not None or payload.get("sprint") is not None) else None,
        "criterion": payload.get("criterion"),
        "status": _normalize_status(payload.get("status")) if payload.get("status") is not None else None,
        "sequence": int(payload.get("sequence")) if payload.get("sequence") is not None else None,
    }
    set_parts = []
    values: List[Any] = []
    for key, value in fields.items():
        if value is None:
            continue
        set_parts.append(f"{key} = %s")
        values.append(value)
    if not set_parts:
        return _json_error("no updatable fields supplied")
    set_parts.extend(["updated_at = NOW()", "updated_by = %s", "source = %s"])
    values.extend([actor, source, criterion_id])
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"UPDATE dashboard_dod_criteria SET {', '.join(set_parts)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
                if not row:
                    return _json_error("dod criterion not found", 404)
                row = _serialize_row(row)
                _record_event(cur, "dod", criterion_id, "update", "DoD criterion updated", actor, source)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/dod/<criterion_id>", methods=["DELETE"])
def delete_dod(criterion_id: str):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_dod_criteria WHERE id = %s RETURNING id", (criterion_id,))
                row = cur.fetchone()
                if not row:
                    return _json_error("dod criterion not found", 404)
                _record_event(cur, "dod", criterion_id, "delete", "DoD criterion deleted", str(actor), source)
        return _json_ok({"id": criterion_id, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/hours", methods=["GET"])
def list_hours():
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                rows = _fetch_all(cur, "SELECT * FROM dashboard_hours_entries ORDER BY week_num")
        return _json_ok({"items": rows, "count": len(rows)})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/hours/<int:week_num>", methods=["PUT"])
def upsert_hours(week_num: int):
    payload = request.get_json(silent=True) or {}
    actor, source = _get_actor_and_source(payload)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO dashboard_hours_entries (
                        week_num, date_range_label, sprint_code, hours, notes,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    )
                    ON CONFLICT (week_num)
                    DO UPDATE SET
                        date_range_label = EXCLUDED.date_range_label,
                        sprint_code = EXCLUDED.sprint_code,
                        hours = EXCLUDED.hours,
                        notes = EXCLUDED.notes,
                        updated_at = NOW(),
                        updated_by = EXCLUDED.updated_by,
                        source = EXCLUDED.source
                    RETURNING *
                    """,
                    (
                        week_num,
                        payload.get("date_range_label") or payload.get("dates"),
                        _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")),
                        payload.get("hours") or 0,
                        str(payload.get("notes") or ""),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "hours", str(week_num), "upsert", "Hours entry updated", actor, source)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/hours/<int:week_num>", methods=["DELETE"])
def delete_hours(week_num: int):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_hours_entries WHERE week_num = %s RETURNING week_num", (week_num,))
                row = cur.fetchone()
                if not row:
                    return _json_error("hours entry not found", 404)
                _record_event(cur, "hours", str(week_num), "delete", "Hours entry deleted", str(actor), source)
        return _json_ok({"week_num": week_num, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/risks", methods=["GET", "POST"])
def risks_collection():
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if request.method == "GET":
                    rows = _fetch_all(cur, "SELECT * FROM dashboard_risk_entries ORDER BY id")
                    return _json_ok({"items": rows, "count": len(rows)})

                payload = request.get_json(silent=True) or {}
                risk_id = str(payload.get("id") or "").strip()
                if not risk_id:
                    return _json_error("id is required")
                risk_text = str(payload.get("risk") or "").strip()
                if not risk_text:
                    return _json_error("risk is required")
                actor, source = _get_actor_and_source(payload)
                cur.execute(
                    """
                    INSERT INTO dashboard_risk_entries (
                        id, risk, likelihood, impact, mitigation, sprint_code, status,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    ) RETURNING *
                    """,
                    (
                        risk_id,
                        risk_text,
                        str(payload.get("likelihood") or payload.get("like") or "M").upper(),
                        str(payload.get("impact") or "M").upper(),
                        str(payload.get("mitigation") or ""),
                        _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")),
                        str(payload.get("status") or "open").strip().lower(),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "risk", risk_id, "create", "Risk entry created", actor, source)
                return _json_ok(row, 201)
    except psycopg2.errors.UniqueViolation:
        return _json_error("risk id already exists", 409)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/risks/<risk_id>", methods=["PUT"])
def update_risk(risk_id: str):
    payload = request.get_json(silent=True) or {}
    actor, source = _get_actor_and_source(payload)
    fields = {
        "risk": payload.get("risk"),
        "likelihood": str(payload.get("likelihood") or payload.get("like")).upper() if (payload.get("likelihood") is not None or payload.get("like") is not None) else None,
        "impact": str(payload.get("impact")).upper() if payload.get("impact") is not None else None,
        "mitigation": payload.get("mitigation"),
        "sprint_code": _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")) if (payload.get("sprint_code") is not None or payload.get("sprint") is not None) else None,
        "status": str(payload.get("status")).strip().lower() if payload.get("status") is not None else None,
    }
    set_parts = []
    values: List[Any] = []
    for key, value in fields.items():
        if value is None:
            continue
        set_parts.append(f"{key} = %s")
        values.append(value)
    if not set_parts:
        return _json_error("no updatable fields supplied")
    set_parts.extend(["updated_at = NOW()", "updated_by = %s", "source = %s"])
    values.extend([actor, source, risk_id])
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"UPDATE dashboard_risk_entries SET {', '.join(set_parts)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
                if not row:
                    return _json_error("risk not found", 404)
                row = _serialize_row(row)
                _record_event(cur, "risk", risk_id, "update", "Risk entry updated", actor, source)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/risks/<risk_id>", methods=["DELETE"])
def delete_risk(risk_id: str):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_risk_entries WHERE id = %s RETURNING id", (risk_id,))
                row = cur.fetchone()
                if not row:
                    return _json_error("risk not found", 404)
                _record_event(cur, "risk", risk_id, "delete", "Risk entry deleted", str(actor), source)
        return _json_ok({"id": risk_id, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/decisions", methods=["GET", "POST"])
def decisions_collection():
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if request.method == "GET":
                    rows = _fetch_all(cur, "SELECT * FROM dashboard_decision_entries ORDER BY id")
                    return _json_ok({"items": rows, "count": len(rows)})

                payload = request.get_json(silent=True) or {}
                decision_id = str(payload.get("id") or "").strip()
                title = str(payload.get("title") or "").strip()
                if not decision_id or not title:
                    return _json_error("id and title are required")
                actor, source = _get_actor_and_source(payload)
                cur.execute(
                    """
                    INSERT INTO dashboard_decision_entries (
                        id, date_label, sprint_code, title, chosen, considered, rationale,
                        created_at, updated_at, updated_by, source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        NOW(), NOW(), %s, %s
                    ) RETURNING *
                    """,
                    (
                        decision_id,
                        str(payload.get("date_label") or payload.get("date") or ""),
                        _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")),
                        title,
                        str(payload.get("chosen") or ""),
                        str(payload.get("considered") or ""),
                        str(payload.get("rationale") or payload.get("why") or ""),
                        actor,
                        source,
                    ),
                )
                row = _serialize_row(cur.fetchone())
                _record_event(cur, "decision", decision_id, "create", "Decision entry created", actor, source)
                return _json_ok(row, 201)
    except psycopg2.errors.UniqueViolation:
        return _json_error("decision id already exists", 409)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/decisions/<decision_id>", methods=["PUT"])
def update_decision(decision_id: str):
    payload = request.get_json(silent=True) or {}
    actor, source = _get_actor_and_source(payload)
    fields = {
        "date_label": payload.get("date_label") if payload.get("date_label") is not None else payload.get("date"),
        "sprint_code": _normalize_sprint(payload.get("sprint_code") or payload.get("sprint")) if (payload.get("sprint_code") is not None or payload.get("sprint") is not None) else None,
        "title": payload.get("title"),
        "chosen": payload.get("chosen"),
        "considered": payload.get("considered"),
        "rationale": payload.get("rationale") if payload.get("rationale") is not None else payload.get("why"),
    }
    set_parts = []
    values: List[Any] = []
    for key, value in fields.items():
        if value is None:
            continue
        set_parts.append(f"{key} = %s")
        values.append(value)
    if not set_parts:
        return _json_error("no updatable fields supplied")
    set_parts.extend(["updated_at = NOW()", "updated_by = %s", "source = %s"])
    values.extend([actor, source, decision_id])
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    f"UPDATE dashboard_decision_entries SET {', '.join(set_parts)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
                if not row:
                    return _json_error("decision not found", 404)
                row = _serialize_row(row)
                _record_event(cur, "decision", decision_id, "update", "Decision entry updated", actor, source)
        return _json_ok(row)
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/decisions/<decision_id>", methods=["DELETE"])
def delete_decision(decision_id: str):
    actor = request.args.get("actor", "system")
    source = _normalize_source(request.args.get("source", "api"))
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("DELETE FROM dashboard_decision_entries WHERE id = %s RETURNING id", (decision_id,))
                row = cur.fetchone()
                if not row:
                    return _json_error("decision not found", 404)
                _record_event(cur, "decision", decision_id, "delete", "Decision entry deleted", str(actor), source)
        return _json_ok({"id": decision_id, "deleted": True})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/events", methods=["GET"])
def list_events():
    try:
        _ensure_db_objects()
        limit = int(request.args.get("limit") or 200)
        if limit < 1:
            limit = 1
        if limit > 1000:
            limit = 1000
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                rows = _fetch_all(
                    cur,
                    "SELECT * FROM dashboard_activity_events ORDER BY occurred_at DESC, id DESC LIMIT %s",
                    (limit,),
                )
        return _json_ok({"items": rows, "count": len(rows)})
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/aggregates/overview", methods=["GET"])
def aggregates_overview():
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                ticket_counts = _fetch_one(
                    cur,
                    """
                    SELECT
                        COUNT(*)::INT AS total,
                        SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END)::INT AS todo,
                        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END)::INT AS in_progress,
                        SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END)::INT AS blocked,
                        SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END)::INT AS done
                    FROM dashboard_tickets
                    """,
                )
                subtask_counts = _fetch_one(
                    cur,
                    """
                    SELECT
                        COUNT(*)::INT AS total,
                        SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END)::INT AS todo,
                        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END)::INT AS in_progress,
                        SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END)::INT AS blocked,
                        SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END)::INT AS done
                    FROM dashboard_subtasks
                    """,
                )
                open_blockers = _fetch_one(
                    cur,
                    "SELECT COUNT(*)::INT AS count FROM dashboard_blockers WHERE status = 'open'",
                )
                hours_total = _fetch_one(
                    cur,
                    "SELECT COALESCE(SUM(hours), 0)::NUMERIC(10,2) AS total_hours FROM dashboard_hours_entries",
                )

        return _json_ok(
            {
                "tickets": ticket_counts,
                "subtasks": subtask_counts,
                "open_blockers": open_blockers["count"] if open_blockers else 0,
                "total_hours": hours_total["total_hours"] if hours_total else 0,
            }
        )
    except Exception as exc:
        return _json_error(str(exc), 500)


@dashboard_bp.route("/aggregates/sprint/<sprint_code>", methods=["GET"])
def aggregates_by_sprint(sprint_code: str):
    normalized = _normalize_sprint(sprint_code)
    try:
        _ensure_db_objects()
        with _connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                ticket_counts = _fetch_one(
                    cur,
                    """
                    SELECT
                        COUNT(*)::INT AS total,
                        SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END)::INT AS todo,
                        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END)::INT AS in_progress,
                        SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END)::INT AS blocked,
                        SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END)::INT AS done
                    FROM dashboard_tickets
                    WHERE sprint_code = %s
                    """,
                    (normalized,),
                )
                subtask_counts = _fetch_one(
                    cur,
                    """
                    SELECT
                        COUNT(*)::INT AS total,
                        SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END)::INT AS todo,
                        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END)::INT AS in_progress,
                        SUM(CASE WHEN status = 'blocked' THEN 1 ELSE 0 END)::INT AS blocked,
                        SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END)::INT AS done
                    FROM dashboard_subtasks
                    WHERE ticket_id IN (
                        SELECT id FROM dashboard_tickets WHERE sprint_code = %s
                    )
                    """,
                    (normalized,),
                )
                blockers = _fetch_one(
                    cur,
                    """
                    SELECT
                        COUNT(*)::INT AS total,
                        SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END)::INT AS open
                    FROM dashboard_blockers
                    WHERE sprint_code = %s
                    """,
                    (normalized,),
                )
                hours = _fetch_one(
                    cur,
                    "SELECT COALESCE(SUM(hours), 0)::NUMERIC(10,2) AS total_hours FROM dashboard_hours_entries WHERE sprint_code = %s",
                    (normalized,),
                )

        return _json_ok(
            {
                "sprint_code": normalized,
                "tickets": ticket_counts,
                "subtasks": subtask_counts,
                "blockers": blockers,
                "total_hours": hours["total_hours"] if hours else 0,
            }
        )
    except Exception as exc:
        return _json_error(str(exc), 500)


def register_dashboard_routes(app):
    """Register dashboard routes and ensure DB objects exist.

    This is imported by `api_server.py` during startup.
    """

    try:
        _ensure_db_objects()
    except Exception as exc:
        app.logger.warning(f"Dashboard API bootstrap deferred: {exc}")
    app.register_blueprint(dashboard_bp)
