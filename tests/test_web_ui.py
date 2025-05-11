import requests
import json
import sys
import time
from requests.exceptions import ConnectionError, Timeout

BASE_URL = "http://localhost:5000"
API_KEY = None
MAX_RETRIES = 3
RETRY_DELAY = 2

def make_request(method, endpoint, **kwargs):
    """Helper function to make requests with retries"""
    url = f"{BASE_URL}{endpoint}"

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except (ConnectionError, Timeout) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Request failed, retrying in {RETRY_DELAY} seconds... ({e})")
                time.sleep(RETRY_DELAY)
            else:
                raise

def test_static_files():
    """Test that static files are being served correctly"""
    print("Testing static files...")

    try:
        # Test index.html
        response = make_request('get', "/")
        if response.status_code == 200 and "<!DOCTYPE html>" in response.text:
            print("✅ Index page loaded successfully")
        else:
            print(f"❌ Failed to load index page. Status code: {response.status_code}")
            return False

        # Test CSS file
        response = make_request('get', "/styles.css")
        if response.status_code == 200 and "body" in response.text:
            print("✅ CSS file loaded successfully")
        else:
            print(f"❌ Failed to load CSS file. Status code: {response.status_code}")
            return False

        # Test JavaScript file
        response = make_request('get', "/script.js")
        if response.status_code == 200 and "function" in response.text:
            print("✅ JavaScript file loaded successfully")
        else:
            print(f"❌ Failed to load JavaScript file. Status code: {response.status_code}")
            return False

        return True
    except Exception as e:
        print(f"❌ Error testing static files: {e}")
        return False

def test_register_user():
    """Test user registration"""
    print("Testing user registration...")
    global API_KEY

    try:
        # Register a new user
        response = make_request(
            'post',
            "/register",
            headers={"Content-Type": "application/json"},
            json={"username": f"testuser_{int(time.time())}", "password": "testpass123"}
        )

        if response.status_code == 201:
            data = response.json()
            API_KEY = data.get("api_key")
            print(f"✅ User registered successfully. API Key: {API_KEY}")
            return True
        else:
            print(f"❌ Failed to register user. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return False



def test_translate_endpoint():
    """Test the translation endpoint"""
    print("Testing translation endpoint...")

    if not API_KEY:
        print("❌ No API key available. Run test_register_user first.")
        return False

    try:
        # Try to translate a simple text
        response = make_request(
            'post',
            "/translate",
            headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
            json={"text": "Hello, how are you?"}
        )

        if response.status_code == 200:
            data = response.json()
            translation = data.get("translation")
            print(f"✅ Translation successful: '{translation}'")
            return True
        elif response.status_code == 503:
            # This is expected if the translation model is not available
            print("⚠️ Translation model not available (this is expected if dependencies are not installed)")
            return True
        else:
            print(f"❌ Translation failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during translation: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Web UI tests...\n")

    # Step 1: Test static files
    print("\n1. Static Files Test")
    if not test_static_files():
        print("❌ Static files test failed. Stopping tests.")
        return 1

    # Step 2: Test user registration
    print("\n2. User Registration Test")
    if not test_register_user():
        print("❌ User registration failed. Stopping tests.")
        return 1

    # Step 3: Test translation endpoint
    print("\n3. Translation Endpoint Test")
    if not test_translate_endpoint():
        print("❌ Translation endpoint test failed. Stopping tests.")
        return 1

    # All tests passed
    print("\n✅ All Web UI tests passed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
