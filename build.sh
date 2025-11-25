#!/bin/bash
# Render build script

# Install Python dependencies
pip install -r requirements.txt

# Build React frontend
cd frontend
npm install
npm run build
cd ..

echo "Build complete!"
