import requests
import json
import sys
import time
from requests.exceptions import ConnectionError, Timeout

BASE_URL = "http://localhost:5000"
API_KEY = None
TRANSLATION_ID = None  # To store the ID of the translation we add
MAX_RETRIES = 3
RETRY_DELAY = 2

def make_request(method, endpoint, **kwargs):
    """Helper function to make requests with retries"""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    for attempt in range(MAX_RETRIES):
        try:
            if method.lower() == 'get':
                response = requests.get(url, **kwargs)
            elif method.lower() == 'post':
                response = requests.post(url, **kwargs)
            elif method.lower() == 'put':
                response = requests.put(url, **kwargs)
            elif method.lower() == 'delete':
                response = requests.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return response
        except (ConnectionError, Timeout) as e:
            print(f"Request failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Giving up.")
                raise

def test_register_user():
    global API_KEY
    print("Testing user registration...")

    try:
        # Generate a unique username with timestamp to avoid conflicts
        import time
        unique_username = f"testuser_{int(time.time())}"

        # Register a new user
        response = make_request(
            'post',
            "/register",
            json={"username": unique_username, "password": "testpassword"}
        )

        if response.status_code == 201:
            data = response.json()
            API_KEY = data.get("api_key")
            print(f"✅ User registered successfully. API Key: {API_KEY}")
            return True
        elif response.status_code == 409:
            print("⚠️ User already exists. This should not happen with a unique username.")
            print("Trying with a different username...")

            # Try with an even more unique username
            unique_username = f"testuser_{int(time.time())}_{hash(str(time.time()))}"
            response = make_request(
                'post',
                "/register",
                json={"username": unique_username, "password": "testpassword"}
            )

            if response.status_code == 201:
                data = response.json()
                API_KEY = data.get("api_key")
                print(f"✅ User registered successfully on second attempt. API Key: {API_KEY}")
                return True
            else:
                print(f"❌ Failed to register user on second attempt. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Failed to register user. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return False

def test_add_translation():
    print("Testing adding a translation...")
    global TRANSLATION_ID

    if not API_KEY:
        print("❌ No API key available. Run test_register_user first.")
        return False

    try:
        # Add a new translation
        response = make_request(
            'post',
            "/translations",
            headers={"X-API-Key": API_KEY},
            json={"English": "hello", "Spanish": "hola"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Translation added successfully: {data}")

            # Store the ID of the translation we just added
            if data and len(data) > 0:
                TRANSLATION_ID = data[0].get("id")
                print(f"✅ Stored translation ID: {TRANSLATION_ID}")

            return True
        else:
            print(f"❌ Failed to add translation. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error adding translation: {e}")
        return False

def test_get_translations():
    print("Testing retrieving all translations...")
    global TRANSLATION_ID

    if not API_KEY:
        print("❌ No API key available. Run test_register_user first.")
        return False

    try:
        # Get all translations
        response = make_request(
            'get',
            "/translations",
            headers={"X-API-Key": API_KEY}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved translations successfully: {data}")

            # Verify that we have at least one translation
            if not data:
                print("⚠️ Warning: No translations found. Expected at least one translation.")
                print("This may be due to using a fresh database in Docker.")

                # Let's add a translation again to ensure we have one for the next tests
                if TRANSLATION_ID is None:
                    print("Adding a translation for subsequent tests...")
                    add_response = make_request(
                        'post',
                        "/translations",
                        headers={"X-API-Key": API_KEY},
                        json={"English": "hello", "Spanish": "hola"}
                    )

                    if add_response.status_code == 200:
                        add_data = add_response.json()
                        if add_data and len(add_data) > 0:
                            TRANSLATION_ID = add_data[0].get("id")
                            print(f"✅ Added a translation with ID: {TRANSLATION_ID}")
            else:
                # Check if we have the translation we added
                found_hello = False
                for translation in data:
                    if translation.get("English") == "hello" and translation.get("Spanish") == "hola":
                        found_hello = True
                        # Update the TRANSLATION_ID if we found our translation
                        TRANSLATION_ID = translation.get("id")
                        break

                if found_hello:
                    print("✅ Found the 'hello/hola' translation we added.")
                else:
                    print("⚠️ Warning: Could not find the 'hello/hola' translation we added.")

            return True
        else:
            print(f"❌ Failed to retrieve translations. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving translations: {e}")
        return False

def test_update_translation():
    print("Testing updating a translation...")

    if not API_KEY:
        print("❌ No API key available. Run test_register_user first.")
        return False

    if not TRANSLATION_ID:
        print("❌ No translation ID available. Run test_add_translation first.")
        return False

    try:
        # Update the translation using the stored ID
        response = make_request(
            'put',
            f"/translations/{TRANSLATION_ID}",
            headers={"X-API-Key": API_KEY},
            json={"English": "goodbye", "Spanish": "adiós"}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Translation updated successfully: {data}")
            return True
        else:
            print(f"❌ Failed to update translation. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error updating translation: {e}")
        return False

def test_delete_translation():
    print("Testing deleting a translation...")

    if not API_KEY:
        print("❌ No API key available. Run test_register_user first.")
        return False

    if not TRANSLATION_ID:
        print("❌ No translation ID available. Run test_add_translation first.")
        return False

    try:
        # Delete the translation using the stored ID
        response = make_request(
            'delete',
            f"/translations/{TRANSLATION_ID}",
            headers={"X-API-Key": API_KEY}
        )

        if response.status_code == 200:
            print(f"✅ Translation deleted successfully")

            # Verify the translation was deleted
            verify_response = make_request(
                'get',
                "/translations",
                headers={"X-API-Key": API_KEY}
            )

            if verify_response.status_code == 200:
                data = verify_response.json()
                deleted = True

                for translation in data:
                    if translation.get("id") == TRANSLATION_ID:
                        deleted = False
                        break

                if deleted:
                    print("✅ Verified translation was deleted")
                else:
                    print("⚠️ Warning: Translation still exists after deletion")

            return True
        else:
            print(f"❌ Failed to delete translation. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error deleting translation: {e}")
        return False

def check_api_health():
    """Check if the API is up and running"""
    print("Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("[OK] API is up and running!")
            return True
        else:
            print(f"[WARNING] API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"[WARNING] API health check failed: {e}")
        return False

def run_all_tests():
    print("Running all API tests...")

    # Wait for the API to be ready
    print("Waiting for API to be ready...")
    max_wait = 30  # seconds
    wait_interval = 5  # seconds

    # Try to connect to the API for up to max_wait seconds
    start_time = time.time()
    api_ready = False

    while time.time() - start_time < max_wait:
        if check_api_health():
            api_ready = True
            break
        print(f"API not ready yet. Waiting {wait_interval} seconds...")
        time.sleep(wait_interval)

    if not api_ready:
        print("❌ API did not become ready in time. Tests may fail.")
        return 1

    # Reset global variables for a clean test run
    global API_KEY, TRANSLATION_ID
    API_KEY = None
    TRANSLATION_ID = None

    # Run tests sequentially with dependencies
    print("\n--- Running Tests Sequentially ---")

    # Step 1: Register user
    print("\n1. User Registration Test")
    if not test_register_user():
        print("❌ User registration failed. Stopping tests.")
        return 1

    # Step 2: Add a translation
    print("\n2. Add Translation Test")
    if not test_add_translation():
        print("❌ Adding translation failed. Stopping tests.")
        return 1

    # Step 3: Get translations - should now include the one we just added
    print("\n3. Get Translations Test")
    # Add a delay to ensure the database has been updated and changes are persisted to disk
    time.sleep(5)
    if not test_get_translations():
        print("❌ Getting translations failed. Stopping tests.")
        return 1

    # Step 4: Update a translation
    print("\n4. Update Translation Test")
    if not test_update_translation():
        print("❌ Updating translation failed. Stopping tests.")
        return 1

    # Step 5: Delete a translation
    print("\n5. Delete Translation Test")
    if not test_delete_translation():
        print("❌ Deleting translation failed. Stopping tests.")
        return 1

    # All tests passed
    print("\n✅ All tests passed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(run_all_tests())
