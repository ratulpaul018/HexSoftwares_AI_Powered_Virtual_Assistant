# 🤖 AI Virtual Assistant - Multi-Agent Architecture

**A powerful, intelligent AI assistant with multi-agent routing, smart app discovery, and web scraping. Runs 100% locally on your Windows PC with Ollama or Claude AI.**

---

## ✨ Features

### 🎯 Smart Command Routing
- **AppAgent** — Open any application on your PC
- **SystemAgent** — Battery, network, WiFi, Bluetooth, brightness, volume, system info
- **WebAgent** — Web search, website opening, news scraping, headlines
- **InfoAgent** — Time, date, weather, news, Wikipedia, YouTube, file operations

### 🏗️ Multi-Agent Architecture
**Intelligent pattern-based routing** with 25+ compiled regex patterns:
- Priority-ordered pattern matching
- <1ms pattern evaluation (super-fast)
- LLM fallback for unrecognized queries only
- First-match-wins strategy

### 🚀 Key Capabilities

#### 🔍 Smart App Opening (6-Layer Discovery)
```
User: "open notepad"
  ↓
1. Static app map lookup (instant)
2. Fuzzy matching (difflib)
3. Windows Registry scan
4. Start Menu .lnk files
5. PATH environment variable
6. Program Files walk
  ↓
✓ Opens Notepad
```

#### 🌐 Website Discovery
```
User: "open medium"
  ↓
1. Try direct domains (www.medium.com, medium.com, etc.)
2. Google search + HTML parsing
3. SITE_MAP registry lookup
  ↓
✓ Opens https://www.medium.com
```

#### 📰 News & Headlines Scraping
```
User: "headlines from bbc"
  ↓
1. Detect news pattern
2. Find website
3. Scrape with BeautifulSoup
4. Extract h1-h4 headlines
  ↓
✓ Returns top 10 headlines
```

#### 💾 File Operations
- Create, read, write, rename, move, delete files
- Create, list directories
- Full path support

#### 📊 System Monitoring
- Battery status & charging info
- Network IP addresses & data usage
- Running processes (CPU/RAM)
- CPU/RAM/disk usage percentages
- Windows update check

#### 🎛️ System Control
- WiFi on/off
- Bluetooth on/off
- Volume control (0-100)
- Screen brightness (0-100)
- Desktop wallpaper change

---

## 🛠️ Available Tools

### System Tools (SystemAgent)
| Tool | Description | Example |
|------|-------------|---------|
| `get_battery_status()` | Battery %, charging, time remaining | "battery status" |
| `get_network_status()` | IP addresses, network adapters, data usage | "network status" |
| `get_running_processes()` | Top CPU/RAM processes | "running processes" |
| `get_system_info()` | CPU/RAM/disk usage | "system info" |
| `control_wifi()` | Turn WiFi on/off | "turn on wifi" |
| `control_bluetooth()` | Turn Bluetooth on/off | "enable bluetooth" |
| `set_volume()` | Set system volume (0-100) | "set volume 50" |
| `set_brightness()` | Set screen brightness (0-100) | "brightness 75" |
| `change_wallpaper()` | Change desktop wallpaper | "change wallpaper" |
| `check_windows_updates()` | Check for Windows updates | "windows updates" |

### App Management Tools (AppAgent)
| Tool | Description | Example |
|------|-------------|---------|
| `smart_open_app()` | Open application (6-layer discovery) | "open chrome" |
| | | "launch notepad" |
| | | "run calculator" |

### Web Tools (WebAgent)
| Tool | Description | Example |
|------|-------------|---------|
| `search_and_get_top_url()` | Search Google, extract top result | Internal |
| `open_website()` | Open website + fetch info | "open medium" |
| `fetch_website_info()` | Get title, description, headings | Internal |
| `web_search_with_content()` | DuckDuckGo search with results | "search python tutorials" |
| `scrape_website_content()` | Scrape website with query | Internal |
| `scrape_website_headlines()` | Extract headlines from website | "headlines from bbc" |

### Information Tools (InfoAgent)
| Tool | Description | Example |
|------|-------------|---------|
| `get_time()` | Current time | "what time is it" |
| `get_date()` | Today's date | "what's the date" |
| `get_weather()` | Current weather & temperature | "weather today" |
| `get_news()` | Latest news headlines | "news" |
| `search_wikipedia()` | Wikipedia search | "who is albert einstein" |
| `play_youtube()` | Play YouTube video | "play despacito" |
| `send_whatsapp()` | Send WhatsApp message | "send message to john" |

