from flask import Flask, render_template, request, jsonify
from langchain_ollama import ChatOllama
import subprocess
import os
import datetime
import wikipedia
import uuid
import webbrowser

app = Flask(__name__)

# Initialize LLM without ReAct agent first - just use basic LLM
print("Initializing ChatOllama...")
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")
print("ChatOllama initialized successfully!")

# File system operations
def create_folder(path: str, folder_name: str) -> str:
    """Create a new folder."""
    try:
        folder_path = os.path.join(path, folder_name)
        if os.path.exists(folder_path):
            return f"Folder '{folder_name}' already exists at {folder_path}"
        os.makedirs(folder_path, exist_ok=True)
        return f"SUCCESS: Folder '{folder_name}' created at {folder_path}"
    except Exception as e:
        return f"ERROR: Could not create folder: {str(e)}"

def delete_file(file_path: str) -> str:
    """Delete a file or folder."""
    try:
        if not os.path.exists(file_path):
            return f"ERROR: File not found: {file_path}"
        if os.path.isdir(file_path):
            import shutil
            shutil.rmtree(file_path)
            return f"SUCCESS: Folder deleted: {file_path}"
        else:
            os.remove(file_path)
            return f"SUCCESS: File deleted: {file_path}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def list_files(directory_path: str) -> str:
    """List files in a directory."""
    try:
        if not os.path.exists(directory_path):
            return f"ERROR: Directory not found: {directory_path}"
        items = os.listdir(directory_path)
        if not items:
            return f"Directory is empty: {directory_path}"
        return f"Files in {directory_path}:\n" + "\n".join([f"  - {item}" for item in items[:20]])
    except Exception as e:
        return f"ERROR: {str(e)}"

def open_website(url: str) -> str:
    """Open a website."""
    try:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        webbrowser.open(url)
        return f"SUCCESS: Opened {url} in browser"
    except Exception as e:
        return f"ERROR: {str(e)}"

def open_application(app_name: str) -> str:
    """Open an application."""
    try:
        app_map = {
            'gmail': 'https://gmail.com',
            'youtube': 'https://youtube.com',
            'chrome': 'chrome',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
        }

        app_lower = app_name.lower().strip()
        target = app_map.get(app_lower, app_name)

        if target.startswith('https://'):
            return open_website(target)

        try:
            subprocess.Popen(target)
            return f"SUCCESS: Opened {app_name}"
        except:
            return f"ERROR: Could not open {app_name}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def get_time() -> str:
    """Get current time."""
    return f"Current time: {datetime.datetime.now().strftime('%I:%M %p')}"

def get_date() -> str:
    """Get current date."""
    return f"Current date: {datetime.datetime.now().strftime('%A, %B %d, %Y')}"

# Parse user intent and execute
def process_command(command: str) -> str:
    """Process a user command and execute the appropriate action."""
    print(f"[DEBUG] Processing: {command}")
    command_lower = command.lower()

    # File operations
    if 'make' in command_lower and ('folder' in command_lower or 'directory' in command_lower):
        parts = command.split("'")
        if len(parts) >= 2:
            folder_name = parts[1]
            path = "C:\\temp" if "C:\\" not in command else command.split("C:\\")[1].split(" ")[0]
            if not path.startswith("C:\\"):
                path = f"C:\\{path}"
            path = os.path.dirname(path) or "C:\\temp"
            return create_folder(path, folder_name)

    if 'make' in command_lower and 'folder' in command_lower:
        # Extract folder name from command
        words = command.split()
        if 'named' in command_lower:
            idx = command_lower.find('named')
            folder_name = command[idx+6:].strip().split()[0].strip("'\"")
            return create_folder("C:\\Users\\ratul\\Desktop", folder_name)

    if 'list' in command_lower and 'files' in command_lower or 'dir' in command_lower:
        path = "C:\\" if "\\" not in command else command.split("\\")[0] + "\\"
        return list_files(path)

    if 'delete' in command_lower or 'remove' in command_lower:
        # Ask for confirmation
        return "Please confirm file deletion"

    # Web operations
    if 'open' in command_lower:
        if 'website' in command_lower or '.com' in command_lower:
            url = command.replace('open', '').strip()
            return open_website(url)
        else:
            app_name = command.replace('open', '').strip()
            return open_application(app_name)

    # Time/Date
    if 'time' in command_lower and 'what' in command_lower:
        return get_time()
    if 'date' in command_lower and 'what' in command_lower:
        return get_date()

    # Default: ask LLM
    print(f"[DEBUG] Sending to LLM: {command}")
    messages = [{"role": "user", "content": command}]
    response = llm.invoke(messages)
    return response.content

# Session management
sessions = {}

def get_or_create_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {"messages": []}
    return sessions[session_id]

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    """Process user command."""
    print("[DEBUG] /api/ask called")
    data = request.json
    command = data.get('command', '').strip()
    session_id = data.get('session_id', str(uuid.uuid4()))

    print(f"[DEBUG] Command: {command}")

    if not command:
        return jsonify({'response': 'Please say something.', 'session_id': session_id})

    try:
        session = get_or_create_session(session_id)
        session['messages'].append({"role": "user", "content": command})

        # Process the command
        response = process_command(command)

        session['messages'].append({"role": "assistant", "content": response})

        print(f"[DEBUG] Response: {response[:100]}")

        return jsonify({
            'response': response,
            'session_id': session_id
        })

    except Exception as e:
        print(f"[DEBUG] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'response': f'Error: {str(e)}', 'session_id': session_id}), 500

if __name__ == '__main__':
    print("Starting AI Virtual Assistant (Simplified Agent)")
    print("http://localhost:8000")
    app.run(debug=False, host='localhost', port=8000)
