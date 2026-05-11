# AI Assistant Setup - Flask + MCP Server

This setup provides:
1. **Flask Web App** - Web interface for users (voice input, chat interface, system monitoring)
2. **MCP Server** - Local Model Context Protocol server for Claude Code to call tools directly
3. **Local Ollama** - Runs llama3.2 locally (no API, no internet required)

## Installation

### 1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Verify Ollama is installed locally
- Download from: https://ollama.ai/
- Start Ollama: Run the Ollama app or `ollama serve`
- Pull model: `ollama pull llama3.2`
- Verify: `ollama list` (should show llama3.2)

## Running the System

### Option 1: Run Both Servers at Once (Recommended)
```powershell
.\run_servers.ps1
```

This will open two PowerShell windows:
- **Flask App**: http://localhost:8000
- **MCP Server**: Running locally on stdio

### Option 2: Run Servers Separately

**Terminal 1 - Flask Web App:**
```bash
python app.py
```
Then visit: http://localhost:8000

**Terminal 2 - MCP Server:**
```bash
python mcp_server.py
```

## Configure Claude Code to Use MCP Server

### For VSCode Extension:
Create `.vscode/settings.json` in your project:
```json
{
  "claude.mcpServers": {
    "ai-assistant": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "c:\\Latest Environment (16.04.25)\\my_new_env\\AI Assistant"
    }
  }
}
```

### For Claude.ai Desktop/Web:
1. Go to Claude Settings → MCP Servers
2. Add new server:
   - Name: `ai-assistant`
   - Command: `python`
   - Args: `mcp_server.py`
   - Working Directory: `c:\Latest Environment (16.04.25)\my_new_env\AI Assistant`

## Available Tools

Once configured, I (Claude Code) can directly call:

| Tool | What it does |
|---|---|
| `play_youtube` | Play a song/video on YouTube |
| `search_web` | Search web via DuckDuckGo |
| `get_weather` | Get current weather |
| `get_news` | Get latest news headlines |
| `send_whatsapp` | Send WhatsApp message |
| `get_system_info` | Show CPU/RAM/disk usage |
| `get_time` | Get current time |
| `get_date` | Get today's date |
| `search_wikipedia` | Search Wikipedia |

## How It Works

### Flask App (Users):
```
User Voice Input → Web Speech API → Flask /api/ask → Ollama LLM → Tool Selection → Tool Execution → Voice Output
```

### MCP Server (Claude Code):
```
Claude Code → MCP Protocol → Tool Call → Direct Execution → Result → Claude Code
```

**Key Benefit**: Everything runs locally. No API keys, no internet dependencies (except for web search/weather/news which require internet but no credentials).

## Testing

### Test Flask App:
1. Open http://localhost:8000
2. Say "What time is it?" → Should hear current time
3. Say "Play Bohemian Rhapsody" → Should play on YouTube
4. Say "What's the weather?" → Should show weather

### Test MCP Server:
Once Claude Code is configured, you can ask me (Claude) things like:
- "Use the tools to search for Python tutorials"
- "Get the current system info"
- "What's the weather right now?"
- "Send a WhatsApp to mom: Hello!"

I will execute these tools directly on your local system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│         Your Local PC                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Ollama (llama3.2 LLM)                             │
│  ├── Not an API, direct binary                     │
│  └── Runs on your machine                          │
│                                                     │
│  ┌──────────────────┐    ┌──────────────────┐     │
│  │   Flask App      │    │   MCP Server     │     │
│  ├──────────────────┤    ├──────────────────┤     │
│  │ Web Interface    │    │ Claude Code      │     │
│  │ (http://...)     │    │ Integration      │     │
│  │                  │    │                  │     │
│  │ Tools:           │    │ Same Tools:      │     │
│  │ • play_youtube   │    │ • play_youtube   │     │
│  │ • search_web     │    │ • search_web     │     │
│  │ • get_weather    │    │ • get_weather    │     │
│  │ • send_whatsapp  │    │ • send_whatsapp  │     │
│  │ • etc.           │    │ • etc.           │     │
│  └──────────────────┘    └──────────────────┘     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Troubleshooting

**Flask shows "Site cannot be reached":**
- Check: http://localhost:8000 (use http, not https)
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito window
- Verify Flask window shows "Running on http://127.0.0.1:8000"

**MCP Server doesn't connect:**
- Verify mcp package installed: `pip show mcp`
- Check working directory path in settings
- Restart Claude Code after changing settings

**Tools not executing:**
- Check Ollama is running: `ollama list`
- Verify contacts.json exists for WhatsApp tool
- Check Flask/MCP windows for error messages

**Ollama errors:**
- Make sure Ollama app is running or `ollama serve` in terminal
- Pull model if missing: `ollama pull llama3.2`
