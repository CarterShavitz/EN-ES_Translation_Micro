# EN-ES Translation Microservice

A containerized Flask microservice for managing English-Spanish translations with API key authentication.

## Overview

This microservice provides a RESTful API for storing and retrieving English-Spanish translations with:

- User registration and API key authentication
- CRUD operations for translation pairs
- SQLite database persistence
- Docker containerization
- Automated testing

## Quick Start

### Docker Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/EN-ES_Translation_Micro.git
cd EN-ES_Translation_Micro

# Build and start the Docker container
docker-compose up -d

# Run tests to verify functionality
./rebuild_and_test.ps1  # Windows
./rebuild_and_test.sh   # Linux/macOS
```

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
```

## API Endpoints

All endpoints except `/register` require an API key in the `X-API-Key` header.

| Endpoint             | Method | Description                            |
| -------------------- | ------ | -------------------------------------- |
| `/register`          | POST   | Register a new user and get an API key |
| `/translations`      | GET    | List all translations                  |
| `/translations`      | POST   | Add a new translation                  |
| `/translations/{id}` | GET    | Get a specific translation             |
| `/translations/{id}` | PUT    | Update a translation                   |
| `/translations/{id}` | DELETE | Delete a translation                   |

## Example Usage

### Register a User

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "pass123"}' \
  http://localhost:5000/register
```

### Add a Translation

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"English": "hello", "Spanish": "hola"}' \
  http://localhost:5000/translations
```

## Project Structure

- `app.py`: Flask application with routes and middleware
- `models.py`: Database models and schema
- `service.py`: Business logic layer
- `Dockerfile` & `docker-compose.yml`: Container configuration
- `tests/`: Automated test scripts
- `rebuild_and_test.ps1/sh`: Scripts to rebuild and test the application

## Testing

The project includes comprehensive tests that verify all API functionality:

```bash
# Run tests with Docker (recommended)
./rebuild_and_test.ps1  # Windows
./rebuild_and_test.sh   # Linux/macOS

# Run tests locally
python tests/run_local_tests.py
```

The tests verify:

1. User registration
2. Adding translations
3. Retrieving translations
4. Updating translations
5. Deleting translations
