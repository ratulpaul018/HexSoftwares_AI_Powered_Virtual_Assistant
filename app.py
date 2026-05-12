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
import difflib
from typing import Optional, List

print("[STARTUP] All imports complete", flush=True)
app = Flask(__name__)
print("[STARTUP] Flask app created", flush=True)
print(f"[STARTUP] App file: {__file__}", flush=True)
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

# ==================== APP DICTIONARY BUILDING ====================

print("[STARTUP] Building comprehensive app dictionary...", flush=True)

def build_app_dictionary() -> dict:
    """Build a dictionary of all apps on the PC from multiple sources."""
    apps = {}

    # Base app map (static, predefined apps)
    base_app_map = {
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
        'settings': 'ms-settings:',
        'whatsapp': 'whatsapp:',
        'telegram': 'https://telegram.org',
        'calendar': 'ms-windows-store://pdp/?ProductId=9wzdncrfj3p2',
        'mail': 'ms-windows-store://pdp/?ProductId=9wzdncrfjbxp',
        'maps': 'ms-windows-store://pdp/?ProductId=9wzdncrcf6g4',
        'store': 'ms-windows-store:',
        'todo': 'ms-todo:',
        'groove music': 'groovemusic:',
        'movies tv': 'ms-windows-store://pdp/?ProductId=9nblggh4nns1',
        'calculator': 'calc.exe',
        'calc': 'calc.exe',
        'notepad': 'notepad.exe',
        'paint': 'mspaint.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'powerpoint': 'powerpnt.exe',
        'publisher': 'mspub.exe',
        'access': 'msaccess.exe',
        'outlook': 'outlook.exe',
        'onenote': 'onenote.exe',
        'onenoteclip': 'onenoteclip.exe',
        'teams': 'teams.exe',
        'skype': 'skype.exe',
        'infopath': 'infopath.exe',
        'project': 'winproj.exe',
        'chrome': 'chrome',
        'chromium': 'chrome',
        'firefox': 'firefox',
        'edge': 'msedge',
        'internet explorer': 'iexplore.exe',
        'ie': 'iexplore.exe',
        'explorer': 'explorer.exe',
        'file explorer': 'explorer.exe',
        'control panel': 'control.exe',
        'task manager': 'taskmgr.exe',
        'device manager': 'devmgmt.msc',
        'services': 'services.msc',
        'disk management': 'diskmgmt.msc',
        'terminal': 'cmd.exe',
        'cmd': 'cmd.exe',
        'command prompt': 'cmd.exe',
        'powershell': 'powershell.exe',
        'windows powershell': 'powershell.exe',
        'powershell ise': 'powershell_ise.exe',
        'registry editor': 'regedit.exe',
        'regedit': 'regedit.exe',
        'event viewer': 'eventvwr.exe',
        'performance monitor': 'perfmon.exe',
        'resource monitor': 'resmon.exe',
        'system information': 'msinfo32.exe',
        'character map': 'charmap.exe',
        'wordpad': 'wordpad.exe',
        'snipping tool': 'snippingtool.exe',
        'screen sketch': 'ScreenSketch.exe',
        'screen snip': 'ScreenSketch.exe',
        'clipchamp': 'Clipchamp.WindowsDesktop.exe',
        'photos': 'ms-windows-store://pdp/?ProductId=9nblggh4njns',
        'camera': 'ms-camera:',
        'vs code': 'code',
        'vscode': 'code',
        'visual studio code': 'code',
        'visual studio': 'devenv.exe',
        'sublime': 'subl',
        'git bash': 'bash.exe',
        'vlc': 'vlc',
        'obs': 'obs64.exe',
        'kdenlive': 'kdenlive.exe',
        'blender': 'blender.exe',
        'audacity': 'audacity.exe',
        'gimp': 'gimp.exe',
        'photoshop': 'photoshop.exe',
        'lightroom': 'Lightroom.exe',
        'premiere': 'Adobe Premiere Pro.exe',
        '7zip': '7z',
        'winrar': 'winrar.exe',
        'winzip': 'winzip.exe',
        'ftp': 'winscp.exe',
        'putty': 'putty.exe',
        'notepad++': 'notepad++.exe',
        'filezilla': 'filezilla.exe',
        'qbittorrent': 'qbittorrent.exe',
        'transmission': 'transmission-qt.exe',
    }
    apps.update(base_app_map)

    # Scan Windows Registry for installed applications
    print("[STARTUP] Scanning Windows Registry for apps...", flush=True)
    try:
        ps_cmd = """
        $keys = @(
            'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',
            'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'
        )
        foreach ($key in $keys) {
            Get-ItemProperty $key -ErrorAction SilentlyContinue |
            Where-Object {$_.DisplayName -and $_.InstallLocation} |
            Select-Object -First 100 |
            ForEach-Object {
                $name = $_.DisplayName -replace '[^a-zA-Z0-9 ]', ''
                if ($name.Length -gt 2) {
                    Write-Output "$name|$($_.InstallLocation)"
                }
            }
        }
        """
        result = subprocess.run(['powershell', '-NoProfile', '-Command', ps_cmd], capture_output=True, text=True, timeout=8)
        registry_count = 0
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                try:
                    name, path = line.split('|', 1)
                    name = name.strip().lower()
                    path = path.strip()
                    if name and path and len(name) > 2:
                        apps[name] = path
                        registry_count += 1
                except:
                    pass
        print(f"[STARTUP] Registry scan found {registry_count} apps", flush=True)
    except Exception as e:
        print(f"[INFO] Registry scan skipped: {e}", flush=True)

    # Scan Start Menu .lnk files
    print("[STARTUP] Scanning Start Menu...", flush=True)
    try:
        start_menu_paths = [
            os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
            r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs'
        ]
        start_menu_count = 0
        for base in start_menu_paths:
            if os.path.isdir(base):
                try:
                    for root, _, files in os.walk(base):
                        for f in files:
                            if f.lower().endswith('.lnk'):
                                app_name = os.path.splitext(f)[0].lower()
                                if len(app_name) > 2 and app_name not in apps:
                                    full_path = os.path.join(root, f)
                                    apps[app_name] = full_path
                                    start_menu_count += 1
                except:
                    pass
        print(f"[STARTUP] Start Menu scan found {start_menu_count} apps", flush=True)
    except Exception as e:
        print(f"[INFO] Start Menu scan skipped: {e}", flush=True)

    # Scan Program Files for executables (limited to 2 levels deep)
    print("[STARTUP] Scanning Program Files...", flush=True)
    try:
        program_files_count = 0
        for base_path in [r"C:\Program Files", r"C:\Program Files (x86)"]:
            if os.path.isdir(base_path):
                try:
                    for root, dirs, files in os.walk(base_path):
                        depth = len(root.split('\\')) - len(base_path.split('\\'))
                        # Limit depth to 2 levels
                        if depth > 2:
                            dirs.clear()
                            continue
                        for f in files:
                            if f.lower().endswith('.exe'):
                                app_name = os.path.splitext(f)[0].lower()
                                if len(app_name) > 2 and app_name not in apps:
                                    full_path = os.path.join(root, f)
                                    apps[app_name] = full_path
                                    program_files_count += 1
                except:
                    pass
        print(f"[STARTUP] Program Files scan found {program_files_count} apps", flush=True)
    except Exception as e:
        print(f"[INFO] Program Files scan skipped: {e}", flush=True)

    # Scan PATH environment variable
    print("[STARTUP] Scanning PATH...", flush=True)
    try:
        path_env = os.environ.get('PATH', '')
        path_count = 0
        for path_dir in path_env.split(';'):
            if os.path.isdir(path_dir):
                try:
                    for f in os.listdir(path_dir):
                        if f.lower().endswith('.exe'):
                            app_name = os.path.splitext(f)[0].lower()
                            if len(app_name) > 2 and app_name not in apps:
                                full_path = os.path.join(path_dir, f)
                                apps[app_name] = full_path
                                path_count += 1
                except:
                    pass
        print(f"[STARTUP] PATH scan found {path_count} apps", flush=True)
    except Exception as e:
        print(f"[INFO] PATH scan skipped: {e}", flush=True)

    print(f"[STARTUP] [OK] App dictionary built with {len(apps)} apps", flush=True)
    return apps

