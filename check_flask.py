import requests
import time
import subprocess

print("Checking Flask server...")

# Check if Flask process is running
result = subprocess.run(['tasklist'], capture_output=True, text=True)
if 'python' in result.stdout:
    print("OK - Python process found running")
else:
    print("ERROR - No Python process found")

# Try to connect to Flask
time.sleep(3)
try:
    response = requests.get('http://localhost:8000/', timeout=5)
    print(f"OK - Flask is running (status: {response.status_code})")

    # Now test the agent API
    print("\nTesting agent with 'make a folder' command...")
    test_response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': 'make a folder named test_folder_agentic in C:\\\\temp',
            'session_id': 'test_agentic'
        },
        timeout=60
    )
    print(f"Status: {test_response.status_code}")
    result = test_response.json()
    print(f"Response: {result['response'][:200]}")

except requests.exceptions.ConnectionError:
    print("ERROR - Cannot connect to Flask at localhost:8000")
    print("Is Flask running? Try:")
    print("  cd 'c:\\Latest Environment (16.04.25)\\my_new_env\\AI Assistant'")
    print("  python app.py")
except Exception as e:
    print(f"ERROR: {str(e)}")
