print("[STARTUP] Python started", flush=True)
from flask import Flask, render_template, request, jsonify
print("[STARTUP] Flask imported", flush=True)
from langchain_ollama import ChatOllama
import datetime
import wikipedia
import psutil
from bs4 import BeautifulSoup
import requests
import json
import os
import pywhatkit
import uuid
import webbrowser
import subprocess
import shutil
import re
import threading
import signal
from typing import Optional, List

print("[STARTUP] All imports complete", flush=True)
app = Flask(__name__)
print("[STARTUP] Flask app created", flush=True)
CONTACTS_FILE = "contacts.json"

# ==================== LLM INITIALIZATION ====================

print("[STARTUP] Starting LLM initialization...", flush=True)

_ollama_llm = None
_claude_llm = None

def _init_llms():
    global _ollama_llm, _claude_llm
    print("[STARTUP] Initializing LLMs...", flush=True)
    try:
        print("[STARTUP] Connecting to Ollama...", flush=True)
        _ollama_llm = ChatOllama(model="llama3.2", base_url="http://localhost:11434", timeout=30)
        print("[INFO] ChatOllama initialized successfully", flush=True)
    except Exception as e:
        print(f"[WARNING] Ollama not available: {e}", flush=True)
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if api_key:
            print("[STARTUP] Initializing Claude...", flush=True)
            from langchain_anthropic import ChatAnthropic
            _claude_llm = ChatAnthropic(model="claude-haiku-4-5-20251001", api_key=api_key, timeout=30)
            print("[INFO] Claude API fallback initialized", flush=True)
        else:
            print("[INFO] ANTHROPIC_API_KEY not set. Claude fallback disabled.", flush=True)
    except Exception as e:
        print(f"[INFO] Claude API not available: {e}", flush=True)

print("[STARTUP] Calling _init_llms()...", flush=True)
_init_llms()
print("[STARTUP] _init_llms() complete", flush=True)

def get_active_llm():
    return _ollama_llm or _claude_llm

# ==================== TOOL DEFINITIONS ====================

