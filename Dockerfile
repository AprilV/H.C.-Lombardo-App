# Railway Dockerfile for H.C. Lombardo App
FROM python:3.10-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend and install dependencies
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install

# Copy all application files
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm run build

# Back to app directory
WORKDIR /app

# Expose port
EXPOSE 8080

# Set PORT environment variable if not set
ENV PORT=8080

# Run database setup then start server
CMD ["sh", "-c", "python setup_render_db.py || true && gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"]
