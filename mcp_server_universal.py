"""
Universal MCP Server - Works with multiple free, open-source LLM backends
Supports: Ollama, LM Studio, Jan.ai
No Claude subscription required - completely free and local
"""

import asyncio
import json
import datetime
import wikipedia
import psutil
from bs4 import BeautifulSoup
import requests
import pywhatkit
import os
from typing import Any
from mcp.server import Server
from mcp.types import TextContent, ToolResult
import subprocess
import webbrowser

# Configuration - Change these to use different LLM backends
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")  # ollama, lm_studio, jan
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")

print(f"[MCP Server] Using backend: {LLM_BACKEND}")
print(f"[MCP Server] Model: {LLM_MODEL}")
print(f"[MCP Server] URL: {LLM_BASE_URL}")

# ==================== LLM Integration ====================

def get_llm_response(prompt: str) -> str:
    """Get response from any supported LLM backend"""
    try:
        if LLM_BACKEND == "ollama":
            import ollama
            response = ollama.generate(
                model=LLM_MODEL,
                prompt=prompt,
                stream=False
            )
            return response.get('response', '').strip()

        elif LLM_BACKEND == "lm_studio":
            # LM Studio compatible endpoint (OpenAI-like API)
            response = requests.post(
                f"{LLM_BASE_URL}/v1/completions",
                json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['text'].strip()
            else:
                return f"LM Studio error: {response.status_code}"

        elif LLM_BACKEND == "jan":
            # Jan.ai compatible endpoint
            response = requests.post(
                f"{LLM_BASE_URL}/v1/chat/completions",
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"Jan.ai error: {response.status_code}"

        else:
            return f"Unknown LLM backend: {LLM_BACKEND}"

    except Exception as e:
        return f"LLM Error: {str(e)}"

# ==================== EXTENDED TOOLS (Agentic) ====================

def open_website(url: str) -> str:
    """Open a website in the default browser."""
    try:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url
        webbrowser.open(url)
        return f"✓ Opened {url} in your browser"
    except Exception as e:
        return f"✗ Could not open website: {str(e)}"

def open_application(app_name: str) -> str:
    """Open an application or website by name. Supports regular apps, Windows apps, and UWP Store apps."""
    try:
        app_map = {
            # Web services
            'gmail': 'https://gmail.com',
            'google': 'https://google.com',
            'youtube': 'https://youtube.com',
            'github': 'https://github.com',
            'twitter': 'https://twitter.com',
            'facebook': 'https://facebook.com',
            'linkedin': 'https://linkedin.com',
            'reddit': 'https://reddit.com',
            # Windows system apps (protocols)
            'settings': 'ms-settings:',
            'whatsapp': 'whatsapp:',
            # Desktop apps
            'calculator': 'calc.exe',
            'calc': 'calc.exe',
            'notepad': 'notepad.exe',
            'paint': 'mspaint.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'vs code': 'code',
            'vscode': 'code',
        }

        app_lower = app_name.lower().strip()

        # Check if it's a web service
        if app_lower in app_map and app_map[app_lower].startswith('https://'):
            return open_website(app_map[app_lower])

        # Get target from map or use app name
        target = app_map.get(app_lower, app_name)

        # Try protocol handlers (ms-settings:, whatsapp:, etc.)
        if target.endswith(':'):
            try:
                subprocess.run(['cmd', '/c', f'start {target}'], check=False, timeout=5)
                return f"✓ Opened {app_name}"
            except:
                pass

        # Try direct execution
        try:
            subprocess.Popen(target)
            return f"✓ Opened {app_name}"
        except (FileNotFoundError, OSError):
            pass

        # Try Windows 'where' command to find in PATH
        try:
            result = subprocess.run(
                ['where', target],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                app_path = result.stdout.strip().split('\n')[0]
                subprocess.Popen(app_path)
                return f"✓ Opened {app_name}"
        except:
            pass

        # Try Windows Registry for installed apps
        try:
            import winreg
            registry_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\App Paths'),
                (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\App Paths'),
            ]

            for hkey, reg_path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            subkey_name = winreg.EnumKeyEx(key, i)
                            if target.lower() in subkey_name[0].lower() or app_lower in subkey_name[0].lower():
                                try:
                                    with winreg.OpenKey(hkey, f"{reg_path}\\{subkey_name[0]}") as subkey:
                                        path = winreg.QueryValueEx(subkey, None)
                                        if path and path[0]:
                                            subprocess.Popen(path[0])
                                            return f"✓ Opened {app_name}"
                                except:
                                    pass
                except:
                    pass
        except:
            pass

        # Try PowerShell to find and launch UWP/Store apps
        try:
            ps_script = f"""
            # Try to find and launch Microsoft Store app
            $package = Get-AppxPackage -Name '*{target}*' -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($package) {{
                $PackageFullName = $package.PackageFullName
                Start-Process "explorer.exe" -ArgumentList "shell:appsFolder\\$($package.PackageFamilyName)!App" -ErrorAction SilentlyContinue
                exit 0
            }}

            # Try as protocol handler
            try {{
                Start-Process "{target}" -ErrorAction SilentlyContinue
                exit 0
            }} catch {{}}

            exit 1
            """
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return f"✓ Opened {app_name}"
        except:
            pass

        # Last resort: try cmd /c start which uses Windows file associations
        try:
            subprocess.run(['cmd', '/c', f'start {target}'], check=False, timeout=5)
            return f"✓ Opened {app_name}"
        except:
            pass

        return f"✗ Could not open {app_name}: Application not found on system"

    except Exception as e:
        return f"✗ Could not open {app_name}: {str(e)}"

# ==================== TOOLS ====================

def play_youtube(query: str) -> str:
    """Play a song or video on YouTube."""
    try:
        if query and len(query.strip()) > 0:
            pywhatkit.playonyt(query)
            return f"Now playing {query} on YouTube. Enjoy!"
        else:
            return "Please specify a song or video name."
    except Exception as e:
        return f"Could not play video: {str(e)}"

def search_web(query: str) -> str:
    """Search the web for information."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(
            'https://duckduckgo.com/html/',
            params={'q': query},
            headers=headers,
            timeout=10
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []

        for result in soup.find_all('div', {'class': 'result'}):
            title_elem = result.find('a', {'class': 'result__a'})
            snippet_elem = result.find('a', {'class': 'result__snippet'})

            if title_elem and snippet_elem:
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True)
                results.append(f"{title}: {snippet}")
                if len(results) >= 2:
                    break

        if results:
            return "Search results: " + ". ".join(results)
        else:
            return f"No detailed results found for '{query}'."
    except Exception as e:
        return f"Web search failed: {str(e)}"

def get_weather() -> str:
    """Get current weather information."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://wttr.in/?format=j1', headers=headers, timeout=5)
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        condition = current['weatherDesc'][0]['value']
        return f"Current weather: {condition} with temperature {temp}°C"
    except:
        return "Unable to fetch weather information at the moment."

def get_news() -> str:
    """Get latest news headlines."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://news.google.com/', headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines = []

        for article in soup.find_all('a', {'data-n-click': True})[:3]:
            title = article.get_text(strip=True)
            if title and len(title) > 10:
                headlines.append(title)

        if headlines:
            return "Latest news headlines: " + ". ".join(headlines[:2])
        else:
            return "Could not fetch latest news."
    except:
        return "Unable to fetch news at the moment."

def send_whatsapp(contact_name: str, message: str) -> str:
    """Send a WhatsApp message to a contact."""
    try:
        contacts_file = "contacts.json"
        if os.path.exists(contacts_file):
            with open(contacts_file, 'r') as f:
                contacts = json.load(f)
        else:
            contacts = {}

        phone = contacts.get(contact_name.lower())
        if not phone:
            return f"Contact '{contact_name}' not found. Available: {', '.join(contacts.keys())}"

        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True)
        return f"WhatsApp message sent to {contact_name}: {message}"
    except Exception as e:
        return f"Failed to send WhatsApp message: {str(e)}"

def get_system_info() -> str:
    """Get system performance information."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        info = (
            f"System Info: CPU {cpu_percent}% usage ({cpu_count} cores), "
            f"RAM {memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB, "
            f"Disk {disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB"
        )
        return info
    except Exception as e:
        return f"Could not get system info: {str(e)}"

def get_time() -> str:
    """Get the current time."""
    return f"Current time: {datetime.datetime.now().strftime('%I:%M %p')}"

def get_date() -> str:
    """Get today's date."""
    return f"Today's date: {datetime.datetime.now().strftime('%A, %B %d, %Y')}"

def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information."""
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except wikipedia.exceptions.DisambiguationError:
        return f"Multiple results found for '{query}'. Please be more specific."
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{query}'."
    except Exception as e:
        return f"Wikipedia search error: {str(e)}"

def set_brightness(level: int) -> str:
    """Set screen brightness using multiple methods (WMI, nircmd, screen-brightness-control)."""
    try:
        level = max(0, min(100, level))

        # Method 1: Try WMI (Windows built-in)
        try:
            ps_script = f"""
            $monitors = Get-WmiObject WmiMonitorBrightnessSetting -Namespace root\\wmi -ErrorAction SilentlyContinue
            $adjusted = 0
            foreach ($monitor in $monitors) {{
                try {{
                    $monitor.WmiSetBrightness(1, {level})
                    $adjusted++
                }} catch {{}}
            }}
            if ($adjusted -gt 0) {{ exit 0 }} else {{ exit 1 }}
            """
            result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return f"✓ Brightness adjusted to {level}%"
        except:
            pass

        # Method 2: Try nircmd (lightweight command-line tool)
        try:
            nircmd_paths = [
                'nircmd.exe',
                os.path.join(os.path.dirname(__file__), 'tools', 'nircmd.exe'),
                r'C:\Windows\nircmd.exe',
                os.path.expandvars(r'%PROGRAMFILES%\NirCmd\nircmd.exe'),
            ]
            for nircmd_path in nircmd_paths:
                try:
                    result = subprocess.run([nircmd_path, 'setbrightness', str(level)], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return f"✓ Brightness adjusted to {level}%"
                except:
                    pass
        except:
            pass

        # Method 3: Try screen-brightness-control library
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            return f"✓ Brightness adjusted to {level}%"
        except ImportError:
            pass
        except Exception as e:
            pass

        # Method 4: Try Windows Registry approach for some monitors
        try:
            ps_script = f"""
            try {{
                $brightness = {level}
                Add-Type -Assembly System.Windows.Forms
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen
                # Try alternative WMI namespace
                $result = Invoke-WmiMethod -Namespace "root\\cimv2\\power" -Class Win32_Battery -Name SetBrightness -ArgumentList 1, $brightness -ErrorAction SilentlyContinue
                if ($result) {{ exit 0 }}
            }} catch {{}}
            exit 1
            """
            result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return f"✓ Brightness adjusted to {level}%"
        except:
            pass

        return f"⚠️ Your monitor/graphics driver doesn't support brightness control. Try: 1) Install nircmd.exe (nirsoft.net/utils/nircmd.html) 2) Update graphics drivers 3) Check monitor DDC-CI support"

    except Exception as e:
        return f"✗ Could not adjust brightness: {str(e)}"

def set_volume(level: int) -> str:
    """Set system volume level (0-100)."""
    try:
        level = max(0, min(100, level))
        ps_script = f"""
        $volume = {level}
        $devices = Get-PnpDevice -Class AudioEndpoint | Where-Object {{$_.Status -eq 'OK'}}
        try {{
            [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync() | Out-Null
            $nAudio = New-Object -ComObject NanoAudioLib.AudioLib
            $nAudio.SetMasterVolume($volume / 100)
        }} catch {{
            Add-Type -AssemblyName PresentationCore
            [System.Windows.Media.SystemSounds]::Beep.Play()
        }}
        """
        subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], capture_output=True, timeout=10)
        return f"✓ Volume set to {level}%"
    except Exception as e:
        return f"✗ Could not set volume: {str(e)}"

def control_wifi(action: str) -> str:
    """Control Wi-Fi on/off. Requires admin privileges."""
    try:
        action_lower = action.lower().strip()
        should_enable = any(word in action_lower for word in ['on', 'enable', 'turn on', 'connect'])
        should_disable = any(word in action_lower for word in ['off', 'disable', 'turn off', 'disconnect'])

        if not should_enable and not should_disable:
            return "✗ Please specify 'on' or 'off' for Wi-Fi"

        # Try netsh with shell=True (requires admin)
        try:
            state = 'enabled' if should_enable else 'disabled'
            cmd = f'netsh interface set interface WiFi admin={state}'
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
            if result.returncode == 0 or 'Ok' in result.stdout:
                status = "on" if should_enable else "off"
                return f"✓ Wi-Fi turned {status}"
        except:
            pass

        # Try PowerShell
        try:
            ps_cmd = 'Enable-NetAdapter -Name Wi-Fi -Confirm:$false' if should_enable else 'Disable-NetAdapter -Name Wi-Fi -Confirm:$false'
            result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                status = "on" if should_enable else "off"
                return f"✓ Wi-Fi turned {status}"
        except:
            pass

        return "⚠️ ADMIN REQUIRED: Wi-Fi control needs admin privileges.\nRun Flask as Administrator to use this feature."

    except Exception as e:
        return f"✗ Wi-Fi error: {str(e)}"

def control_bluetooth(action: str) -> str:
    """Control Bluetooth on/off. Requires admin privileges."""
    try:
        action_lower = action.lower().strip()
        should_enable = any(word in action_lower for word in ['on', 'enable', 'turn on', 'connect'])
        should_disable = any(word in action_lower for word in ['off', 'disable', 'turn off', 'disconnect'])

        if not should_enable and not should_disable:
            return "✗ Please specify 'on' or 'off' for Bluetooth"

        # Try PowerShell with admin
        try:
            if should_enable:
                ps_cmd = """
                $radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().Result
                foreach ($radio in $radios) {
                    if ($radio.Kind -eq 'Bluetooth') {
                        $radio.SetStateAsync(1) | Out-Null
                    }
                }
                """
            else:
                ps_cmd = """
                $radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().Result
                foreach ($radio in $radios) {
                    if ($radio.Kind -eq 'Bluetooth') {
                        $radio.SetStateAsync(0) | Out-Null
                    }
                }
                """

            result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                status = "on" if should_enable else "off"
                return f"✓ Bluetooth turned {status}"
        except:
            pass

        return "⚠️ ADMIN REQUIRED: Bluetooth control needs admin privileges.\nRun Flask as Administrator to use this feature."

    except Exception as e:
        return f"✗ Bluetooth error: {str(e)}"

def control_sound(action: str) -> str:
    """Mute/unmute system sound."""
    try:
        action_lower = action.lower().strip()
        should_mute = any(word in action_lower for word in ['mute', 'off', 'silent', 'quiet'])
        should_unmute = any(word in action_lower for word in ['unmute', 'on', 'loud', 'sound on'])

        if not should_mute and not should_unmute:
            return "✗ Please specify 'mute' or 'unmute' for sound"

        # Use PowerShell to control volume/mute
        ps_script = f"""
        $AudioDevice = New-Object -ComObject AudioDeviceLib.AudioMmDeviceEnumerator
        $AudioDevice.GetDefaultAudioEndpoint(0,1).AudioEndpointVolume.Mute = ${should_mute}
        exit 0
        """

        result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_script],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            status = "muted" if should_mute else "unmuted"
            return f"✓ Sound {status}"

        return "⚠️ Sound control requires admin privileges"

    except Exception as e:
        return f"✗ Sound control error: {str(e)}"

def control_screen(action: str) -> str:
    """Lock or sleep the screen."""
    try:
        action_lower = action.lower().strip()
        should_lock = any(word in action_lower for word in ['lock', 'locked'])
        should_sleep = any(word in action_lower for word in ['sleep', 'sleep mode', 'suspend'])
        should_off = any(word in action_lower for word in ['off', 'turn off', 'monitor off'])

        if should_lock:
            # Lock the screen
            subprocess.run(['cmd', '/c', 'rundll32.exe user32.dll,LockWorkStation'],
                         capture_output=True, timeout=5)
            return "✓ Screen locked"

        elif should_sleep:
            # Sleep mode
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0', '1', '0'],
                         capture_output=True, timeout=5)
            return "✓ Computer going to sleep mode"

        elif should_off:
            # Turn off monitor (using nircmd or WMI)
            try:
                nircmd_paths = [
                    'nircmd.exe',
                    os.path.join(os.path.dirname(__file__), 'tools', 'nircmd.exe'),
                    r'C:\Windows\nircmd.exe',
                ]
                for path in nircmd_paths:
                    try:
                        subprocess.run([path, 'monitoroff'], capture_output=True, timeout=5)
                        return "✓ Monitor turned off"
                    except:
                        pass
            except:
                pass

            return "⚠️ Monitor off may require nircmd.exe. Try 'Lock screen' or 'Sleep' instead."

        return "✗ Please specify 'lock', 'sleep', or 'monitor off'"

    except Exception as e:
        return f"✗ Screen control error: {str(e)}"

def control_airplane_mode(action: str) -> str:
    """Turn airplane mode on/off."""
    try:
        action_lower = action.lower().strip()
        should_enable = any(word in action_lower for word in ['on', 'enable', 'turn on'])
        should_disable = any(word in action_lower for word in ['off', 'disable', 'turn off'])

        if not should_enable and not should_disable:
            return "✗ Please specify 'on' or 'off' for airplane mode"

        # Use Settings shortcut first (fastest on Windows 11)
        try:
            subprocess.run(['cmd', '/c', 'start ms-settings:airplanemode'],
                         check=False, timeout=5)
            status = "on" if should_enable else "off"
            return f"⚠️ Opened Airplane Mode settings. Please turn it {status} manually or wait 3 seconds..."
        except:
            pass

        return "⚠️ Airplane mode requires manual control via Settings > Network & Internet > Airplane Mode"

    except Exception as e:
        return f"✗ Airplane mode error: {str(e)}"

def execute_windows_settings_command(task: str) -> str:
    """Execute various Windows settings tasks based on natural language commands."""
    task_lower = task.lower().strip()

    settings_map = {
        'display': 'ms-settings:display',
        'resolution': 'ms-settings:display-advanced',
        'screen': 'ms-settings:display',
        'theme': 'ms-settings:personalization-colors',
        'dark mode': 'ms-settings:personalization-colors',
        'wallpaper': 'ms-settings:personalization-background',
        'sound': 'ms-settings:sound',
        'volume': 'ms-settings:sound',
        'audio': 'ms-settings:sound',
        'speaker': 'ms-settings:sound',
        'date': 'ms-settings:dateandtime',
        'time': 'ms-settings:dateandtime',
        'timezone': 'ms-settings:dateandtime',
        'clock': 'ms-settings:dateandtime',
        'wifi': 'ms-settings:network-wifi',
        'network': 'ms-settings:network-status',
        'internet': 'ms-settings:network-wifi',
        'bluetooth': 'ms-settings:bluetooth',
        'sleep': 'ms-settings:powersleep',
        'power': 'ms-settings:powersleep',
        'battery': 'ms-settings:powersleep',
        'privacy': 'ms-settings:privacy-general',
        'camera': 'ms-settings:privacy-webcam',
        'microphone': 'ms-settings:privacy-microphone',
        'location': 'ms-settings:privacy-location',
        'keyboard': 'ms-settings:keyboard',
        'mouse': 'ms-settings:devices-mouse',
        'touchpad': 'ms-settings:devices-touchpad',
        'about': 'ms-settings:about',
        'storage': 'ms-settings:storagesense',
        'disk': 'ms-settings:storagesense',
        'startup': 'ms-settings:startupapps',
        'update': 'ms-settings:update-security',
        'windows update': 'ms-settings:update-security',
    }

    for keyword, uri in settings_map.items():
        if keyword in task_lower:
            try:
                subprocess.run(['cmd', '/c', f'start {uri}'], check=False, timeout=5)
                return f"✓ Opened Windows {keyword.title()} settings"
            except Exception as e:
                return f"✗ Could not open settings: {str(e)}"

    try:
        subprocess.run(['cmd', '/c', 'start ms-settings:'], check=False, timeout=5)
        return f"✓ Opened Windows Settings. Please look for '{task}' in the settings menu."
    except Exception as e:
        return f"✗ Could not open settings: {str(e)}"

# ==================== MCP TOOLS DEFINITION ====================

TOOLS = [
    {
        "name": "open_website",
        "description": "Open a website in the default browser",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Website URL (e.g., gmail.com, google.com)"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "open_application",
        "description": "Open an application or website by name (e.g., Gmail, Calculator, Chrome, Notepad)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "App name (e.g., 'Gmail', 'Calculator', 'Chrome', 'Notepad')"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "play_youtube",
        "description": "Play a song or video on YouTube",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Song or video name"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_web",
        "description": "Search the web using DuckDuckGo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get current weather",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_news",
        "description": "Get news headlines",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "send_whatsapp",
        "description": "Send WhatsApp message",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contact_name": {"type": "string", "description": "Contact name"},
                "message": {"type": "string", "description": "Message text"}
            },
            "required": ["contact_name", "message"]
        }
    },
    {
        "name": "get_system_info",
        "description": "Get system performance info",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_time",
        "description": "Get current time",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_date",
        "description": "Get today's date",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Person or topic"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "set_brightness",
        "description": "Set screen brightness level (0-100%)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "Brightness level 0-100"}
            },
            "required": ["level"]
        }
    },
    {
        "name": "set_volume",
        "description": "Set system volume level (0-100%)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "Volume level 0-100"}
            },
            "required": ["level"]
        }
    },
    {
        "name": "execute_windows_settings_command",
        "description": "Open Windows Settings for a specific task (display, sound, date, time, network, privacy, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Settings task or feature name"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "control_wifi",
        "description": "Turn Wi-Fi on or off",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action: 'on', 'off', 'enable', 'disable', 'turn on', 'turn off', 'connect', 'disconnect'"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "control_bluetooth",
        "description": "Turn Bluetooth on or off",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action: 'on', 'off', 'enable', 'disable', 'turn on', 'turn off'"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "control_sound",
        "description": "Mute or unmute system sound",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action: 'mute', 'unmute', 'on', 'off'"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "control_screen",
        "description": "Lock screen, sleep mode, or turn off monitor",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action: 'lock', 'sleep', 'monitor off'"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "control_airplane_mode",
        "description": "Turn airplane mode on or off",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action: 'on', 'off', 'enable', 'disable'"}
            },
            "required": ["action"]
        }
    }
]

# ==================== TOOL EXECUTION ====================

async def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool"""
    if name == "open_website":
        return open_website(arguments.get("url", ""))
    elif name == "open_application":
        return open_application(arguments.get("app_name", ""))
    elif name == "play_youtube":
        return play_youtube(arguments.get("query", ""))
    elif name == "search_web":
        return search_web(arguments.get("query", ""))
    elif name == "get_weather":
        return get_weather()
    elif name == "get_news":
        return get_news()
    elif name == "send_whatsapp":
        return send_whatsapp(arguments.get("contact_name", ""), arguments.get("message", ""))
    elif name == "get_system_info":
        return get_system_info()
    elif name == "get_time":
        return get_time()
    elif name == "get_date":
        return get_date()
    elif name == "search_wikipedia":
        return search_wikipedia(arguments.get("query", ""))
    elif name == "set_brightness":
        return set_brightness(int(arguments.get("level", 75)))
    elif name == "set_volume":
        return set_volume(int(arguments.get("level", 50)))
    elif name == "execute_windows_settings_command":
        return execute_windows_settings_command(arguments.get("task", ""))
    elif name == "control_wifi":
        return control_wifi(arguments.get("action", ""))
    elif name == "control_bluetooth":
        return control_bluetooth(arguments.get("action", ""))
    elif name == "control_sound":
        return control_sound(arguments.get("action", ""))
    elif name == "control_screen":
        return control_screen(arguments.get("action", ""))
    elif name == "control_airplane_mode":
        return control_airplane_mode(arguments.get("action", ""))
    else:
        return f"Unknown tool: {name}"

# ==================== MCP SERVER ====================

server = Server("ai-assistant-universal")

@server.list_tools()
async def list_tools():
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[ToolResult]:
    try:
        result = await execute_tool(name, arguments)
        return [ToolResult(type="text", text=result)]
    except Exception as e:
        return [ToolResult(type="text", text=f"Error: {str(e)}", isError=True)]

async def main():
    print("\n" + "="*60)
    print("AI Assistant - Universal MCP Server (FREE & LOCAL)")
    print("="*60)
    print(f"Backend: {LLM_BACKEND.upper()}")
    print(f"Model: {LLM_MODEL}")
    print(f"URL: {LLM_BASE_URL}")
    print("\nTools Available:")
    for tool in TOOLS:
        print(f"  • {tool['name']}")
    print("\n" + "="*60)
    async with server:
        await server.start()

if __name__ == "__main__":
    asyncio.run(main())
