#!/bin/bash
# Render build script

# Install Python dependencies
pip install -r requirements.txt

# Setup database (creates schema and loads NFL data)
echo "🗄️  Setting up database..."
python setup_render_db.py || echo "⚠️  Database setup skipped (may already exist)"

# Build React frontend
cd frontend
npm install
npm run build
cd ..

echo "Build complete!"
