#!/bin/bash
# Railway startup script

# Run database setup (ignore errors)
python setup_render_db.py || true

# Start gunicorn
exec gunicorn api_server:app --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120
