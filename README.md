# 🤖 AI Virtual Assistant - Multi-Agent Architecture

**A powerful AI assistant with intelligent multi-agent routing, smart app/website discovery, and web scraping capabilities. Runs 100% locally on your PC.**

---

## ✨ Key Features

### 🎯 Smart "Open" Command
- **Priority-based routing:** Apps first, then websites
- **Intelligent discovery:** Finds any application on your PC or searches for any website
- Examples:
  - `"open notepad"` → Opens Notepad application
  - `"open chrome"` → Opens Chrome browser
  - `"open medium"` → Searches & opens medium.com
  - `"open cnn"` → Searches & opens cnn.com

### 📰 News & Headlines Scraping
- Scrapes websites with BeautifulSoup
- Extracts top 10 headlines from any news site
- Examples:
  - `"headlines from bbc"` → Returns BBC news headlines
  - `"news from cnn"` → Returns CNN news headlines
  - `"top news from techcrunch"` → Returns TechCrunch headlines

### 🏗️ Multi-Agent Architecture
- **SystemAgent** — Battery, network, processes, WiFi, Bluetooth, volume, brightness, wallpaper, updates
- **AppAgent** — Opening applications via 6-layer smart discovery
- **WebAgent** — Website search, news scraping, content fetching
- **InfoAgent** — Time, date, weather, news, Wikipedia, YouTube, files, LLM fallback

### ⚡ Pattern-Based Routing (Super Fast)
- <1ms regex pattern matching
- First-match-wins priority ordering
- LLM only as last resort for unrecognized queries

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Ollama (or LM Studio / Jan.ai)
- Windows 10/11

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ratulpaul018/HexSoftwares_AI_Powered_Virtual_Assistant.git
cd HexSoftwares_AI_Powered_Virtual_Assistant
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start Ollama:**
```bash
ollama serve
# In another terminal, pull a model:
ollama pull llama2
```

4. **Run the Flask app:**
```bash
python app.py
```

5. **Access the web interface:**
Open http://localhost:8000 in your browser

---

## 📋 System Architecture

```
User Command
     ↓
PatternRouter (25+ compiled regex patterns)
     ├─ SystemAgent (hardware/OS queries)
     ├─ AppAgent (app discovery + opening)
     ├─ WebAgent (web search + news scraping)
     └─ InfoAgent (general info + LLM fallback)
     ↓
Tool Execution
     ├─ smart_open_app() — 6-layer app discovery
     ├─ search_and_get_top_url() — Google parsing
     ├─ scrape_website_headlines() — BeautifulSoup
     ├─ get_battery_status() — psutil
     ├─ get_network_status() — ifconfig + netstat
     └─ 20+ more tools
     ↓
Response to User
```

---

## 💡 Usage Examples

### Opening Applications
```
User: "open notepad"
→ AppAgent finds notepad.exe
→ Opens Notepad application
✓ Response: "✓ Opened notepad"

User: "launch chrome"
→ AppAgent finds chrome.exe
→ Opens Chrome browser
✓ Response: "✓ Opened chrome"
```

### Opening Websites
```
User: "open medium"
→ Not an app → WebAgent takes over
→ Tries www.medium.com (HEAD request)
→ Found! Opens website with content preview
✓ Response: "✓ Opened: medium\n  https://www.medium.com"

User: "open amazon website"
→ SITE_MAP lookup finds amazon.com
→ Opens with website info
✓ Response: "✓ Opened https://amazon.com"
```

### Getting Headlines
```
User: "headlines from bbc"
→ WebAgent detects news pattern
→ Finds BBC website
→ Scrapes with BeautifulSoup
→ Extracts top 10 headlines
✓ Response: "📰 Latest news headlines:\n  • Cabinet split...\n  • Trump-Xi summit..."

User: "news from techcrunch"
→ Searches for TechCrunch
→ Scrapes and returns headlines
✓ Response: "📰 Latest news headlines:\n  • AI breakthrough...\n  • New startup..."
```

### System Commands
```
User: "battery status"
→ SystemAgent.get_battery_status()
✓ Response: "🔋 Battery: 85% (Charging) | Time remaining: 2h 30m"

User: "show running processes"
→ SystemAgent.get_running_processes()
✓ Response: "📊 Top processes by CPU/RAM: Chrome: 45%, Edge: 32%..."

User: "check network status"
→ SystemAgent.get_network_status()
✓ Response: "🌐 Network Status: Connected | IP: 192.168.1.100 | Data: 2.3GB down, 845MB up"
```

---

## 🔍 Smart App Discovery (6 Layers)

When you say `"open [app_name]"`, the system tries to find it in this order:

1. **Static Map Lookup** — Pre-configured apps (calc, notepad, chrome, etc.)
2. **Fuzzy Matching** — Similar names (difflib, cutoff 0.75)
3. **Windows Registry** — HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths
4. **Start Menu Scan** — .lnk files in AppData & ProgramData
5. **PATH Lookup** — where.exe for executables
6. **Program Files Walk** — Search common installation directories

---

## 🌐 Smart Website Discovery (2-Tier)

When you say `"open [something]"` and it's not an app:

1. **Direct Domain Detection** — Try www.name.com, name.com, www.name.org, name.net, name.io, etc.
   - Uses HEAD requests for instant detection
   - Accepts HTTP status < 500 (site exists if not server error)
   - ~100-500ms per check

2. **Google Search Parsing** — If direct lookup fails
   - Searches Google
   - Parses HTML with BeautifulSoup
   - Extracts top result URL
   - Filters out Google domains, translate, etc.