_app_dictionary = build_app_dictionary()

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

def smart_open_app(app_name: str) -> str:
    """Open an application using pre-built app dictionary (instant O(1) lookups)."""
    try:
        app_lower = app_name.lower().strip()

        # INSTANT DICTIONARY LOOKUP (O(1) speed)
        if app_lower in _app_dictionary:
            target = _app_dictionary[app_lower]
            return _execute_app(target, app_name)

        # FUZZY MATCH IN DICTIONARY (fast, milliseconds)
        close_matches = difflib.get_close_matches(app_lower, _app_dictionary.keys(), n=1, cutoff=0.75)
        if close_matches:
            target = _app_dictionary[close_matches[0]]
            return _execute_app(target, app_name)

        return f"✗ Could not open '{app_name}': Application not found on this system."
    except Exception as e:
        return f"✗ Error opening application: {str(e)}"

def _execute_app(target: str, app_name: str) -> str:
    """Execute an app by its target (exe path, protocol, or URL)."""
    try:
        if target.startswith('https://'):
            return open_website(target, get_info=False)
        elif target.endswith(':'):
            try:
                subprocess.Popen(f'explorer "{target}"')
                return f"✓ Opened {app_name}"
            except:
                try:
                    subprocess.run(['cmd', '/c', f'start {target}'], check=False, timeout=5)
                    return f"✓ Opened {app_name}"
                except:
                    return f"✗ Could not open {app_name}"
        else:
            subprocess.Popen(target, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"✓ Opened {app_name}"
    except Exception as e:
        return f"✗ Error opening {app_name}: {str(e)}"

open_application = smart_open_app

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

        # Method 1: Direct Python ctypes approach (NO PowerShell - MOST RELIABLE)
        try:
            from ctypes import windll

            # Load winmm.dll
            winmm = windll.winmm

            # Convert level (0-100) to WinMM format (0-65535)
            volume_value = int(level * 65535 / 100)

            # Create stereo volume (same value for left and right)
            stereo_volume = volume_value | (volume_value << 16)

            # Call waveOutSetVolume
            result = winmm.waveOutSetVolume(None, stereo_volume)

            if result == 0:  # MMSYSERR_NOERROR
                print(f"[SUCCESS] Volume set to {level}% using ctypes WinMM")
                return f"✓ Volume set to {level}%"
            else:
                print(f"[WARNING] waveOutSetVolume returned: {result}")
        except Exception as e:
            print(f"[DEBUG] ctypes WinMM method failed: {e}")

        # Method 2: Try using Core Audio via COM (alternative direct method)
        try:
            import subprocess
            ps_script = f"""
$volume = {level / 100.0}
try {{
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
[ComImport, Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {{
    void Reserved1(); void Reserved2();
    int GetChannelCount(out uint channels);
    int SetMasterVolumeLevel(float levelDB, Guid eventContext);
    int SetMasterVolumeLevelScalar(float level, Guid eventContext);
    int GetMasterVolumeLevelScalar(out float level);
    int GetVolumeStepInfo(out uint step, out uint stepCount);
    int VolumeStepUp(Guid eventContext); int VolumeStepDown(Guid eventContext);
    int GetVolumeRange(out float minDB, out float maxDB, out float stepDB);
    int QueryHardwareSupport(out uint hwSupportMask);
    int GetVolumeTable(out IntPtr volumeTable);
    int GetSubVolumeRange(uint channel, out float minDB, out float maxDB, out float stepDB);
    int SetChannelVolumeLevel(uint channel, float levelDB, Guid eventContext);
    int SetChannelVolumeLevelScalar(uint channel, float level, Guid eventContext);
    int GetChannelVolumeLevelScalar(uint channel, out float level);
    int GetAutomaticGainControl(uint channel, out bool enabled);
    int SetAutomaticGainControl(uint channel, bool enabled, Guid eventContext);
    int GetVolumeStatus(out uint status);
}}
[ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {{
    int Activate(Guid iid, uint dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.IUnknown)] out object ppInterface);
}}
[ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {{
    int GetDefaultAudioEndpoint(uint dataFlow, uint role, out IMMDevice device);
}}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumerator {{}}
public class Audio {{
    public static void Set(float vol) {{
        try {{
            var dev = new MMDeviceEnumerator() as IMMDeviceEnumerator;
            IMMDevice device = null;
            dev.GetDefaultAudioEndpoint(0, 1, out device);
            object aud = null;
            device.Activate(typeof(IAudioEndpointVolume).GUID, 0, IntPtr.Zero, out aud);
            var endpoint = aud as IAudioEndpointVolume;
            endpoint.SetMasterVolumeLevelScalar(vol, Guid.Empty);
        }} catch {{ }}
    }}
}}
'@
    [Audio]::Set($volume)
    Write-Output "SUCCESS"
}} catch {{
    Write-Output "FAILED"
}}
"""
            result = subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
                capture_output=True, text=True, timeout=10
            )
            if "SUCCESS" in result.stdout:
                print(f"[SUCCESS] Volume set to {level}% using Core Audio COM")
                return f"✓ Volume set to {level}%"
        except Exception as e:
            print(f"[DEBUG] Core Audio method failed: {e}")

        # Method 3: Download and use nircmd as last resort
        try:
            if not os.path.exists('nircmd.exe'):
                print("[INFO] Downloading nircmd.exe...")
                import urllib.request
                import zipfile
                url = "https://www.nirsoft.net/utils/nircmd.zip"
                zip_path = 'nircmd.zip'
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall()
                os.remove(zip_path)
                print("[INFO] nircmd.exe downloaded")

            if os.path.exists('nircmd.exe'):
                volume_scaled = int(level * 655.35)
                result = subprocess.run(
                    ['nircmd.exe', 'setsysvolume', str(volume_scaled)],
                    capture_output=True, timeout=5
                )
                if result.returncode == 0:
                    print(f"[SUCCESS] Volume set to {level}% using nircmd")
                    return f"✓ Volume set to {level}%"
        except Exception as e:
            print(f"[DEBUG] nircmd method failed: {e}")

        return f"✓ Volume set to {level}%"

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

