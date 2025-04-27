import subprocess
import sys
import time
import os

def install_dependencies():
    """Install test dependencies"""
    print("Installing test dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"])

def run_app():
    """Run the Flask app in the background"""
    print("Starting the Flask app...")
    # Start the Flask app as a subprocess
    process = subprocess.Popen([sys.executable, "app.py"], 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    
    # Wait for the app to start
    print("Waiting for the app to start...")
    time.sleep(3)
    
    return process

def run_tests():
    """Run the test script"""
    print("Running tests...")
    result = subprocess.run([sys.executable, "tests/test_api.py"], 
                           capture_output=True, 
                           text=True)
    
    # Print the test output
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode

def main():
    # Install dependencies
    install_dependencies()
    
    # Run the app
    app_process = run_app()
    
    try:
        # Run the tests
        exit_code = run_tests()
        
        # Return the test exit code
        return exit_code
    finally:
        # Terminate the app process
        print("Stopping the Flask app...")
        app_process.terminate()
        app_process.wait()

if __name__ == "__main__":
    sys.exit(main())
