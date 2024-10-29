const API_URL = 'http://127.0.0.1:5000/api';
let currentToken = null;

async function register() {
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        displayResponse(data);
    } catch (error) {
        displayResponse({ error: error.message });
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        if (data.token) {
            currentToken = data.token;
        }
        displayResponse(data);
    } catch (error) {
        displayResponse({ error: error.message });
    }
}

async function accessProtected() {
    if (!currentToken) {
        displayResponse({ error: 'Please login first' });
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/protected`, {
            headers: {
                'Authorization': currentToken
            }
        });
        
        const data = await response.json();
        displayResponse(data);
    } catch (error) {
        displayResponse({ error: error.message });
    }
}

function displayResponse(data) {
    document.getElementById('response-data').textContent = 
        JSON.stringify(data, null, 2);
}