def fetch_website_info(url: str) -> str:
    """Fetch and extract information from a website using BeautifulSoup."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title = soup.title.string if soup.title else "No title found"

        # Extract main headings
        headings = []
        for h in soup.find_all(['h1', 'h2', 'h3'])[:3]:
            text = h.get_text(strip=True)
            if text and len(text) > 5:
                headings.append(text)

        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all('p')[:3]:
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                paragraphs.append(text)

        # Extract meta description
        meta_description = ""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            meta_description = meta.get('content', '')

        # Compile information
        info = f"🌐 Website: {title}\n"
        if meta_description:
            info += f"Description: {meta_description}\n"
        if headings:
            info += "\nMain sections:\n" + "\n".join([f"  • {h}" for h in headings])
        if paragraphs:
            info += "\n\nContent summary:\n" + "\n".join([f"  {p[:100]}..." if len(p) > 100 else f"  {p}" for p in paragraphs])

        return info

    except Exception as e:
        return f"✗ Could not fetch website info: {str(e)}"

def open_website(url: str, get_info: bool = True) -> str:
    """Open a website in the default browser and optionally fetch its information."""
    try:
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        # Try to open in browser
        try:
            webbrowser.open(url, new=2)
        except:
            pass

        # Fetch and display website information
        if get_info:
            info = fetch_website_info(url)
            return f"✓ Opened {url}\n\n{info}"
        else:
            return f"✓ Opened {url} in your browser"
    except Exception as e:
        return f"✗ Could not open website: {str(e)}"

def open_application(app_name: str) -> str:
    """Open an application on the system. Comprehensively searches for Windows apps, web services, and installed programs."""
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
            'stack overflow': 'https://stackoverflow.com',
            'wikipedia': 'https://wikipedia.org',
            # System apps with icons/protocols
            'settings': 'ms-settings:',
            'whatsapp': 'whatsapp:',
            'telegram': 'https://telegram.org',
            # Common executables
            'calculator': 'calc.exe',
            'calc': 'calc.exe',
            'notepad': 'notepad.exe',
            'paint': 'mspaint.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'access': 'msaccess.exe',
            'outlook': 'outlook.exe',
            'onenote': 'onenote.exe',
            'teams': 'teams.exe',
            # Browsers and tools
            'chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'explorer': 'explorer.exe',
            'file explorer': 'explorer.exe',
            'control panel': 'control.exe',
            'task manager': 'taskmgr.exe',
            'terminal': 'cmd.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'vs code': 'code',
            'vscode': 'code',
            'visual studio code': 'code',
            'sublime': 'subl',
            'vlc': 'vlc',
            'photoshop': 'photoshop.exe',
            '7zip': '7z',
            'winrar': 'winrar.exe',
        }

        app_lower = app_name.lower().strip()

        # Check if it's a web service
        if app_lower in app_map and app_map[app_lower].startswith('https://'):
            return open_website(app_map[app_lower], get_info=False)

        # Get target from map or use app_name directly
        target = app_map.get(app_lower, app_name)

        # Handle protocol handlers (ms-settings:, whatsapp:, etc.)
        if target.endswith(':'):
            try:
                subprocess.Popen(f'explorer "{target}"')
                return f"✓ Opened {app_name}"
            except:
                try:
                    subprocess.run(['cmd', '/c', f'start {target}'], check=False, timeout=5)
                    return f"✓ Opened {app_name}"
                except:
                    pass

        # Method 1: Try direct execution
        try:
            subprocess.Popen(target, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"✓ Opened {app_name}"
        except:
            pass

        # Method 2: Try with 'where' command to find in PATH
        try:
            result = subprocess.run(['where', target], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                app_path = result.stdout.strip().split('\n')[0]
                subprocess.Popen(app_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"✓ Opened {app_name}"
        except:
            pass

        # Method 3: Search in common installation directories
        common_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expanduser("~\\AppData\\Local\\Programs"),
            r"C:\Users",
        ]

        for base_path in common_paths:
            try:
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.lower().startswith(target.lower().split()[0]) and file.lower().endswith(('.exe', '.lnk')):
                            full_path = os.path.join(root, file)
                            subprocess.Popen(full_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            return f"✓ Opened {app_name}"
            except:
                continue

        # Method 4: Use PowerShell Get-Command to find executables
        try:
            ps_cmd = f"Get-Command {target} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source"
            result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_cmd],
                                  capture_output=True, text=True, timeout=10)
            if result.stdout.strip():
                app_path = result.stdout.strip()
                subprocess.Popen(app_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"✓ Opened {app_name}"
        except:
            pass

        return f"✗ Could not open '{app_name}': Application not found on this system. Try installing the application or check the spelling."
    except Exception as e:
        return f"✗ Error opening application: {str(e)}"

def create_folder(path: str = None, folder_name: str = None) -> str:
    """Create a new folder. Use this when user wants to make a folder."""
    try:
        # Use provided path or default to Desktop
        if not path:
            path = os.path.join(os.path.expanduser("~"), "Desktop")

        # If no name provided, generate one
        if not folder_name:
            from datetime import datetime
            folder_name = f"Folder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        folder_path = os.path.join(path, folder_name)
        if os.path.exists(folder_path):
            return f"⚠️ Folder '{folder_name}' already exists at {folder_path}"
        os.makedirs(folder_path, exist_ok=True)

        # Open the folder in Windows Explorer
        try:
            import subprocess
            subprocess.Popen(f'explorer "{folder_path}"')
        except:
            pass

        return f"✓ Folder '{folder_name}' created at {folder_path} and opened"
    except Exception as e:
        return f"✗ Could not create folder: {str(e)}"

def delete_file(file_path: str) -> str:
    """Delete a file from the system. Use this when user wants to delete a file."""
    try:
        if not os.path.exists(file_path):
            return f"✗ File not found: {file_path}"
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
            return f"✓ Folder and its contents deleted: {file_path}"
        else:
            os.remove(file_path)
            return f"✓ File deleted: {file_path}"
    except Exception as e:
        return f"✗ Could not delete file: {str(e)}"

def list_files(directory_path: str) -> str:
    """List all files and folders in a directory. Use this when user wants to see what's in a folder."""
    try:
        if not os.path.exists(directory_path):
            return f"✗ Directory not found: {directory_path}"

        items = os.listdir(directory_path)
        if not items:
            return f"📁 Directory is empty: {directory_path}"

        files = []
        folders = []
        for item in items:
            full_path = os.path.join(directory_path, item)
            if os.path.isdir(full_path):
                folders.append(f"  📁 {item}/")
            else:
                files.append(f"  📄 {item}")

        result = f"📂 Contents of {directory_path}:\n"
        if folders:
            result += "Folders:\n" + "\n".join(folders) + "\n"
        if files:
            result += "Files:\n" + "\n".join(files)
        return result
    except Exception as e:
        return f"✗ Could not list files: {str(e)}"

