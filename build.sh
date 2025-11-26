#!/bin/bash
# Render build script

# Install Python dependencies
pip install -r requirements.txt

# NOTE: Database setup must be run manually AFTER first deployment
# because environment variables aren't available during build.
# Run this command in Render Shell once app is deployed:
# python setup_render_db.py

# Build React frontend
cd frontend
npm install
npm run build
cd ..

echo "Build complete!"
