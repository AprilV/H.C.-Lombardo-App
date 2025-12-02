#!/usr/bin/env
# AWS Amplify Build Script (Frontend Only)
# Backend builds happen on EC2 manually

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎨 Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete!"
