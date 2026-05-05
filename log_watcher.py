"""
log_watcher.py — H.C. Lombardo NFL Analytics
Watches repo for file changes. Writes daily archive files and serves the
logbook page locally so the browser can fetch live data via HTTP.

Archive structure:
  docs/devlog/archive/YYYY-MM-DD.json  — one file per day
  docs/devlog/archive/index.json       — list of all available dates

Served at http://localhost:8765/ so fetch() works in the browser.
Started automatically by START-DEV.bat.
"""
import http.server
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

REPO         = Path("c:/ReactGitEC2/IS330/H.C Lombardo App")
ARCHIVE_DIR  = REPO / "docs" / "devlog" / "archive"
SERVE_DIR    = REPO / "docs" / "devlog"
PORT         = 8765
MAX_PER_DAY  = 2000  # max entries per daily file before rolling
EVENT_DEBOUNCE_SECONDS = 0.35

WATCH_EXTS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css',
    '.json', '.sql', '.md', '.txt', '.bat', '.sh', '.yml', '.yaml'
}

# Never track these — noise with no signal
IGNORE_NAMES = {
    'node_modules', '.git', '__pycache__', 'build', 'dist',
    'live.json', 'index.json', 'CLAUDE_SESSION_BRIEF.md'
}

_io_lock = threading.Lock()
_event_lock = threading.Lock()
_last_event_at = {}


def _safe_resolve(path_like):
    return Path(path_like).resolve(strict=False)


def _is_relative_to(path_obj, parent_obj):
    try:
        path_obj.relative_to(parent_obj)
        return True
    except ValueError:
        return False


def should_track(path_str):
    p = _safe_resolve(path_str)
    if not _is_relative_to(p, _safe_resolve(REPO)):
        return False
    # Never record writes to the devlog archive itself; that causes recursion.
    if _is_relative_to(p, _safe_resolve(ARCHIVE_DIR)):
        return False
    for part in p.parts:
        if part in IGNORE_NAMES:
            return False
    if p.name.startswith('.'):
        return False
    return p.suffix.lower() in WATCH_EXTS


def should_emit_event(event_type, path_str):
    now = time.time()
    key = (event_type, str(_safe_resolve(path_str)).lower())
    with _event_lock:
        last = _last_event_at.get(key)
        if last is not None and (now - last) < EVENT_DEBOUNCE_SECONDS:
            return False
        _last_event_at[key] = now
        return True


def today():
    return datetime.now().strftime('%Y-%m-%d')


def archive_path(date_str=None):
    return ARCHIVE_DIR / f"{date_str or today()}.json"


def load_day(date_str=None):
    p = archive_path(date_str)
    if p.exists():
        try:
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_day(entries, date_str=None):
    if len(entries) > MAX_PER_DAY:
        entries = entries[-MAX_PER_DAY:]
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with _io_lock:
        with open(archive_path(date_str), 'w', encoding='utf-8') as f:
            json.dump(entries, f, separators=(',', ':'))
        update_index()


def update_index():
    """Rebuild the index of available archive dates."""
    dates = sorted(
        p.stem for p in ARCHIVE_DIR.glob('*.json') if p.stem != 'index'
    )
    with open(ARCHIVE_DIR / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(dates, f, separators=(',', ':'))


def add_entry(event_type, path_str, extra=None):
    rel = str(_safe_resolve(path_str).relative_to(_safe_resolve(REPO))).replace('\\', '/')
    ts  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {'ts': ts, 'type': event_type, 'file': rel}
    if extra:
        entry.update(extra)
    entries = load_day()
    entries.append(entry)
    save_day(entries)
    label = event_type.upper().ljust(8)
    print(f"[{ts}] {label} {rel}")


class RepoHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if not event.is_directory and should_track(event.src_path) and should_emit_event('modified', event.src_path):
            try:
                add_entry('modified', event.src_path)
            except Exception as exc:
                print(f"[log_watcher][WARN] modified event failed: {exc}")

    def on_created(self, event):
        if not event.is_directory and should_track(event.src_path) and should_emit_event('created', event.src_path):
            try:
                add_entry('created', event.src_path)
            except Exception as exc:
                print(f"[log_watcher][WARN] created event failed: {exc}")

    def on_deleted(self, event):
        if not event.is_directory and should_track(event.src_path) and should_emit_event('deleted', event.src_path):
            try:
                add_entry('deleted', event.src_path)
            except Exception as exc:
                print(f"[log_watcher][WARN] deleted event failed: {exc}")

    def on_moved(self, event):
        if not event.is_directory:
            if (should_track(event.src_path) or should_track(event.dest_path)) and should_emit_event('renamed', event.dest_path):
                try:
                    add_entry('renamed', event.dest_path,
                              extra={'from': str(_safe_resolve(event.src_path).relative_to(_safe_resolve(REPO))).replace('\\', '/')})
                except Exception as exc:
                    print(f"[log_watcher][WARN] moved event failed: {exc}")


class CORSHandler(http.server.SimpleHTTPRequestHandler):
    """Serve docs/devlog/ with CORS + no-cache so fetch() always gets fresh data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    # Suppress per-request logs — keep the console clean
    def log_message(self, format, *args):
        pass


def start_http_server():
    server = http.server.HTTPServer(('localhost', PORT), CORSHandler)
    server.serve_forever()


if __name__ == '__main__':
    print('=' * 60)
    print('  H.C. LOMBARDO — PROJECT LOGBOOK WATCHER')
    print(f'  Watching : {REPO}')
    print(f'  Archives : {ARCHIVE_DIR}')
    print(f'  Browser  : http://localhost:{PORT}/')
    print('=' * 60)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Write startup entry
    add_entry('started', str(REPO / 'log_watcher.py'))

    # HTTP server in background thread
    threading.Thread(target=start_http_server, daemon=True).start()

    # File watcher
    handler  = RepoHandler()
    observer = Observer()
    observer.schedule(handler, str(REPO), recursive=True)
    observer.start()
    print(f'[log_watcher] Watching for changes on {today()}...')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print('\n[log_watcher] Stopped.')
    observer.join()