def read_file(file_path: str) -> str:
    """Read and display the contents of a file. Use this when user wants to read a file."""
    try:
        if not os.path.exists(file_path):
            return f"✗ File not found: {file_path}"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if len(content) > 2000:
            content = content[:2000] + "\n... (file truncated for display)"

        return f"📄 Contents of {file_path}:\n\n{content}"
    except Exception as e:
        return f"✗ Could not read file: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Creates the file if it doesn't exist. Use this when user wants to write/save to a file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✓ File written successfully: {file_path}"
    except Exception as e:
        return f"✗ Could not write file: {str(e)}"

def rename_file(old_path: str, new_path: str) -> str:
    """Rename or move a file to a new path. Use this when user wants to rename a file."""
    try:
        if not os.path.exists(old_path):
            return f"✗ File not found: {old_path}"

        if os.path.exists(new_path):
            return f"⚠️ Destination already exists: {new_path}"

        os.rename(old_path, new_path)
        return f"✓ File renamed/moved from {old_path} to {new_path}"
    except Exception as e:
        return f"✗ Could not rename file: {str(e)}"

def move_file(source_path: str, destination_path: str) -> str:
    """Move a file or folder to a new location. Use this when user wants to move files."""
    try:
        if not os.path.exists(source_path):
            return f"✗ Source not found: {source_path}"

        shutil.move(source_path, destination_path)
        return f"✓ Moved from {source_path} to {destination_path}"
    except Exception as e:
        return f"✗ Could not move file: {str(e)}"

