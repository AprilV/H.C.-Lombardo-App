#!/usr/bin/env python3
"""Generate a full-program test coverage report from code inventory + live probes."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RouteResult:
    route: str
    status_code: int | None
    ok: bool
    error: str | None


@dataclass
class ApiResult:
    method: str
    template: str
    resolved: str | None
    status_code: int | None
    ok: bool
    skipped: bool
    skip_reason: str | None
    error: str | None


@dataclass
class FullProgramStatus:
    generated_utc: str
    frontend_base: str
    api_base: str
    route_inventory_count: int
    route_results: list[RouteResult]
    api_inventory_count: int
    api_results: list[ApiResult]
    totals: dict[str, int]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_routes(app_js: Path) -> list[str]:
    text = read_text(app_js)
    raw_routes = re.findall(r"<Route\s+path=\"([^\"]+)\"", text)
    routes: list[str] = []
    for route in raw_routes:
        if ":" in route:
            continue
        routes.append(route)
    return sorted(set(routes))


def iter_js_files(src_dir: Path) -> Iterable[Path]:
    for path in src_dir.rglob("*.js"):
        if path.is_file():
            yield path


def parse_api_templates(src_dir: Path) -> list[tuple[str, str]]:
    templates: list[tuple[str, str]] = []
    fetch_pattern = re.compile(
        r"fetch\(\s*`\$\{API_URL\}([^`]+)`(?:\s*,\s*\{(?P<opts>.*?)\})?",
        re.S,
    )

    for js_file in iter_js_files(src_dir):
        text = read_text(js_file)
        for match in fetch_pattern.finditer(text):
            suffix = match.group(1).strip()
            opts = match.group("opts") or ""
            method = "GET"
            method_match = re.search(r"method\s*:\s*['\"]([A-Z]+)['\"]", opts)
            if method_match:
                method = method_match.group(1).upper()
            templates.append((method, suffix))

    unique = sorted(set(templates), key=lambda item: (item[0], item[1]))
    return unique


def resolve_template(template: str) -> str | None:
    # Complex inline template expressions (ternaries, nested templates) are
    # intentionally skipped because they cannot be resolved safely with
    # static token substitution.
    if re.search(r"\$\{[^}]*\?", template):
        return None

    if template.count("${") != template.count("}"):
        return None

    sample_values = {
        "season": "2025",
        "selectedSeason": "2025",
        "seasonA": "2025",
        "seasonB": "2025",
        "defaultSeason": "2025",
        "week": "1",
        "selectedTeam": "KC",
        "abbr": "KC",
        "abbreviation": "KC",
        "teamAbbr": "KC",
    }

    unresolved = set(re.findall(r"\$\{([^}]+)\}", template))
    if not unresolved:
        return template

    resolved = template
    for key in list(unresolved):
        if key not in sample_values:
            return None
        resolved = resolved.replace(f"${{{key}}}", sample_values[key])

    if "${" in resolved:
        return None

    return resolved


def probe_route(frontend_base: str, route: str, timeout_seconds: float) -> RouteResult:
    url = f"{frontend_base.rstrip('/')}{route}"
    try:
        response = requests.get(url, timeout=timeout_seconds)
        status = response.status_code
        return RouteResult(route=route, status_code=status, ok=status < 400, error=None)
    except Exception as exc:  # noqa: BLE001
        return RouteResult(route=route, status_code=None, ok=False, error=str(exc))


def probe_api(
    api_base: str,
    method: str,
    template: str,
    timeout_seconds: float,
) -> ApiResult:
    resolved = resolve_template(template)
    if method != "GET":
        return ApiResult(
            method=method,
            template=template,
            resolved=resolved,
            status_code=None,
            ok=False,
            skipped=True,
            skip_reason="Non-GET endpoint skipped to avoid side effects",
            error=None,
        )

    if resolved is None:
        return ApiResult(
            method=method,
            template=template,
            resolved=None,
            status_code=None,
            ok=False,
            skipped=True,
            skip_reason="Template has unresolved dynamic variables",
            error=None,
        )

    url = f"{api_base.rstrip('/')}{resolved}"
    try:
        response = requests.get(url, timeout=timeout_seconds)
        status = response.status_code
        return ApiResult(
            method=method,
            template=template,
            resolved=resolved,
            status_code=status,
            ok=status < 400,
            skipped=False,
            skip_reason=None,
            error=None,
        )
    except Exception as exc:  # noqa: BLE001
        return ApiResult(
            method=method,
            template=template,
            resolved=resolved,
            status_code=None,
            ok=False,
            skipped=False,
            skip_reason=None,
            error=str(exc),
        )


def to_markdown(status: FullProgramStatus) -> str:
    lines: list[str] = []
    lines.append("# Full Program Test Automation Status")
    lines.append("")
    lines.append(f"Generated UTC: {status.generated_utc}")
    lines.append(f"Frontend base: {status.frontend_base}")
    lines.append(f"API base: {status.api_base}")
    lines.append("")
    lines.append("## Totals")
    for key, value in status.totals.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Route Results")
    for item in status.route_results:
        lines.append(
            "- "
            + f"route={item.route} ok={str(item.ok).lower()} "
            + f"status={item.status_code} error={item.error}"
        )
    lines.append("")
    lines.append("## API Results")
    for item in status.api_results:
        lines.append(
            "- "
            + f"method={item.method} template={item.template} resolved={item.resolved} "
            + f"ok={str(item.ok).lower()} skipped={str(item.skipped).lower()} "
            + f"status={item.status_code} skip_reason={item.skip_reason} error={item.error}"
        )
    lines.append("")
    return "\n".join(lines)


def load_api_base(repo_root: Path) -> str:
    env_prod = repo_root / "frontend/.env.production"
    if not env_prod.exists():
        return ""

    for line in read_text(env_prod).splitlines():
        raw = line.strip()
        if raw.startswith("REACT_APP_API_URL="):
            return raw.split("=", 1)[1].strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run full-program route + API inventory probes."
    )
    parser.add_argument(
        "--frontend-base",
        default="https://staging.d2fwv8daemi5y2.amplifyapp.com",
        help="Frontend base URL to probe routes.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="Timeout for HTTP probes.",
    )
    parser.add_argument(
        "--output-json",
        default="docs/sprints/ta039_release_tag/full_program_test_status_latest.json",
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--output-md",
        default="docs/sprints/ta039_release_tag/FULL_PROGRAM_TEST_AUTOSTATUS_latest.md",
        help="Output markdown report path.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    app_js = repo_root / "frontend/src/App.js"
    src_dir = repo_root / "frontend/src"

    api_base = load_api_base(repo_root)

    routes = parse_routes(app_js)
    route_results = [
        probe_route(args.frontend_base, route, args.timeout_seconds) for route in routes
    ]

    api_templates = parse_api_templates(src_dir)
    api_results = [
        probe_api(api_base, method, template, args.timeout_seconds)
        for method, template in api_templates
    ]

    totals = {
        "route_inventory_count": len(routes),
        "route_pass": sum(1 for item in route_results if item.ok),
        "route_fail": sum(1 for item in route_results if not item.ok),
        "api_inventory_count": len(api_templates),
        "api_pass": sum(1 for item in api_results if item.ok and not item.skipped),
        "api_fail": sum(1 for item in api_results if (not item.ok) and (not item.skipped)),
        "api_skipped": sum(1 for item in api_results if item.skipped),
    }

    status = FullProgramStatus(
        generated_utc=utc_now(),
        frontend_base=args.frontend_base,
        api_base=api_base,
        route_inventory_count=len(routes),
        route_results=route_results,
        api_inventory_count=len(api_templates),
        api_results=api_results,
        totals=totals,
    )

    out_json = repo_root / args.output_json
    out_md = repo_root / args.output_md
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    out_md.write_text(to_markdown(status), encoding="utf-8")

    print(json.dumps(asdict(status), ensure_ascii=True))

    overall_ok = totals["route_fail"] == 0 and totals["api_fail"] == 0
    return 0 if overall_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