### File Operation Tools (InfoAgent)
| Tool | Description | Example |
|------|-------------|---------|
| `create_folder()` | Create new folder | "create folder test" |
| `list_files()` | List directory contents | "list files" |
| `read_file()` | Read file content | "read file.txt" |
| `write_file()` | Write to file | Internal |
| `rename_file()` | Rename file | Internal |
| `move_file()` | Move file to location | Internal |
| `delete_file()` | Delete file | Internal |

---

## 🚀 Getting Started

### Prerequisites
- **Python** 3.8 or higher
- **Ollama** (download from ollama.ai) OR Claude API key
- **Windows 10/11**

### Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/ratulpaul018/HexSoftwares_AI_Powered_Virtual_Assistant.git
cd HexSoftwares_AI_Powered_Virtual_Assistant
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Start Ollama (if using local LLM)
```bash
ollama serve

# In another terminal, pull a model:
ollama pull llama2
```

#### Step 4: Run the Application
```bash
python app.py
```

#### Step 5: Open in Browser
```
http://localhost:8000
```

---

## 📋 Usage Examples

### Opening Applications
```
User: "open notepad"
→ Finds notepad.exe
→ Opens application
✓ "✓ Opened notepad"

User: "launch chrome"
→ Finds chrome.exe
→ Opens Chrome browser
✓ "✓ Opened chrome"

User: "run calculator"
→ Finds calc.exe
→ Opens Calculator
✓ "✓ Opened calculator"
```

### System Status
```
User: "battery status"
✓ "🔋 Battery: 85% | Charging: Yes | Time: 2h 30m remaining"

User: "network status"
✓ "🌐 Network Status: Connected | IP: 192.168.1.100 | Data: 2.3GB ↓ 845MB ↑"

User: "running processes"
✓ "📊 Top processes by CPU/RAM: Chrome: 45% | Firefox: 32% | Teams: 18%"

User: "system info"
✓ "💻 CPU: 35% | RAM: 8GB/16GB (50%) | Disk: 450GB/512GB (88%)"
```

### Website Operations
```
User: "open medium"
→ Searches for medium.com
→ Finds www.medium.com
→ Opens website with info preview
✓ "✓ Opened: medium\n  https://www.medium.com"

User: "open github website"
→ Opens github.com
→ Fetches website info
✓ "✓ Opened https://github.com"

User: "headlines from bbc"
→ Scrapes BBC website
→ Extracts headlines
✓ "📰 Latest news headlines:
   • Cabinet split as Home Secretary...
   • How Trump-Xi summit could set..."
```

### Information Queries
```
User: "what time is it"
✓ "🕐 Current time: 2:30 PM"

User: "what's the date"
✓ "📅 Today's date: Monday, May 12, 2025"

User: "weather"
✓ "☀️ Weather: Sunny | Temperature: 72°F | Humidity: 65%"

User: "who is albert einstein"
✓ "Wikipedia: Albert Einstein was a German-born theoretical physicist..."
```

### File Operations
```
User: "create folder mynotes"
✓ "✓ Created folder: mynotes"

User: "list files"
✓ "📁 Files in Desktop:
   • document.txt
   • photo.jpg
   • project.zip"

User: "read notes.txt"
✓ "📄 Content of notes.txt:
   Remember to buy milk
   Call dentist on Friday..."
```

---

## 🏗️ Architecture

### PatternRouter (Pattern-Based Dispatcher)
```
User Input
    ↓
PatternRouter (25+ compiled regex patterns)
    ├─ Pattern 1: "open ... website" → WebAgent
    ├─ Pattern 2: "battery/charge" → SystemAgent
    ├─ Pattern 3: "network/ip" → SystemAgent
    ├─ Pattern 4: "process/running" → SystemAgent
    ├─ Pattern 5: "wifi/bluetooth" → SystemAgent
    ├─ Pattern 6: "volume/brightness" → SystemAgent
    ├─ Pattern 7: "open [app]" → AppAgent
    ├─ Pattern 8: "news/headlines" → WebAgent
    ├─ ... (17+ more patterns)
    └─ Fallback: InfoAgent (LLM)
    ↓
Tool Execution
    ↓
Response
```

