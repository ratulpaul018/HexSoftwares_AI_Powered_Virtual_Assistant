import requests
import json
import time

# Wait for server to start
time.sleep(3)

# Test 1: Create folder
print("Test 1: Create folder")
response = requests.post(
    'http://localhost:8000/api/ask',
    json={
        'command': 'make a folder named test_folder in C:\\\\Users\\\\ratul\\\\Desktop',
        'session_id': 'test1'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test 2: Get current time
print("Test 2: Get current time")
response = requests.post(
    'http://localhost:8000/api/ask',
    json={
        'command': 'what is the current time',
        'session_id': 'test2'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test 3: System info
print("Test 3: Get system info")
response = requests.post(
    'http://localhost:8000/api/ask',
    json={
        'command': 'show me system information',
        'session_id': 'test3'
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
