# EN-ES_Translation_Micro
Microservices project of a translation service


### Register User

curl -X POST -H "Content-Type: application/json" -d '{"username": "your_username", "password": "your_password"}' http://localhost:5000/register

Retrieve the response API key for the user

### Retrieve Translations

curl -X GET -H "X-API-Key: your_api_key" http://localhost:5000/translations

### Add Translations

curl -X POST -H "Content-Type: application/json" -H "X-API-Key: your_api_key" -d '{"English": "english_phrase", "Spanish": "spanish_phrase"}' http://localhost:5000/translations
