// Global variables
let apiKey = localStorage.getItem('apiKey') || '';

// Service URLs - use relative URLs to avoid CORS issues
const USER_SERVICE_URL = '/user-service';
const VOCAB_SERVICE_URL = '/vocab-service';
const TRANSLATION_SERVICE_URL = '/translation-service';

// Common fetch options for all API calls
const fetchOptions = {
    mode: 'cors',
    credentials: 'include',
    headers: {
        'Accept': 'application/json'
    }
};

// DOM elements
const registerForm = document.getElementById('registerForm');
const apiKeyDisplay = document.getElementById('apiKeyDisplay');
const apiKeyElement = document.getElementById('apiKey');
const addVocabForm = document.getElementById('addVocabForm');
const vocabTableBody = document.getElementById('vocabTableBody');
const translateForm = document.getElementById('translateForm');
const englishText = document.getElementById('englishText');
const spanishText = document.getElementById('spanishText');
const preprocessedTextContainer = document.getElementById('preprocessedTextContainer');
const preprocessedText = document.getElementById('preprocessedText');

// Check if API key exists in local storage and show it
if (apiKey) {
    apiKeyElement.textContent = apiKey;
    apiKeyDisplay.classList.remove('d-none');
    // Load vocabulary on page load if API key exists
    loadVocabulary();
}

// Event listeners
registerForm.addEventListener('submit', handleRegister);
addVocabForm.addEventListener('submit', handleAddVocab);
translateForm.addEventListener('submit', handleTranslate);

// Register user and get API key
async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${USER_SERVICE_URL}/register`, {
            method: 'POST',
            headers: {
                ...fetchOptions.headers,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }),
            mode: 'cors',
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            apiKey = data.api_key;
            localStorage.setItem('apiKey', apiKey);
            apiKeyElement.textContent = apiKey;
            apiKeyDisplay.classList.remove('d-none');

            // Load vocabulary after successful registration
            loadVocabulary();
        } else {
            alert(`Registration failed: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Load vocabulary from API
async function loadVocabulary() {
    if (!apiKey) {
        alert('Please register to get an API key first');
        return;
    }

    try {
        const response = await fetch(`${VOCAB_SERVICE_URL}/translations`, {
            method: 'GET',
            headers: {
                ...fetchOptions.headers,
                'X-API-Key': apiKey
            },
            mode: 'cors',
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            displayVocabulary(data);
        } else {
            const errorData = await response.json();
            alert(`Failed to load vocabulary: ${errorData.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Display vocabulary in the table
function displayVocabulary(vocabulary) {
    vocabTableBody.innerHTML = '';

    if (vocabulary.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" class="text-center">No vocabulary items found</td>';
        vocabTableBody.appendChild(row);
        return;
    }

    vocabulary.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.English}</td>
            <td>${item.Spanish}</td>
            <td>
                <button class="btn btn-sm btn-link btn-delete" data-id="${item.id}">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </td>
        `;
        vocabTableBody.appendChild(row);

        // Add event listener to delete button
        const deleteButton = row.querySelector('.btn-delete');
        deleteButton.addEventListener('click', () => deleteVocabItem(item.id));
    });
}

// Add new vocabulary item
async function handleAddVocab(event) {
    event.preventDefault();

    if (!apiKey) {
        alert('Please register to get an API key first');
        return;
    }

    const englishTerm = document.getElementById('englishTerm').value;
    const spanishTerm = document.getElementById('spanishTerm').value;

    try {
        const response = await fetch(`${VOCAB_SERVICE_URL}/translations`, {
            method: 'POST',
            headers: {
                ...fetchOptions.headers,
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify({
                English: englishTerm,
                Spanish: spanishTerm
            }),
            mode: 'cors',
            credentials: 'include'
        });

        if (response.ok) {
            // Clear form fields
            document.getElementById('englishTerm').value = '';
            document.getElementById('spanishTerm').value = '';

            // Reload vocabulary
            loadVocabulary();
        } else {
            const errorData = await response.json();
            alert(`Failed to add vocabulary: ${errorData.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Delete vocabulary item
async function deleteVocabItem(id) {
    if (!apiKey) {
        alert('Please register to get an API key first');
        return;
    }

    if (!confirm('Are you sure you want to delete this vocabulary item?')) {
        return;
    }

    try {
        const response = await fetch(`${VOCAB_SERVICE_URL}/translations/${id}`, {
            method: 'DELETE',
            headers: {
                ...fetchOptions.headers,
                'X-API-Key': apiKey
            },
            mode: 'cors',
            credentials: 'include'
        });

        if (response.ok) {
            // Reload vocabulary
            loadVocabulary();
        } else {
            const errorData = await response.json();
            alert(`Failed to delete vocabulary: ${errorData.error}`);
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

    try {
        const response = await fetch(`${TRANSLATION_SERVICE_URL}/translate`, {
            method: 'POST',
            headers: {
                ...fetchOptions.headers,
                'Content-Type': 'application/json',
                'X-API-Key': apiKey
            },
            body: JSON.stringify({ text }),
            mode: 'cors',
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            spanishText.value = data.translation;

            // Handle preprocessed text if available
            if (data.preprocessed && data.preprocessed_text) {
                preprocessedText.value = data.preprocessed_text;
                preprocessedTextContainer.classList.remove('d-none');
            } else {
                preprocessedTextContainer.classList.add('d-none');
            }
        } else {
            const errorData = await response.json();
            alert(`Translation failed: ${errorData.error}`);
            preprocessedTextContainer.classList.add('d-none');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}
