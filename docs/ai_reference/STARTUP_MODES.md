# H.C. Lombardo - Startup Guide

Last Updated: May 14, 2026

## Primary Start/Stop Commands (Canonical)

Use these commands from project root:

```powershell
python startup.py
python shutdown.py
```

These are the authoritative local control commands.

---

## Launch Options

### 1) `startup.py` (recommended default)

- Starts Flask API on port 5000
- Starts React dev server on port 3000
- Starts live data updater
- Starts dev log watcher on port 8765
- Opens browser to `http://localhost:3000`

### 2) `START-DEV.bat` (convenience wrapper)

- Convenience launcher for development workflow
- Uses the same dev ports: 3000 (React), 5000 (API), 8765 (log watcher)
- Stop with either `STOP.bat` or `python shutdown.py`

### 3) `START.bat` (production-like local run)

- Builds React production bundle
- Serves frontend + API through Flask on port 5000
- No hot reload
- Best for demo/performance validation

---

## Quick Comparison

| Feature | `startup.py` | `START-DEV.bat` | `START.bat` |
|---------|---------------|------------------|-------------|
| Startup type | Python orchestrator | Dev wrapper | Production-like wrapper |
| Ports | 3000, 5000, 8765 | 3000, 5000, 8765 | 5000 |
| Hot reload | Yes | Yes | No |
| Includes updater/log watcher | Yes | Yes | Updater only |
| Best use | Daily local work | Double-click local work | Demos/testing |

---

## Typical Workflow

### Development

```powershell
python startup.py
# edit/test with hot reload
python shutdown.py
```

### Production-like local test

```powershell
START.bat
STOP.bat
```

---

## Troubleshooting

- Cannot open app: verify `http://localhost:3000` after `python startup.py`
- API not responding: verify `http://localhost:5000/health`
- Port collision: run `python shutdown.py` before restarting

---

## Summary

- Develop and debug: `python startup.py`
- Stop everything: `python shutdown.py`
- Use `START-DEV.bat` and `STOP.bat` as optional wrappers
- Use `START.bat` for production-like local validation