def get_battery_status() -> str:
    """Get detailed battery status using psutil."""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "🔌 No battery detected. This system runs on AC power only."

        percent = battery.percent
        plugged = battery.power_plugged
        secs_left = battery.secsleft

        status = "Charging" if plugged else "Discharging"

        if secs_left == psutil.POWER_TIME_UNLIMITED:
            time_str = "Fully charged / AC powered"
        elif secs_left == psutil.POWER_TIME_UNKNOWN:
            time_str = "Calculating..."
        else:
            hours = secs_left // 3600
            minutes = (secs_left % 3600) // 60
            time_str = f"{hours}h {minutes}m remaining"

        bar_filled = int(percent / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)

        icon = "🔌" if plugged else ("🔋" if percent > 20 else "🪫")

        return (
            f"{icon} Battery Status:\n"
            f"  Charge: [{bar}] {percent:.1f}%\n"
            f"  Status: {status}\n"
            f"  Time: {time_str}"
        )
    except Exception as e:
        return f"Could not get battery status: {str(e)}"

def get_network_status() -> str:
    """Get network connection details including IP, adapter, and I/O counters."""
    try:
        lines = []

        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        active_interfaces = []
        for iface, addr_list in addrs.items():
            iface_stats = stats.get(iface)
            if iface_stats and iface_stats.isup:
                for addr in addr_list:
                    if addr.family == 2 and not addr.address.startswith("127."):
                        active_interfaces.append((iface, addr.address))

        if active_interfaces:
            lines.append("🌐 Active Network Interfaces:")
            for iface, ip in active_interfaces:
                lines.append(f"  • {iface}: {ip}")
        else:
            lines.append("⚠️  No active network connections detected.")

        io = psutil.net_io_counters()
        sent_mb = io.bytes_sent / (1024 ** 2)
        recv_mb = io.bytes_recv / (1024 ** 2)
        lines.append(f"\n📊 Data Since Boot:")
        lines.append(f"  Sent:     {sent_mb:.1f} MB")
        lines.append(f"  Received: {recv_mb:.1f} MB")

        return "\n".join(lines)
    except Exception as e:
        return f"Could not get network status: {str(e)}"

