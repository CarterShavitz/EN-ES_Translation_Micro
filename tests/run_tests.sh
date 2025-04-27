#!/bin/bash

# Install test dependencies
echo "Installing test dependencies..."
pip install -r requirements-test.txt

# Start the Docker container in the background
echo "Starting Docker container..."
docker-compose up -d

# Wait for the container to be ready
echo "Waiting for container to be ready..."
echo "This may take up to 30 seconds..."
sleep 10
# Check if the container is healthy
CONTAINER_ID=$(docker-compose ps -q translation-api)
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_ID 2>/dev/null || echo "starting")
echo "Container health status: $HEALTH_STATUS"

# If not healthy yet, wait a bit more
if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "Container is not healthy yet, waiting more time..."
    sleep 20
fi

# Run the tests
echo "Running tests..."
python tests/test_api.py

# Capture the exit code
EXIT_CODE=$?

# Stop the Docker container
echo "Stopping Docker container..."
docker-compose down

# Exit with the test exit code
exit $EXIT_CODE