def set_brightness(level) -> str:
    """Set screen brightness level (0-100). Use this when user wants to change brightness."""
    try:
        # Convert to int if needed
        if isinstance(level, str):
            level = int(''.join(filter(str.isdigit, level)))
        level = max(0, min(100, int(level)))

        # Method 1: Try WMI (works on some systems)
        try:
            ps_script = f"""
            $wmi = Get-WmiObject -Namespace "root\\WMI" -Class WmiMonitorBrightness -ErrorAction SilentlyContinue
            if ($wmi) {{
                $wmi.WmiSetBrightness(1, {level})
                Start-Sleep -Milliseconds 300
                Write-Output "SUCCESS"
            }} else {{
                Write-Output "NO_WMI"
            }}
            """
            result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_script],
                                  capture_output=True, text=True, timeout=10)
            if "SUCCESS" in result.stdout:
                return f"✓ Brightness set to {level}%"
        except:
            pass

        # Method 2: Try Windows Settings (alternative)
        try:
            ps_script = f"""
            try {{
                $monitor = Get-WmiObject -Namespace root\\WMI -Class WmiMonitorBrightness
                if ($monitor) {{
                    $monitor.WmiSetBrightness(0, {level})
                    Write-Output "SUCCESS"
                }}
            }} catch {{
                Write-Output "FAILED"
            }}
            """
            result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_script],
                                  capture_output=True, text=True, timeout=10)
            if "SUCCESS" in result.stdout:
                return f"✓ Brightness set to {level}%"
        except:
            pass

        # Method 3: Use nircmd if available
        try:
            nircmd_path = os.path.join(os.path.dirname(__file__), 'tools', 'nircmd.exe')
            if os.path.exists(nircmd_path):
                result = subprocess.run([nircmd_path, 'setbrightness', str(level)],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return f"✓ Brightness set to {level}%"
        except:
            pass

        return f"⚠️ Brightness control may not be available on this system. Your monitor might need manual brightness adjustment or this system doesn't support programmatic brightness control."

    except Exception as e:
        return f"✗ Error setting brightness: {str(e)}"

def set_volume(level) -> str:
    """Set system volume level (0-100). Use this when user wants to change volume."""
    try:
        # Convert to int if needed
        if isinstance(level, str):
            level = int(''.join(filter(str.isdigit, level)))
        level = max(0, min(100, int(level)))

        # Method 1: Try using nircmd if available (with full path)
        try:
            nircmd_path = os.path.join(os.path.dirname(__file__), 'tools', 'nircmd.exe')
            if os.path.exists(nircmd_path):
                result = subprocess.run([nircmd_path, 'setsysvolume', str(int(level * 655))],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return f"[SUCCESS] Volume set to {level}%"
        except:
            pass

        # Method 2: Try COM object approach
        ps_script = f"""
        [void][Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
        $wshShell = New-Object -ComObject WScript.Shell
        try {{
            $AudioDevice = New-Object -ComObject AudioDeviceLib.AudioMmDeviceEnumerator
            $device = $AudioDevice.GetDefaultAudioEndpoint(0, 1)
            if ($device) {{
                $device.AudioEndpointVolume.MasterVolumeLevelScalar = {level / 100.0}
                Start-Sleep -Milliseconds 300
                Write-Output "SUCCESS"
            }}
        }} catch {{
            Write-Output "FAILED"
        }}
        """

        result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_script],
                              capture_output=True, text=True, timeout=5)

        if "SUCCESS" in result.stdout:
            return f"[SUCCESS] Volume set to {level}%"

        return f"⚠️ Volume control not available. Try adjusting volume using Sound Settings or keyboard volume buttons."

    except Exception as e:
        return f"✗ Could not set volume: {str(e)}"

def control_wifi(action: str) -> str:
    """Turn Wi-Fi on or off. Requires admin privileges. Use this when user wants to enable/disable Wi-Fi."""
    try:
        action_lower = action.lower()
        should_enable = any(word in action_lower for word in ['on', 'enable', 'turn on'])

        # Get current Wi-Fi adapter names first
        try:
            result = subprocess.run(['powershell', '-Command', 'Get-NetAdapter | Where-Object {$_.Name -like "*Wi-Fi*" -or $_.Name -like "*Wireless*"} | Select-Object -ExpandProperty Name'],
                                  capture_output=True, text=True, timeout=5)
            adapter_names = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
        except:
            adapter_names = ['Wi-Fi']

        if not adapter_names:
            return "✗ No wireless adapter found on this system"

        for adapter_name in adapter_names:
            try:
                ps_cmd = f'Enable-NetAdapter -Name "{adapter_name}" -Confirm:$false' if should_enable else f'Disable-NetAdapter -Name "{adapter_name}" -Confirm:$false'
                result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, timeout=10)

                # Verify the state actually changed
                import time
                time.sleep(1)
                verify_cmd = f'(Get-NetAdapter -Name "{adapter_name}").Status'
                verify = subprocess.run(['powershell', '-Command', verify_cmd], capture_output=True, text=True, timeout=5)
                current_state = verify.stdout.strip().lower()

                expected_state = "up" if should_enable else "disabled"
                if expected_state in current_state or (should_enable and current_state == "up"):
                    status = "on" if should_enable else "off"
                    return f"✓ Wi-Fi turned {status}"
                elif not should_enable and "disabled" in current_state:
                    return "✓ Wi-Fi turned off"
            except:
                continue

        return "⚠️ Wi-Fi control needs admin privileges. Run Flask with administrator rights."
    except Exception as e:
        return f"✗ Wi-Fi error: {str(e)}"

