# English-Spanish Translation Microservices

A containerized microservices application for managing vocabulary terms and translating English to Spanish.

## Overview

This application consists of four separate microservices:

1. **User Management Service**: Handles user registration and API key authentication
2. **Vocabulary Storage Service**: Manages the storage and retrieval of vocabulary terms
3. **Translation Service**: Provides English to Spanish translation using a machine learning model
4. **Web UI**: A simple web interface for interacting with the services

## Architecture

- Each service runs in its own Docker container
- Services communicate with each other via HTTP APIs
- Authentication is handled via API keys
- Data is persisted in SQLite databases (one per service)
- The web UI provides a unified interface to all services

## Quick Start

### Docker Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/EN-ES_Translation_Micro.git
cd EN-ES_Translation_Micro

# Build and start the Docker containers
docker-compose up -d

# Access the web UI
# Open your browser and navigate to http://localhost
```

## Service Details

### User Management Service (Port 5001)

- Handles user registration
- Generates and validates API keys
- Stores user data in a SQLite database

### Vocabulary Storage Service (Port 5000)

- Stores English-Spanish vocabulary terms
- Provides CRUD operations for vocabulary management
- Authenticates requests using the User Management Service

### Translation Service (Port 5002)

- Translates English text to Spanish using a machine learning model
- Falls back to a simple dictionary-based translator if the ML model fails
- Authenticates requests using the User Management Service

### Web UI (Port 80)

- Provides a user-friendly interface for all services
- Handles user registration and API key storage
- Allows vocabulary management (add/delete terms)
- Provides a translation interface

## API Endpoints

All endpoints except `/register` require an API key in the `X-API-Key` header.

### User Management Service

- `POST /register`: Register a new user and get an API key
- `GET /validate-key`: Validate an API key
- `GET /api`: Health check endpoint

### Vocabulary Storage Service

- `GET /translations`: List all vocabulary entries
- `POST /translations`: Create a new vocabulary entry
- `GET /translations/{id}`: Get a specific vocabulary entry
- `PUT /translations/{id}`: Update a vocabulary entry
- `DELETE /translations/{id}`: Delete a vocabulary entry
- `GET /api`: Health check endpoint

### Translation Service

- `POST /translate`: Translate English text to Spanish
- `GET /api`: Health check endpoint

## Example Usage

### Register a User

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "pass123"}' \
  http://localhost:5001/register
```

### Add a Vocabulary Term

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"English": "SOW", "Spanish": "Scope of Work"}' \
  http://localhost:5000/translations
```

### Translate Text

```bash
curl -X POST -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"text": "Hello, how are you today?"}' \
  http://localhost:5002/translate
```

## Web UI

The project includes a simple web UI for interacting with all services:

- User registration and API key management
- Vocabulary management (add/delete terms)
- Text translation from English to Spanish

To access the web UI, simply open your browser and navigate to:

```
http://localhost/
```

## Project Structure

- `user-service/`: User management microservice
  - `app.py`: Flask application for user management
  - `Dockerfile`: Container configuration for user service
  - `requirements.txt`: Dependencies for user service
- `vocab-service/`: Vocabulary storage microservice
  - `app.py`: Flask application for vocabulary management
  - `Dockerfile`: Container configuration for vocabulary service
  - `requirements.txt`: Dependencies for vocabulary service
- `translation-service/`: Translation microservice
  - `app.py`: Flask application for translation
  - `translation_model.py`: Machine learning translation model
  - `simple_translator.py`: Fallback dictionary-based translator
  - `Dockerfile`: Container configuration for translation service
  - `requirements.txt`: Dependencies for translation service
- `web-ui/`: Web interface
  - `index.html`: Main HTML page
  - `script.js`: Client-side JavaScript
  - `styles.css`: CSS styles
  - `Dockerfile`: Container configuration for web UI
- `docker-compose.yml`: Multi-container Docker configuration
- `tests/`: Automated test scripts

## Development and Testing

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

### Local Development

Each service can be developed and tested independently:

```bash
# User Management Service
cd user-service
pip install -r requirements.txt
python app.py

# Vocabulary Storage Service
cd vocab-service
pip install -r requirements.txt
python app.py

# Translation Service
cd translation-service
pip install -r requirements.txt
python app.py

# Web UI (using any static file server)
cd web-ui
python -m http.server 80
```

### Testing

The project includes tests for each service. To run all tests:

```bash
# Build and test all services
docker-compose up -d
./tests/run_tests.ps1  # Windows
./tests/run_tests.sh   # Linux/macOS
```

The tests verify:

1. User registration and API key validation
2. Vocabulary term management (CRUD operations)
3. English to Spanish translation
4. Web UI functionality
