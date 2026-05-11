import requests
import time
import os

print("Waiting for Flask to initialize...")
time.sleep(8)

print("\n" + "="*60)
print("TESTING LANGGRAPH REACT AGENT - TRUE AGENTIC BEHAVIOR")
print("="*60)

# Test 1: Create folder (core agentic task)
print("\nTest 1: Create a folder named 'test_folder' in C:\\temp")
print("-" * 60)
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "Create a folder named test_folder in C:\\temp",
            'session_id': 'test1'
        },
        timeout=60
    )
    result = response.json()
    print(f"Response: {result['response']}")

    # Check if folder was created
    if os.path.exists(r'C:\temp\test_folder'):
        print("RESULT: Folder was ACTUALLY CREATED! Agent is truly agentic!")
    else:
        print("NOTE: Folder not created - may need better tool parameter extraction")

except Exception as e:
    print(f"ERROR: {str(e)}")

# Test 2: List files (file system interaction)
print("\n\nTest 2: List files in C:\\Users\\ratul\\Desktop")
print("-" * 60)
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "List the files in C:\\Users\\ratul\\Desktop",
            'session_id': 'test2'
        },
        timeout=60
    )
    result = response.json()
    response_text = result['response'][:300]
    print(f"Response (first 300 chars): {response_text}")

except Exception as e:
    print(f"ERROR: {str(e)}")

# Test 3: System info
print("\n\nTest 3: Get system information")
print("-" * 60)
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "Show me the system information",
            'session_id': 'test3'
        },
        timeout=60
    )
    result = response.json()
    response_text = result['response'][:300]
    print(f"Response (first 300 chars): {response_text}")

except Exception as e:
    print(f"ERROR: {str(e)}")

# Test 4: Current time
print("\n\nTest 4: Get current time")
print("-" * 60)
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={
            'command': "What is the current time?",
            'session_id': 'test4'
        },
        timeout=60
    )
    result = response.json()
    print(f"Response: {result['response']}")

except Exception as e:
    print(f"ERROR: {str(e)}")

print("\n" + "="*60)
print("TESTS COMPLETED")
print("="*60)