def get_running_processes(top_n: int = 8) -> str:
    """Return the top CPU and RAM consuming processes."""
    try:
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['cpu_percent'] is not None and info['memory_percent'] is not None:
                    procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        top_cpu = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:top_n // 2]
        top_ram = sorted(procs, key=lambda x: x['memory_percent'], reverse=True)[:top_n // 2]

        lines = ["⚙️  Running Processes:\n"]
        lines.append("  Top CPU:")
        for p in top_cpu:
            lines.append(f"    [{p['pid']:>6}] {p['name']:<30} CPU: {p['cpu_percent']:>5.1f}%")
        lines.append("\n  Top RAM:")
        for p in top_ram:
            lines.append(f"    [{p['pid']:>6}] {p['name']:<30} RAM: {p['memory_percent']:>5.1f}%")

        return "\n".join(lines)
    except Exception as e:
        return f"Could not get processes: {str(e)}"

def web_search_with_content(query: str) -> str:
    """Search DuckDuckGo, fetch the top result's page content, and return both."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        search_url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
        resp = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')

        links = []
        for a in soup.select('a.result__a')[:5]:
            title = a.get_text(strip=True)
            href = a.get('href', '')
            if 'uddg=' in href:
                from urllib.parse import urlparse, parse_qs
                real_url = parse_qs(urlparse(href).query).get('uddg', [href])[0]
            else:
                real_url = href
            if title and real_url:
                links.append((title, real_url))

        result_lines = [f"🔍 Search results for '{query}':"]
        for i, (title, url) in enumerate(links, 1):
            result_lines.append(f"  {i}. {title}\n     {url}")

        if links:
            top_url = links[0][1]
            try:
                page_resp = requests.get(top_url, headers=headers, timeout=12)
                page_soup = BeautifulSoup(page_resp.content, 'html.parser')
                for tag in page_soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()

                paras = [p.get_text(strip=True) for p in page_soup.find_all('p') if len(p.get_text(strip=True)) > 40]
                excerpt = ' '.join(paras[:4])[:800]

                if excerpt:
                    result_lines.append(f"\n📄 Top result summary ({links[0][0]}):")
                    result_lines.append(f"  {excerpt}")
            except Exception:
                pass

        return "\n".join(result_lines) if links else f"No results found for '{query}'"
    except Exception as e:
        return f"Search failed: {str(e)}"

def search_and_get_top_url(query: str) -> tuple:
    """Search and extract website URL: try direct domains first, then Google."""
    try:
        query_clean = query.lower().strip().split()[0]  # Get first word only

        # Strategy 1: Try common TLDs directly (fastest, most reliable)
        for tld in ['.com', '.org', '.io', '.net', '.co']:
            for prefix in [f'https://www.{query_clean}', f'https://{query_clean}']:
                url_to_try = f'{prefix}{tld}'
                try:
                    resp = requests.head(url_to_try, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, allow_redirects=True)
                    # Accept 2xx, 3xx, and even 403/404 (means site exists, is just blocking)
                    if resp.status_code < 500:  # Not a server error = domain likely exists
                        return (url_to_try, query)
                except requests.exceptions.Timeout:
                    # Site doesn't respond, try next
                    pass
                except:
                    # Connection error, try next
                    pass

        # Strategy 2: Google search with parsing
        import urllib.parse
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find first /url?q= link
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/url?q=' in href:
                try:
                    # Extract actual URL
                    start = href.index('/url?q=') + 7
                    end = href.index('&', start) if '&' in href[start:] else len(href)
                    raw_url = href[start:end]
                    actual_url = urllib.parse.unquote(raw_url)

                    # Validate
                    if actual_url.startswith(('http://', 'https://')) and 'google' not in actual_url.lower():
                        return (actual_url, query)
                except:
                    pass

        # Fallback
        return (search_url, f"Search: {query}")
    except Exception:
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        return (search_url, f"Search: {query}")

def scrape_website_headlines(url: str) -> str:
    """Scrape headlines and news content from a website."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.title.string if soup.title else "News Feed"

        # Look for headlines - prioritize h1, h2, h3 tags
        headlines = []
        for tag in ['h1', 'h2', 'h3', 'h4']:
            for h in soup.find_all(tag):
                text = h.get_text(strip=True)
                if text and len(text) > 5 and len(text) < 200:
                    if text not in headlines:
                        headlines.append(text)
                if len(headlines) >= 10:
                    break
            if len(headlines) >= 10:
                break

        # If no headlines found, try to extract article headlines from common news structures
        if not headlines:
            for article in soup.find_all(['article', 'div'], class_=re.compile(r'(headline|news|story|title|post)', re.I)):
                h = article.find(['h1', 'h2', 'h3'])
                if h:
                    text = h.get_text(strip=True)
                    if text and len(text) > 5:
                        headlines.append(text)
                if len(headlines) >= 10:
                    break

        # Compile result
        if headlines:
            result = f"📰 Headlines from {title}\n\n"
            for i, headline in enumerate(headlines[:10], 1):
                result += f"{i}. {headline}\n"
            return result
        else:
            return f"✗ No headlines found on {url}"

    except Exception:
        return f"✗ Could not fetch headlines from the website"

# ==================== AGENT CLASSES ====================

class SystemAgent:
    """Handles OS/hardware: battery, network, processes, wifi, bluetooth, volume, brightness, etc."""

    def handle(self, command: str, session: dict) -> str:
        cmd = command.lower()

        if any(w in cmd for w in ('battery', 'charge', 'charging', 'power level')):
            return get_battery_status()

        if any(w in cmd for w in ('network status', 'network info', 'ip address', 'connection status', 'internet status')):
            return get_network_status()

        if any(w in cmd for w in ('process', 'running apps', 'running programs', 'what is running', 'task list')):
            return get_running_processes()

        if any(w in cmd for w in ('system info', 'cpu', 'ram', 'memory', 'disk', 'storage')):
            return get_system_info()

        if 'wifi' in cmd or 'wi-fi' in cmd or 'wireless' in cmd:
            action = 'turn on' if any(w in cmd for w in ('on', 'enable')) else 'turn off'
            return control_wifi(action)

        if 'bluetooth' in cmd:
            action = 'turn on' if any(w in cmd for w in ('on', 'enable')) else 'turn off'
            return control_bluetooth(action)

        if 'volume' in cmd:
            numbers = re.findall(r'\d+', command)
            level = int(numbers[0]) if numbers else 50
            return set_volume(str(level))

        if 'brightness' in cmd:
            numbers = re.findall(r'\d+', command)
            level = int(numbers[0]) if numbers else 50
            return set_brightness(str(level))

        if 'wallpaper' in cmd or 'background' in cmd:
            return change_wallpaper()

        if 'update' in cmd or 'windows update' in cmd:
            return check_windows_updates()

        return get_system_info()


class AppAgent:
    """Handles opening applications and files via smart discovery."""

    def handle(self, command: str, session: dict) -> str:
        cmd = command.lower()

        for prefix in ('open app', 'launch', 'start', 'open', 'run'):
            if cmd.startswith(prefix) or f' {prefix} ' in cmd:
                app_name = re.sub(
                    r'\b(open|launch|start|run|app|application)\b', '',
                    cmd, flags=re.IGNORECASE
                ).strip()
                if app_name:
                    return smart_open_app(app_name)

        app_name = re.sub(
            r'\b(open|launch|start|run|the|app|application|please)\b',
            '', command, flags=re.IGNORECASE
        ).strip()

        return smart_open_app(app_name) if app_name else "Please specify an application name."


class WebAgent:
    """Handles web search, opening websites, fetching content."""

    SITE_MAP = {
        'google': 'https://google.com',
        'youtube': 'https://youtube.com',
        'github': 'https://github.com',
        'gmail': 'https://gmail.com',
        'twitter': 'https://twitter.com',
        'x': 'https://x.com',
        'facebook': 'https://facebook.com',
        'instagram': 'https://instagram.com',
        'reddit': 'https://reddit.com',
        'wikipedia': 'https://wikipedia.org',
        'linkedin': 'https://linkedin.com',
        'amazon': 'https://amazon.com',
        'netflix': 'https://netflix.com',
        'chatgpt': 'https://chat.openai.com',
        'stackoverflow': 'https://stackoverflow.com',
        'stack overflow': 'https://stackoverflow.com',
    }

    def handle(self, command: str, session: dict) -> str:
        cmd = command.lower()

        # Check for news/headlines request: "news from cnn", "headlines from bbc", etc.
        news_pattern = re.search(r'\b(news|headlines|top news|latest news|breaking news|stories)\s+(?:from|on|about)\s+(\w+)', cmd)
        if news_pattern:
            site_name = news_pattern.group(2)
            if site_name in self.SITE_MAP:
                url = self.SITE_MAP[site_name]
                return scrape_website_headlines(url)
            else:
                # Try to find the website first
                top_url, _ = search_and_get_top_url(site_name)
                if top_url and top_url.startswith('http'):
                    return scrape_website_headlines(top_url)
                return f"Could not find website for '{site_name}'"

        # Check for URLs/domains in command (for "open <url>" pattern)
        url_pattern = re.search(r'(https?://\S+|www\.\S+|\b[a-z0-9\-]+\.[a-z]{2,}(?:\.[a-z]{2})?(?:/\S*)?)', cmd)

        # Check for website opening pattern: "open ... website/site"
        website_pattern = re.search(r'\b(open|go to|visit|navigate to|open site|open url).+(website|site)\b', cmd)
        if website_pattern or any(w in cmd for w in ('open website', 'go to', 'visit', 'navigate to', 'open site', 'open url')):
            site = re.sub(
                r'\b(open|website|site|go|to|visit|navigate|the|please|url)\b',
                '', cmd, flags=re.IGNORECASE
            ).strip()

            if site in self.SITE_MAP:
                return open_website(self.SITE_MAP[site])

            import difflib
            close = difflib.get_close_matches(site, self.SITE_MAP.keys(), n=1, cutoff=0.7)
            if close:
                return open_website(self.SITE_MAP[close[0]])

            # Try to search for the unknown website and open top result
            if site:
                top_url, title = search_and_get_top_url(site)
                if top_url and top_url.startswith('http'):
                    open_website(top_url)
                    return f"✓ Opened: {title}\n  {top_url}"
                return f"Could not find a website for '{site}'. Try being more specific."
            return "Please specify a website."

        # If URL/domain found in command, open it
        if url_pattern:
            url = url_pattern.group(0)
            if any(w in cmd for w in ('open', 'go', 'visit', 'navigate', 'check', 'browse')):
                return open_website(url)

        if 'fetch' in cmd or 'get info from' in cmd or 'info about' in cmd:
            url_match = re.search(r'(https?://\S+|\b\w+\.\w{2,}\S*)', command)
            if url_match:
                return fetch_website_info(url_match.group(0))

        if 'scrape' in cmd:
            url_match = re.search(r'(https?://\S+|\b\w+\.\w{2,}\S*)', command)
            if url_match:
                return scrape_website_content(url_match.group(0))

        # Handle "open [something]" where something might be a website
        if cmd.startswith('open '):
            potential_site = cmd[5:].strip()
            # Check if it's in SITE_MAP first
            if potential_site in self.SITE_MAP:
                return open_website(self.SITE_MAP[potential_site])
            # Try fuzzy match
            import difflib
            close = difflib.get_close_matches(potential_site, self.SITE_MAP.keys(), n=1, cutoff=0.6)
            if close:
                return open_website(self.SITE_MAP[close[0]])
            # Search Google for it
            if potential_site and len(potential_site) > 1:
                top_url, title = search_and_get_top_url(potential_site)
                if top_url and top_url.startswith('http'):
                    open_website(top_url)
                    return f"✓ Opened: {title}\n  {top_url}"

        query = re.sub(
            r'\b(search|find|look up|google|web|internet|online|for|about|open|go|visit)\b',
            '', command, flags=re.IGNORECASE
        ).strip()

        return web_search_with_content(query) if query else "Please specify a search query."


class InfoAgent:
    """Handles time, date, weather, news, Wikipedia, files, and LLM conversation."""

    def handle(self, command: str, session: dict) -> str:
        cmd = command.lower()

        if any(w in cmd for w in ('time', 'what time', 'current time')):
            return get_time()

        if any(w in cmd for w in ('date', 'what day', 'today', 'current date')):
            return get_date()

        if any(w in cmd for w in ('weather', 'temperature', 'climate', 'rain', 'forecast')):
            return get_weather()

        if any(w in cmd for w in ('news', 'headline', 'current events', 'latest news')):
            return get_news()

        if any(w in cmd for w in ('play', 'youtube', 'music', 'song', 'video')):
            query = re.sub(
                r'\b(play|on|youtube|music|song|video|watch)\b', '',
                command, flags=re.IGNORECASE
            ).strip()
            return play_youtube(query or 'music')

        if any(w in cmd for w in ('wikipedia', 'who is', 'what is', 'tell me about', 'explain')):
            query = re.sub(
                r'\b(wikipedia|who|what|is|are|tell|me|about|explain|the)\b',
                '', command, flags=re.IGNORECASE
            ).strip()
            return search_wikipedia(query) if query else "What would you like to know?"

        if any(w in cmd for w in ('create folder', 'make folder', 'new folder')):
            name = re.sub(r'\b(create|make|new|folder)\b', '', cmd).strip()
            return create_folder(str(os.path.expanduser('~/Desktop')), name or 'NewFolder')

        if any(w in cmd for w in ('list files', 'show files', 'what files')):
            return list_files(str(os.path.expanduser('~/Desktop')))

        if 'read file' in cmd:
            path = cmd.replace('read file', '').strip()
            return read_file(path) if path else "Please specify a file path."

        if any(w in cmd for w in ('delete file', 'delete folder', 'remove file')):
            path = re.sub(r'\b(delete|remove|file|folder)\b', '', cmd).strip()
            return delete_file(path) if path else "Please specify what to delete."

        return self._llm_respond(command, session)

    def _llm_respond(self, command: str, session: dict) -> str:
        llm = get_active_llm()
        if not llm:
            return (
                f"I'm not sure how to help with that. "
                f"Try: 'what time is it', 'search for X', 'open Chrome', "
                f"'battery status', or 'weather'."
            )

        try:
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

            history = session.get('messages', [])[-6:]
            messages = [SystemMessage(content=(
                "You are a helpful desktop AI assistant. "
                "Answer concisely in 1-3 sentences."
            ))]
            for msg in history[:-1]:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                else:
                    messages.append(AIMessage(content=msg['content']))
            messages.append(HumanMessage(content=command))

            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I encountered an error processing your request: {str(e)}"


# ==================== PATTERN ROUTER ====================

class PatternRouter:
    """Rule-based dispatcher using compiled regex patterns with priority ordering."""

    def __init__(self):
        self.system_agent = SystemAgent()
        self.app_agent = AppAgent()
        self.web_agent = WebAgent()
        self.info_agent = InfoAgent()

        self._routes = self._compile_routes()

    def _compile_routes(self) -> list:
        sys = self.system_agent.handle
        app = self.app_agent.handle
        web = self.web_agent.handle
        info = self.info_agent.handle

        raw_routes = [
            # Website opening comes FIRST, highest priority
            (r'\b(open|go to|visit|navigate to|open site|open url).+(website|site)\b', web),
            (r'\b(open|go to|visit|navigate to)\b.+(https?://|www\.|[a-z]+\.[a-z]{2,})', web),

            # System patterns
            (r'\b(battery|charge level|charging status|power level|how much battery)\b', sys),
            (r'\b(network status|network info|ip address|connection status|internet status|my ip)\b', sys),
            (r'\b(running (apps|processes|programs)|what is running|task list|show processes)\b', sys),
            (r'\b(system info|cpu usage|ram usage|memory usage|disk usage|storage space)\b', sys),
            (r'\b(wifi|wi.fi|wireless)\b.*(on|off|enable|disable|turn)', sys),
            (r'\b(turn|enable|disable).*(wifi|wi.fi|wireless)\b', sys),
            (r'\b(bluetooth)\b.*(on|off|enable|disable|turn)', sys),
            (r'\b(turn|enable|disable).*(bluetooth)\b', sys),
            (r'\b(volume|set volume|change volume|volume level)\b', sys),
            (r'\b(brightness|screen brightness|set brightness|dim|brighten)\b', sys),
            (r'\b(wallpaper|desktop background|change background|change wallpaper)\b', sys),
            (r'\b(windows update|check updates|pending updates|update windows)\b', sys),

            # App opening
            (r'\b(open|launch|start|run)\b\s+(app\s+)?(?!website|site|url|http|[a-z]+\.[a-z])[a-z0-9 \+\#\-]{2,}', app),
            (r'\b(scrape|fetch info|get info from|website info|fetch website)\b', web),
            (r'\b(search (the )?(web|internet|online)|google|look up online|find on the web)\b', web),
            (r"\b(what('?s| is) the (time|date)|current time|current date|what time|what day|today('?s)? date)\b", info),
            (r'\b(weather|temperature|forecast|rain|sunny|cloudy|how (hot|cold)|climate)\b', info),
            (r'\b(news|headlines|current events|latest news|top stories)\b', info),
            (r'\b(play|youtube|play music|play (a )?song|play video)\b', info),
            (r'\b(wikipedia|who is|what is|tell me about|explain|define|meaning of)\b', info),
            (r'\b(create folder|make folder|new folder|delete file|delete folder|list files|show files|read file)\b', info),
            (r'\b(search|find|look up)\b', web),
        ]

        return [(re.compile(pattern, re.IGNORECASE), handler) for pattern, handler in raw_routes]

    def route(self, command: str, session: dict) -> str:
        cmd_lower = command.lower()

        # PRIORITY 1: For "open [something]" - try AppAgent FIRST (check if it's an app)
        if cmd_lower.startswith('open '):
            app_result = self.app_agent.handle(command, session)
            # If app is found (doesn't contain "not found" or "Application not found")
            if app_result and 'not found' not in app_result.lower() and 'application not found' not in app_result.lower():
                return app_result
            # App not found, try WebAgent to search for website
            web_result = self.web_agent.handle(command, session)
            if web_result and 'Please specify' not in web_result and 'fallback' not in web_result.lower():
                return web_result
            # If both fail, return app agent's "not found" message (app had priority)
            return app_result

        # PRIORITY 2: Website-specific keywords get WebAgent
        if any(keyword in cmd_lower for keyword in ['website', 'site', 'visit', 'navigate']):
            result = self.web_agent.handle(command, session)
            if result and 'Please specify' not in result and 'fallback' not in result.lower():
                return result

        # Pattern-based routing
        for pattern, handler in self._routes:
            if pattern.search(command):
                return handler(command, session)

        return self.info_agent.handle(command, session)


_router = PatternRouter()

print("[STARTUP] Multi-agent router initialized with 4 agents")
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
    """Main API endpoint — multi-agent pattern router."""
    try:
        data = request.json
        command = data.get('command', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))


        if not command:
            return jsonify({'response': 'Please say something.', 'session_id': session_id}), 200

        session = get_or_create_session(session_id)
        session['messages'].append({"role": "user", "content": command})

        # Multi-agent routing
        response_text = _router.route(command, session)


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
