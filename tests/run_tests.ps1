# Install test dependencies
Write-Host "Installing test dependencies..."
pip install -r requirements-test.txt

# Start the Docker container in the background
Write-Host "Starting Docker container..."
docker-compose up -d

# Wait for the container to be ready
Write-Host "Waiting for container to be ready..."
Write-Host "This may take up to 30 seconds..."
Start-Sleep -Seconds 10

# Check if the container is healthy
$CONTAINER_ID = docker-compose ps -q translation-api
$HEALTH_STATUS = docker inspect --format='{{.State.Health.Status}}' $CONTAINER_ID 2>$null
Write-Host "Container health status: $HEALTH_STATUS"

# If not healthy yet, wait a bit more
if ($HEALTH_STATUS -ne "healthy") {
    Write-Host "Container is not healthy yet, waiting more time..."
    Start-Sleep -Seconds 20
}

# Run the tests
Write-Host "Running tests..."
python tests/test_api.py

# Capture the exit code
$EXIT_CODE = $LASTEXITCODE

# Stop the Docker container
Write-Host "Stopping Docker container..."
docker-compose down

# Exit with the test exit code
exit $EXIT_CODE
