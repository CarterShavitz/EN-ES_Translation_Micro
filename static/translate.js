// Global variables
let apiKey = localStorage.getItem('apiKey') || '';
const API_BASE_URL = 'http://localhost:5000';

// DOM elements
const registerForm = document.getElementById('registerForm');
const apiKeyDisplay = document.getElementById('apiKeyDisplay');
const apiKeyElement = document.getElementById('apiKey');
const translateForm = document.getElementById('translateForm');
const englishText = document.getElementById('englishText');
const spanishText = document.getElementById('spanishText');

// Check if API key exists in local storage and show it
if (apiKey) {
    apiKeyElement.textContent = apiKey;
    apiKeyDisplay.classList.remove('d-none');
}

// Event listeners
registerForm.addEventListener('submit', handleRegister);
translateForm.addEventListener('submit', handleTranslate);

// Register user and get API key
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            apiKey = data.api_key;
            localStorage.setItem('apiKey', apiKey);
            apiKeyElement.textContent = apiKey;
            apiKeyDisplay.classList.remove('d-none');
        } else {
            alert(`Registration failed: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Translate text
async function handleTranslate(event) {
    event.preventDefault();
    
    if (!apiKey) {
        alert('Please register to get an API key first');
        return;
    }
    
    const text = englishText.value.trim();
    
    if (!text) {
        alert('Please enter some text to translate');
        return;
    }
    
    // Show loading indicator
    spanishText.value = "Translating...";
    
    try {
        const response = await fetch(`${API_BASE_URL}/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify({ text })
        });
        
        if (response.ok) {
            const data = await response.json();
            spanishText.value = data.translation;
        } else {
            let errorMessage = "Translation failed";
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = `${errorMessage}: ${response.statusText}`;
            }
            
            spanishText.value = `Error: ${errorMessage}`;
            alert(errorMessage);
        }
    } catch (error) {
        spanishText.value = `Error: ${error.message}`;
        alert(`Error: ${error.message}`);
    }
}
