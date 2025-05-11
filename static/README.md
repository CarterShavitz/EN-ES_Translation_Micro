# Vocabulary Management Web UI

This is a simple web interface for managing vocabulary terms and their definitions.

## Features

1. **User Registration**:

   - Register to get an API key for accessing the vocabulary service

2. **Vocabulary Management**:
   - Add new terms and their definitions (e.g., SOW = Scope of Work)
   - View all vocabulary terms
   - Delete vocabulary terms

## How to Use

1. **Register a User**:

   - Enter a username and password
   - Click "Register" to get an API key
   - The API key will be stored in your browser's local storage

2. **Manage Vocabulary**:

   - Add terms by entering the term (e.g., SOW) and its definition (e.g., Scope of Work)
   - View all terms and definitions in the table
   - Delete terms by clicking the "Delete" button

## Technical Details

- The web UI communicates with the vocabulary microservice API
- Authentication is handled via API keys
- All data is stored in a SQLite database on the server
- The backend uses the same API endpoints as the translation service, but we're using it to store terms and definitions instead of translations