def control_bluetooth(action: str) -> str:
    """Turn Bluetooth on or off. Requires admin privileges. Use this when user wants to enable/disable Bluetooth."""
    try:
        action_lower = action.lower()
        should_enable = any(word in action_lower for word in ['on', 'enable', 'turn on'])

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

        return "⚠️ Bluetooth control needs admin privileges. Run Flask with administrator rights."
    except Exception as e:
        return f"✗ Bluetooth error: {str(e)}"

def get_system_info() -> str:
    """Get current system information like CPU, RAM, and disk usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        info = f"""
📊 System Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️  CPU Usage: {cpu_percent}%
💾 RAM: {memory.used:.1f}GB / {memory.total:.1f}GB ({memory.percent}%)
💿 Disk: {disk.used:.1f}GB / {disk.total:.1f}GB ({disk.percent}%)
"""
        return info.strip()
    except Exception as e:
        return f"✗ Could not get system info: {str(e)}"

def get_time() -> str:
    """Get the current time."""
    return f"🕐 Current time: {datetime.datetime.now().strftime('%I:%M %p')}"

def get_date() -> str:
    """Get the current date."""
    return f"📅 Current date: {datetime.datetime.now().strftime('%A, %B %d, %Y')}"

def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information about a topic. Use this when user asks about a person or topic."""
    try:
        result = wikipedia.summary(query, sentences=3)
        return f"📖 Wikipedia result for '{query}':\n\n{result}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"⚠️ Ambiguous query. Did you mean one of these?\n" + "\n".join(e.options[:5])
    except wikipedia.exceptions.PageError:
        return f"✗ No Wikipedia page found for '{query}'"
    except Exception as e:
        return f"✗ Could not search Wikipedia: {str(e)}"

def search_web(query: str) -> str:
    """Search the web for information and return results with links."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = f"https://duckduckgo.com/search?q={query}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        results = []

        # Try multiple selectors for robustness
        for result in soup.find_all('a', class_='result__a')[:5]:
            title = result.get_text(strip=True)
            link = result.get('href')
            if title and link and len(title) > 5:
                results.append(f"• {title}\n  {link}")

        if len(results) < 3:
            # Fallback: try alternative selectors
            for link in soup.find_all('a', limit=10):
                href = link.get('href')
                text = link.get_text(strip=True)
                if href and text and len(text) > 10 and ('http' in href or 'duckduckgo' not in href):
                    if len(results) < 5:
                        results.append(f"• {text}\n  {href}")

        if results:
            return f"🔍 Search results for '{query}':\n\n" + "\n".join(results[:5])
        else:
            return f"⚠️ No results found for '{query}'"
    except Exception as e:
        return f"✗ Could not search web: {str(e)}"

def scrape_website_content(url: str, query: str = None) -> str:
    """Scrape and extract specific information from a website based on query."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unwanted elements
        for script in soup(["script", "style", "meta", "noscript"]):
            script.decompose()

        # Extract all text
        text = soup.get_text()

        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        # Limit text length
        if len(text) > 5000:
            text = text[:5000] + "..."

        # Extract title
        title = soup.title.string if soup.title else url

        result = f"📄 Website: {title}\n\n"
        result += f"Content from {url}:\n"
        result += text

        return result

    except Exception as e:
        return f"✗ Could not scrape website: {str(e)}"

