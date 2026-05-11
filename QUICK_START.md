# Quick Start Guide

## ✓ Both Systems Running Now!

### 1. Flask Web App (for Users)
**URL:** http://localhost:8000

**Features:**
- Voice input/output via Web Speech API
- Real-time system monitoring (CPU, RAM, disk)
- Contact management
- Chat interface
- Multiple spinner animations for different operations

**Test it:**
- Open browser to http://localhost:8000
- Click microphone button and say: "What time is it?"
- Should hear the current time back

---

### 2. MCP Server (for Claude Code)
**Status:** Running locally on stdio (no port, no API)

**How I (Claude Code) can help:**
Ask me things like:
- "Search for Python machine learning tutorials"
- "Get the current weather"
- "Check my system performance"
- "Send a WhatsApp to mom: Hello!"
- "What's the latest news?"
- "Play Bohemian Rhapsody"

I'll execute these directly on your local PC via the MCP server.

---

## Setup for Claude Code Integration

Choose your Claude environment:

### Option A: Claude Code VSCode Extension
1. Open `.vscode/settings.json` in your workspace
2. Add this:
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
3. Restart VSCode
4. I'll have access to all tools

### Option B: Claude.ai Web App
1. Go to claude.ai
2. Settings → MCP Servers (if available)
3. Add server configuration from Option A above
4. Restart and chat with me

### Option C: Claude Desktop App
1. Locate the config file:
   - **macOS/Linux:** `~/.config/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
2. Add to `mcpServers`:
```json
"ai-assistant": {
  "command": "python",
  "args": ["mcp_server.py"],
  "cwd": "c:\\Latest Environment (16.04.25)\\my_new_env\\AI Assistant"
}
```
3. Restart Claude Desktop

---

## Available Tools I Can Call

| Tool | Example | What Happens |
|---|---|---|
| `play_youtube` | "Play Bohemian Rhapsody" | Opens YouTube and plays it on your PC |
| `search_web` | "Search for Python tutorials" | DuckDuckGo web search results |
| `get_weather` | "What's the weather?" | Current weather info |
| `get_news` | "Get news headlines" | Latest news from Google News |
| `send_whatsapp` | "Send WhatsApp to mom: Hi!" | Sends message via WhatsApp (if browser is open) |
| `get_system_info` | "Check my system" | CPU, RAM, disk usage |
| `get_time` | "What time is it?" | Current time |
| `get_date` | "What's the date?" | Today's date |
| `search_wikipedia` | "Who is Albert Einstein?" | Wikipedia summary |

---

## Architecture Summary

```
Local PC Running 2 Systems:

1. Flask App (Web Interface)
   └─ User: Says "What time is it?" via microphone
   └─ Backend: Ollama LLM processes intent
   └─ Executes: get_time tool
   └─ Returns: "It's 2:30 PM"
   
2. MCP Server (Claude Code Integration)
   └─ Claude Code: Asks "What time is it?"
   └─ MCP Protocol: Routes to mcp_server.py
   └─ Executes: get_time tool
   └─ Returns: "It's 2:30 PM"

Both share:
├─ Same tools (no duplication)
├─ Local Ollama (llama3.2 model)
├─ contacts.json for WhatsApp
└─ No API keys, no internet (except web search/weather)
```

---

## Troubleshooting

### Flask site not loading?
```powershell
# Check if running
Get-Process | Where-Object { $_.ProcessName -eq "python" }

# If not, restart:
python app.py
```

### MCP Server not connecting?
```bash
# Check it's running in its window
# Verify settings path is correct (no spaces issues on Windows)
# Make sure `pip install mcp` succeeded
pip show mcp
```

### Tools not working?
1. Check Ollama is running: `ollama list` should show llama3.2
2. Check contacts.json exists (for WhatsApp tool)
3. Check both server windows for error messages

### Need to stop everything?
- Close both PowerShell windows where servers are running
- Or: `Get-Process python | Stop-Process`

---

## Next Steps

1. **Test Flask Web App**: Open http://localhost:8000 and try voice commands
2. **Configure Claude Code**: Follow setup instructions for your platform
3. **Test MCP Server**: Ask me (Claude Code) to use the tools
4. **Read SETUP.md**: Full documentation with all details

Enjoy your local AI assistant! 🚀
