import requests
import time

print("Waiting for Flask to start...")
time.sleep(5)

print("Testing debug Flask...")
try:
    response = requests.post(
        'http://localhost:8000/api/ask',
        json={'command': 'hello'},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {str(e)}")
