import os
import subprocess

print("Looking for Ollama...")

# Common install paths
paths_to_check = [
    r'C:\Users\ratul\AppData\Local\Programs\Ollama\ollama.exe',
    r'C:\Program Files\Ollama\ollama.exe',
    r'C:\Program Files (x86)\Ollama\ollama.exe',
]

found = False
for path in paths_to_check:
    if os.path.exists(path):
        print(f"Found Ollama at: {path}")
        found = True
        break

if not found:
    print("Ollama not found in expected locations")
    print("Checking if Ollama is running...")
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'ollama' in result.stdout.lower():
            print("Ollama process is running!")
        else:
            print("Ollama process is NOT running")
            print("\nTo use the AI Assistant, you need to start Ollama:")
            print("1. Run Ollama (usually: C:\\Users\\ratul\\AppData\\Local\\Programs\\Ollama\\ollama.exe)")
            print("2. Make sure the 'llama3.2' model is downloaded")
            print("3. Then start the Flask assistant")
    except Exception as e:
        print(f"Error checking processes: {e}")
