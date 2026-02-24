# --- STAGE 1: Build CSS with Node ---
FROM node:20-slim AS builder-css
WORKDIR /build
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build:css

# --- STAGE 2: Python Backend ---
FROM python:3.11-slim AS runner

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends 
    curl 
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy project files
COPY . .

# Copy the built CSS from the first stage
COPY --from=builder-css /build/static/dist/css/app.min.css ./static/dist/css/app.min.css

# Expose the port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
