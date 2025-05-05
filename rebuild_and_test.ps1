# Stop any running containers
Write-Host "Stopping any running containers..."
docker-compose down

# Remove old images and volumes
Write-Host "Removing old images and volumes..."
docker-compose rm -f
docker volume prune -f

# Create data directory if it doesn't exist
Write-Host "Ensuring data directory exists..."
if (-not (Test-Path -Path "data")) {
    New-Item -ItemType Directory -Path "data"
}

# Build the new image
Write-Host "Building new image..."
docker-compose build --no-cache

# Run the tests
Write-Host "Running tests..."
./tests/run_tests.ps1

# Exit with the test exit code
exit $LASTEXITCODE