def play_youtube(query: str) -> str:
    """Search and play a video on YouTube. Use this when user wants to play music or video."""
    try:
        pywhatkit.playonyt(query)
        return f"▶️ Playing '{query}' on YouTube"
    except Exception as e:
        return f"✗ Could not play on YouTube: {str(e)}"

def send_whatsapp(contact_name: str, message: str) -> str:
    """Send a WhatsApp message to a contact. Use this when user wants to send WhatsApp message."""
    try:
        pywhatkit.sendwhatmsg_instantly(contact_name, message)
        return f"✓ WhatsApp message sent to {contact_name}: {message}"
    except Exception as e:
        return f"✗ Could not send WhatsApp message: {str(e)}"

def change_wallpaper(image_path: str = None) -> str:
    """Change the Windows desktop wallpaper."""
    try:
        # If no image path provided, use a default or system image
        if not image_path:
            # Try to use a default Windows wallpaper
            import ctypes
            # Use a built-in Windows image
            default_wallpaper = r"C:\Windows\web\wallpaper\Windows\img0.jpg"
            if os.path.exists(default_wallpaper):
                image_path = default_wallpaper
            else:
                return "⚠️ No image path provided. Please specify an image file path."

        # Set the wallpaper using ctypes (Windows API)
        if os.path.exists(image_path):
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)
            return f"✓ Wallpaper changed to: {image_path}"
        else:
            return f"✗ Image not found: {image_path}"
    except Exception as e:
        return f"✗ Could not change wallpaper: {str(e)}"

def check_windows_updates() -> str:
    """Check for pending Windows updates on the system. Use this when user asks about Windows updates."""
    try:
        ps_script = """
        $session = New-Object -ComObject Microsoft.Update.Session
        $searcher = $session.CreateUpdateSearcher()
        $result = $searcher.Search("IsInstalled=0 and Type='Software'")
        $count = $result.Updates.Count
        if ($count -eq 0) {
            Write-Output "No pending updates"
        } else {
            Write-Output "$count updates available:"
            foreach ($update in $result.Updates) {
                Write-Output "  - $($update.Title)"
            }
        }
        """
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return f"Windows Update Check:\n{result.stdout.strip()}"
        return "Could not check for updates. Try running as Administrator."
    except Exception as e:
        return f"Error checking updates: {str(e)}"

