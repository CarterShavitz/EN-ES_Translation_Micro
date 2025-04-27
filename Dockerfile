FROM python:3.9-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Clean install of dependencies with specific versions
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a directory for the database
RUN mkdir -p /app/data

# Create a volume for the database
VOLUME /app/data

# Set environment variable for database path
ENV DATABASE_PATH=/app/data/translations.db

EXPOSE 5000

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