3. **SITE_MAP Registry** — Pre-registered websites
   - Wikipedia, Amazon, GitHub, YouTube, Netflix, etc.
   - Instant lookup from dictionary

---

## 🎯 Pattern Router Details

**25+ Compiled Regex Patterns** (evaluated in priority order):

| Priority | Pattern | Agent | Examples |
|----------|---------|-------|----------|
| 1 | `open ... website` | Web | "open cnn website" |
| 2 | `open ... url` | Web | "open github.com" |
| 3 | `battery/charge` | System | "battery status" |
| 4 | `network/ip` | System | "network status" |
| 5 | `process/running` | System | "running processes" |
| 6 | `wifi/bluetooth` | System | "turn on wifi" |
| 7 | `volume/brightness` | System | "set volume 50" |
| 8 | `open [app]` | App | "open notepad" |
| 9 | `news/headlines` | Web | "news from bbc" |
| 10+ | Various | Info | time, weather, etc. |
| Last | Fallback | Info | LLM general chat |

---

## 📊 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Pattern matching | <1ms | Compiled regex |
| App discovery | ~100ms | Direct map lookup |
| Direct domain check | 500-1000ms | HEAD requests |
| Google search + parse | 2-3s | Network dependent |
| News scraping | 2-5s | Website dependent |
| LLM response | 1-10s | Model dependent |

---

## 🛠️ Available Tools

### System Tools
- `get_battery_status()` — Battery percentage, charging status, time remaining
- `get_network_status()` — IP address, data usage, connection status
- `get_running_processes()` — Top CPU/RAM consuming processes
- `get_system_info()` — CPU/RAM/disk usage percentages
- `control_wifi()` — Turn WiFi on/off
- `control_bluetooth()` — Turn Bluetooth on/off
- `set_volume()` — Set system volume level
- `set_brightness()` — Set screen brightness
- `change_wallpaper()` — Change desktop wallpaper
- `check_windows_updates()` — Check for Windows updates

### App & Web Tools
- `smart_open_app()` — 6-layer app discovery and opening
- `search_and_get_top_url()` — Google search + domain detection
- `scrape_website_headlines()` — Extract headlines with BeautifulSoup
- `fetch_website_info()` — Get title, description, headings, content
- `open_website()` — Open browser and fetch website info

### Information Tools
- `get_time()` — Current time
- `get_date()` — Current date
- `get_weather()` — Current weather
- `get_news()` — Latest news headlines
- `search_wikipedia()` — Wikipedia search
- `play_youtube()` — Play YouTube videos
- `web_search_with_content()` — Search web with results

---

## 📁 Project Structure

```
HexSoftwares_AI_Powered_Virtual_Assistant/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── templates/
│   └── index.html                 # Web interface
├── mcp_server_universal.py        # MCP server for Claude Code
├── tools_extended.py              # Extended tool definitions
├── SETUP.md                       # Detailed setup instructions
├── QUICK_START.md                 # Quick reference
├── FREE_FOREVER_GUIDE.md          # Backend configuration guide
└── .vscode/
    └── settings.json              # Claude Code integration config
```

---

## 🔗 API Endpoints

### POST /api/ask
Send a command and get a response.

**Request:**
```json
{
  "command": "open medium",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "response": "✓ Opened: medium\n  https://www.medium.com",
  "session_id": "user123"
}
```

### GET /api/system
Get system status information.

### POST /api/contacts
Manage contacts.

---

## 🔐 Privacy & Security

- ✅ **100% local execution** — Nothing sent to external servers (except web search/weather/news)
- ✅ **No API keys required** — Uses local Ollama LLM
- ✅ **Open source** — Full transparency
- ✅ **User controls data** — All data stored locally
- ✅ **No telemetry** — No tracking or analytics

---

## 🚀 Performance Optimization

- **Pattern matching** — Compiled regex patterns for instant evaluation
- **First-match-wins** — Stops searching after first pattern match
- **LLM as fallback** — Only invoked for unrecognized queries
- **Caching** — Session management and app discovery caching
- **Async operations** — Non-blocking web scraping and searches

---

## 🐛 Troubleshooting

### Flask app not starting?
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process using port 8000
taskkill /PID <PID> /F
```

### Ollama connection error?
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull a model
ollama pull llama2
```

### App not opening?
- Check if app name is correct
- Verify app is installed
- Look at logs for details

### Website not opening?
- Check internet connection
- Verify domain name is correct
- Try direct URL in browser

---

## 📖 Additional Resources

- **FREE_FOREVER_GUIDE.md** — Complete backend setup guide
- **SETUP.md** — Detailed technical setup
- **QUICK_START.md** — Quick reference guide
- **SYSTEM_SUMMARY.md** — Architecture overview

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit PRs for:
- New tools and features
- Bug fixes
- Documentation improvements
- Performance optimizations

---

## 📜 License

This project is open source and available under the MIT License.

---

## 🎉 You Now Have

✅ **Smart app/website discovery** — Intelligently distinguishes apps from websites

✅ **6-layer app discovery** — Finds any application on your PC

✅ **Google search integration** — Finds and opens any website

✅ **News scraping** — Extract headlines from any website

✅ **Multi-agent architecture** — Specialized agents for different domains

✅ **Pattern-based routing** — Super-fast <1ms pattern matching

✅ **Zero external dependencies** — Runs completely locally

✅ **Extensible design** — Easy to add new agents and tools

---

**Built with ❤️ for privacy-conscious developers**

Get started: `python app.py` and open http://localhost:8000

Questions? Check the documentation files for detailed instructions!