### Agent Responsibilities

**SystemAgent**
- Hardware & OS control
- Battery, network, WiFi, Bluetooth
- Volume, brightness, wallpaper
- Windows updates

**AppAgent**
- Multi-layer app discovery
- Application launching
- 6-strategy executable finding

**WebAgent**
- Website opening
- Web searching
- News scraping
- Headlines extraction

**InfoAgent**
- Time, date, weather
- News, Wikipedia, YouTube
- File operations
- LLM fallback for general chat

---

## 📡 API Endpoints

### POST /api/ask
Send a voice command and get a response.

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

**Response:**
```json
{
  "cpu_usage": 35,
  "ram_usage": 50,
  "disk_usage": 88,
  "battery": 85,
  "charging": true
}
```

### POST /api/contacts
Manage contacts (create, read, update, delete).

---

## ⚙️ Configuration

### LLM Selection

**Using Ollama (Local - Free):**
```bash
ollama serve
# In another terminal:
ollama pull llama2
```

**Using Claude (Requires API key):**
```bash
# Set environment variable
$env:ANTHROPIC_API_KEY = "your-api-key-here"
python app.py
```

---

## 📊 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Pattern matching | <1ms | Compiled regex |
| App discovery | ~100ms | Instant map lookup |
| Website opening | ~2-3s | Direct domain + scraping |
| Headlines scraping | ~2-5s | BeautifulSoup parsing |
| LLM response | ~1-10s | Ollama/Claude dependent |

---

## 🔧 Troubleshooting

### Flask App Won't Start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Or use different port in app.py
app.run(port=8001)
```

### Ollama Connection Error
```bash
# Ensure Ollama is running
ollama serve

# In another terminal, pull a model
ollama pull llama2

# Test the connection
curl http://localhost:11434
```

### App Not Opening
- Check if application name is correct
- Verify app is installed on the system
- Look for error messages in console

### Website Not Opening
- Check internet connection
- Verify domain name/website exists
- Try opening URL directly in browser

---

## 📝 File Structure

```
HexSoftwares_AI_Powered_Virtual_Assistant/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/
│   └── index.html           # Web interface
└── .git/                    # Version control
```

---

## 🔐 Privacy & Security

- ✅ **100% Local** — Runs entirely on your PC
- ✅ **No Cloud** — Nothing sent to external servers (except web search)
- ✅ **Open Source** — Full code transparency
- ✅ **Your Data** — Complete control over all information
- ✅ **Offline** — Works without internet (except weather/news/web search)

---

## 🎯 Key Highlights

- **Smart Routing** — Pattern-based dispatch with LLM fallback
- **Super Fast** — <1ms pattern matching, instant response
- **6-Layer App Discovery** — Finds any application on your PC
- **Website Intelligence** — Searches Google, opens websites, scrapes content
- **No Dependencies** — All standard Python libraries + minimal packages
- **Extensible** — Easy to add new agents and patterns

---

## 📖 Documentation

- This README covers all features and usage
- Check code comments for implementation details
- Review `app.py` for complete tool definitions

---

## 🎉 You Now Have

✅ **Multi-agent AI assistant** — 4 specialized agents  
✅ **Smart app discovery** — 6-layer search strategy  
✅ **Web integration** — Search, open, scrape websites  
✅ **System control** — Battery, network, WiFi, brightness, volume  
✅ **File management** — Create, read, write, organize files  
✅ **Information services** — Weather, news, Wikipedia, YouTube  
✅ **Super-fast routing** — Pattern-based dispatch (<1ms)  
✅ **Local execution** — 100% privacy-preserving  

---

## 🚀 Quick Commands

```
# Open applications
"open chrome"
"launch notepad"
"run calculator"

# Check system
"battery status"
"network status"
"running processes"
"system info"

# Website operations
"open medium"
"open github website"
"headlines from bbc"
"search python tutorials"

# System control
"turn on wifi"
"set volume 50"
"brightness 75"
"change wallpaper"

# Information
"what time is it"
"weather"
"who is albert einstein"
"play despacito"
```

---

**Built with ❤️ for privacy-conscious Windows users**

**Get started:** `python app.py` → Open http://localhost:8000

Questions? Check the code or error messages for detailed information!
