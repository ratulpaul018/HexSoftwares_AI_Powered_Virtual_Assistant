import requests
import time
import os

print("Waiting for Flask to start...")
time.sleep(5)

# Test 1: Create folder
print("\n=== Test 1: Create Folder ===")
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "make a folder named 'test_agentic_folder' in C:\\temp",
            'session_id': 'test1'
        },
        timeout=15
    )
    result = response.json()
    print(f"Response: {result['response']}")

    # Check if folder was actually created
    if os.path.exists(r'C:\temp\test_agentic_folder'):
        print("SUCCESS: Folder was actually created on disk!")
    else:
        print("NOTE: Folder not found on disk")

except Exception as e:
    print(f"Error: {str(e)}")

# Test 2: List files
print("\n=== Test 2: List Files ===")
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "list files in C:\\Users",
            'session_id': 'test2'
        },
        timeout=15
    )
    result = response.json()
    print(f"Response (first 200 chars): {result['response'][:200]}")
except Exception as e:
    print(f"Error: {str(e)}")

# Test 3: Get time
print("\n=== Test 3: Get Time ===")
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "what is the current time",
            'session_id': 'test3'
        },
        timeout=15
    )
    result = response.json()
    print(f"Response: {result['response']}")
except Exception as e:
    print(f"Error: {str(e)}")

# Test 4: Open website
print("\n=== Test 4: Open Website ===")
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "open google.com",
            'session_id': 'test4'
        },
        timeout=15
    )
    result = response.json()
    print(f"Response: {result['response']}")
except Exception as e:
    print(f"Error: {str(e)}")

print("\nAll tests completed!")