def get_weather() -> str:
    """Get current weather information. Use this when user asks about weather."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://wttr.in/?format=j1', headers=headers, timeout=10)
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        condition = current['weatherDesc'][0]['value']
        return f"Current weather: {condition} with temperature {temp}°C"
    except Exception as e:
        return f"Could not fetch weather: {str(e)}"

def get_news() -> str:
    """Get latest news headlines from multiple sources using web scraping."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        headlines = []

        # Try BBC News
        try:
            response = requests.get('https://www.bbc.com/news', headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # BBC News uses h2, h3 tags for headlines
            for tag in soup.find_all(['h2', 'h3'])[:5]:
                text = tag.get_text(strip=True)
                if text and len(text) > 10 and len(text) < 200:
                    headlines.append(text)
        except:
            pass

        # Try Reuters
        if len(headlines) < 3:
            try:
                response = requests.get('https://www.reuters.com', headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                for heading in soup.find_all('h3', limit=5):
                    text = heading.get_text(strip=True)
                    if text and len(text) > 10 and len(text) < 200:
                        headlines.append(text)
            except:
                pass

        # Try DuckDuckGo news
        if len(headlines) < 3:
            try:
                response = requests.get('https://news.duckduckgo.com', headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                for link in soup.find_all('a', class_='result__a', limit=5):
                    text = link.get_text(strip=True)
                    if text and len(text) > 10:
                        headlines.append(text)
            except:
                pass

        # Remove duplicates while preserving order
        seen = set()
        unique_headlines = []
        for h in headlines:
            if h not in seen and len(h) > 10:
                seen.add(h)
                unique_headlines.append(h)

        if unique_headlines:
            return "📰 Latest news headlines:\n" + "\n".join([f"  • {h}" for h in unique_headlines[:5]])
        else:
            return "⚠️ Could not fetch latest news from available sources. Please try again later."
    except Exception as e:
        return f"✗ Could not fetch news: {str(e)}"

# ==================== TOOL SETS FOR 4 AGENTS ====================


# Tool definitions not needed - using simple if/elif routing in /api/ask endpoint
print("[STARTUP] Tools initialized - 2am version")

print("[STARTUP] APP READY TO RECEIVE REQUESTS", flush=True)

# ==================== SESSION MANAGEMENT ====================

# Session-based conversation history
sessions = {}

def get_or_create_session(session_id):
    """Get or create a conversation session."""
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "pending_approval": None,
            "last_command": None
        }
    return sessions[session_id]

# ==================== ROUTES ====================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    """Main API endpoint - simple if/elif keyword routing (2 am version)."""
    try:
        data = request.json
        command = data.get('command', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))

        if not command:
            return jsonify({'response': 'Please say something.', 'session_id': session_id}), 200

        session = get_or_create_session(session_id)
        session['messages'].append({"role": "user", "content": command})

        # Simple if/elif keyword routing (2 am version)
        cmd_lower = command.lower()
        response_text = ""

        if any(w in cmd_lower for w in ['time', 'hour', 'minute', 'what time']):
            response_text = get_time()
        elif any(w in cmd_lower for w in ['date', 'day', 'what date']):
            response_text = get_date()
        elif any(w in cmd_lower for w in ['weather', 'temperature', 'climate', 'rain', 'cold', 'hot']):
            response_text = get_weather()
        elif any(w in cmd_lower for w in ['news', 'headline', 'current event']):
            response_text = get_news()
        elif any(w in cmd_lower for w in ['system info', 'cpu', 'ram', 'memory', 'disk']):
            response_text = get_system_info()
        elif any(w in cmd_lower for w in ['wifi', 'wi-fi']):
            if any(w in cmd_lower for w in ['on', 'enable', 'turn on']):
                response_text = control_wifi('turn on')
            elif any(w in cmd_lower for w in ['off', 'disable', 'turn off']):
                response_text = control_wifi('turn off')
            else:
                response_text = control_wifi('toggle')
        elif any(w in cmd_lower for w in ['bluetooth']):
            if any(w in cmd_lower for w in ['on', 'enable', 'turn on']):
                response_text = control_bluetooth('turn on')
            elif any(w in cmd_lower for w in ['off', 'disable', 'turn off']):
                response_text = control_bluetooth('turn off')
            else:
                response_text = control_bluetooth('toggle')
        elif any(w in cmd_lower for w in ['volume']):
            try:
                import re
                numbers = re.findall(r'\d+', command)
                level = int(numbers[0]) if numbers else 50
                response_text = set_volume(str(level))
            except:
                response_text = "Please specify a volume level (0-100)"
        elif any(w in cmd_lower for w in ['brightness']):
            try:
                import re
                numbers = re.findall(r'\d+', command)
                level = int(numbers[0]) if numbers else 50
                response_text = set_brightness(str(level))
            except:
                response_text = "Please specify a brightness level (0-100)"
        elif any(w in cmd_lower for w in ['wallpaper', 'background']):
            response_text = change_wallpaper()
        elif any(w in cmd_lower for w in ['play ', 'youtube', 'music', 'song']):
            query = command.replace('play', '').replace('youtube', '').strip()
            response_text = play_youtube(query if query else 'music')
        elif any(w in cmd_lower for w in ['create folder', 'make folder', 'new folder']):
            folder_name = command.replace('create folder', '').replace('make folder', '').replace('new folder', '').strip()
            response_text = create_folder(str(os.path.expanduser("~/Desktop")), folder_name if folder_name else 'NewFolder')
        elif any(w in cmd_lower for w in ['delete file', 'delete folder', 'remove file']):
            file_name = command.replace('delete file', '').replace('delete folder', '').replace('remove file', '').strip()
            response_text = delete_file(file_name) if file_name else "Please specify a file to delete"
        elif any(w in cmd_lower for w in ['list files', 'show files', 'what files']):
            path = str(os.path.expanduser("~/Desktop"))
            response_text = list_files(path)
        elif any(w in cmd_lower for w in ['read file']):
            file_name = command.replace('read file', '').strip()
            response_text = read_file(file_name) if file_name else "Please specify a file to read"
        elif any(w in cmd_lower for w in ['write file', 'save file']):
            response_text = "Please provide file path and content"
        elif any(w in cmd_lower for w in ['open app', 'launch']):
            app_name = command.replace('open app', '').replace('launch', '').strip()
            response_text = open_application(app_name) if app_name else "Please specify an app"
        elif any(w in cmd_lower for w in ['open website', 'go to']):
            url = command.replace('open website', '').replace('go to', '').strip()
            response_text = open_website(url) if url else "Please specify a website"
        elif any(w in cmd_lower for w in ['wikipedia', 'who is', 'what is']):
            query = command.replace('wikipedia', '').replace('who is', '').replace('what is', '').strip()
            response_text = search_wikipedia(query) if query else "Please specify who or what to search for"
        elif any(w in cmd_lower for w in ['search', 'find']):
            query = command.replace('search', '').replace('find', '').strip()
            response_text = search_web(query) if query else "Please specify what to search for"
        elif any(w in cmd_lower for w in ['update', 'windows update']):
            response_text = check_windows_updates()
        elif any(w in cmd_lower for w in ['whatsapp', 'send message']):
            response_text = "Please specify contact and message"
        else:
            response_text = f"Command '{command}' not recognized. Try asking about time, weather, news, or system info."

        session['messages'].append({"role": "assistant", "content": response_text})
        response = jsonify({'response': response_text, 'session_id': session_id})
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        return jsonify({'response': f"Error: {error_msg}", 'session_id': session_id}), 500


@app.route('/api/system', methods=['GET'])
def system_info():
    """Get system information."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
                if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                    processes.append(pinfo)
            except:
                pass

        processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]

        return jsonify({
            "cpu": {"percent": cpu_percent},
            "memory": {"used": round(memory.used / (1024**3), 2), "total": round(memory.total / (1024**3), 2), "percent": memory.percent},
            "disk": {"used": round(disk.used / (1024**3), 2), "total": round(disk.total / (1024**3), 2), "percent": disk.percent},
            "processes": processes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contacts', methods=['GET', 'POST'])
def contacts():
    """Manage contacts."""
    try:
        if request.method == 'GET':
            if os.path.exists(CONTACTS_FILE):
                with open(CONTACTS_FILE, 'r') as f:
                    return jsonify(json.load(f))
            return jsonify([])

        elif request.method == 'POST':
            data = request.json
            contacts_list = []
            if os.path.exists(CONTACTS_FILE):
                with open(CONTACTS_FILE, 'r') as f:
                    contacts_list = json.load(f)

            contacts_list.append(data)
            with open(CONTACTS_FILE, 'w') as f:
                json.dump(contacts_list, f, indent=2)

            return jsonify({"message": "Contact added", "contact": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("[INFO] AI Virtual Assistant - Starting Flask Server", flush=True)
    print("[INFO] Ollama Model: llama3.2", flush=True)
    print("[INFO] Port: 8000", flush=True)
    print("[INFO] Access at: http://localhost:8000 or http://127.0.0.1:8000", flush=True)
    print("[INFO] Starting Flask web server...", flush=True)
    app.run(debug=False, host='0.0.0.0', port=8000, use_reloader=False, threaded=True)
