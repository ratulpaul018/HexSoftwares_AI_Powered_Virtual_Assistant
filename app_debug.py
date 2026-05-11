from flask import Flask, render_template, request, jsonify
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
import sys
import datetime

app = Flask(__name__)

print("[DEBUG] Flask app starting...", flush=True)

# Initialize LLM
print("[DEBUG] Initializing ChatOllama...", flush=True)
llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434")
print("[DEBUG] ChatOllama initialized", flush=True)

# Simple test tool
@tool
def test_tool(message: str) -> str:
    """A simple test tool."""
    print(f"[DEBUG] test_tool called with: {message}", flush=True)
    return f"Test response: {message}"

print("[DEBUG] Creating agent with tools...", flush=True)
tools = [test_tool]
agent = create_react_agent(llm, tools)
print("[DEBUG] Agent created successfully", flush=True)

@app.route('/')
def home():
    return "Flask is running"

@app.route('/api/ask', methods=['POST'])
def ask():
    """Test endpoint."""
    print(f"[DEBUG] /api/ask called", flush=True, file=sys.stderr)
    sys.stderr.flush()

    data = request.json
    command = data.get('command', '').strip()
    print(f"[DEBUG] Command received: {command}", flush=True, file=sys.stderr)
    sys.stderr.flush()

    try:
        print(f"[DEBUG] Invoking agent...", flush=True, file=sys.stderr)
        sys.stderr.flush()

        result = agent.invoke({
            "messages": [{"role": "user", "content": command}]
        })

        print(f"[DEBUG] Agent returned", flush=True, file=sys.stderr)
        sys.stderr.flush()

        response = result["messages"][-1].content if result["messages"] else "No response"

        return jsonify({'response': response})

    except Exception as e:
        print(f"[DEBUG] Error: {str(e)}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[DEBUG] Starting Flask server...", flush=True)
    sys.stdout.flush()
    app.run(debug=False, host='localhost', port=8000)
