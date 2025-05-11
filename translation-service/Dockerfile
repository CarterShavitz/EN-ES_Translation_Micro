FROM python:3.9-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Clean install of dependencies with specific versions
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/api || exit 1

CMD ["python", "app.py"]
