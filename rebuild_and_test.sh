#!/bin/bash

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down

# Remove old images and volumes
echo "Removing old images and volumes..."
docker-compose rm -f
docker volume prune -f

# Create data directory if it doesn't exist
echo "Ensuring data directory exists..."
mkdir -p data

# Build the new image
echo "Building new image..."
docker-compose build --no-cache

# Run the tests
echo "Running tests..."
./tests/run_tests.sh

# Exit with the test exit code
exit $?
