"""
Extended Tools for AI Assistant - Agentic Task Execution
Enables opening websites, applications, sending emails, and more
"""

import webbrowser
import subprocess
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from typing import Optional

# ==================== WEBSITE & APPLICATION TOOLS ====================

def open_website(url: str) -> str:
    """Open a website in the default browser."""
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'https://' + url

        webbrowser.open(url)
        return f"✓ Opened {url} in your browser"
    except Exception as e:
        return f"✗ Could not open website: {str(e)}"

def open_application(app_name: str) -> str:
    """Open an application by name."""
    try:
        # Map common app names to executables
        app_map = {
            'gmail': 'https://gmail.com',
            'google': 'https://google.com',
            'youtube': 'https://youtube.com',
            'github': 'https://github.com',
            'twitter': 'https://twitter.com',
            'facebook': 'https://facebook.com',
            'linkedin': 'https://linkedin.com',
            'reddit': 'https://reddit.com',
            'gmail app': 'mail',  # Windows Mail
            'calculator': 'calc.exe',
            'notepad': 'notepad.exe',
            'paint': 'mspaint.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'notepad++': 'notepad++.exe',
            'vs code': 'code',
            'vscode': 'code',
        }

        app_lower = app_name.lower().strip()

        # Check if it's a web service
        if app_lower in app_map and app_map[app_lower].startswith('https://'):
            return open_website(app_map[app_lower])

        # Otherwise try to open as application
        if app_lower in app_map:
            executable = app_map[app_lower]
        else:
            executable = app_name

        # Try to launch the application
        subprocess.Popen(executable)
        return f"✓ Opened {app_name}"
    except Exception as e:
        return f"✗ Could not open {app_name}: {str(e)}"

# ==================== EMAIL TOOLS ====================

# Load email config from file if it exists
EMAIL_CONFIG_FILE = "email_config.json"

def load_email_config() -> dict:
    """Load email configuration."""
    if os.path.exists(EMAIL_CONFIG_FILE):
        try:
            with open(EMAIL_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_email_config(config: dict):
    """Save email configuration."""
    with open(EMAIL_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email (requires email config to be set up first)."""
    try:
        config = load_email_config()

        if not config.get('email') or not config.get('password'):
            return (
                "⚠️  Email not configured. To send emails:\n"
                "1. Create email_config.json with:\n"
                '{"email": "your-email@gmail.com", "password": "your-app-password"}\n'
                "2. Use Gmail app password (not regular password)\n"
                "3. Try again"
            )

        sender_email = config['email']
        sender_password = config['password']
        smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = config.get('smtp_port', 587)

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

        return f"✓ Email sent to {to_email}: {subject}"
    except Exception as e:
        return f"✗ Failed to send email: {str(e)}"

def configure_email(email: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587) -> str:
    """Configure email settings for sending emails."""
    try:
        config = {
            "email": email,
            "password": password,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port
        }
        save_email_config(config)
        return f"✓ Email configured for {email}"
    except Exception as e:
        return f"✗ Failed to configure email: {str(e)}"

# ==================== FILE & SYSTEM TOOLS ====================

def open_file(file_path: str) -> str:
    """Open a file with its default application."""
    try:
        if not os.path.exists(file_path):
            return f"✗ File not found: {file_path}"

        # Windows
        os.startfile(file_path)
        return f"✓ Opened {file_path}"
    except Exception as e:
        return f"✗ Could not open file: {str(e)}"

def open_folder(folder_path: str) -> str:
    """Open a folder in file explorer."""
    try:
        if not os.path.exists(folder_path):
            return f"✗ Folder not found: {folder_path}"

        # Windows
        os.startfile(folder_path)
        return f"✓ Opened folder: {folder_path}"
    except Exception as e:
        return f"✗ Could not open folder: {str(e)}"

# ==================== INFORMATION TOOLS ====================

def get_available_apps() -> str:
    """Get list of commonly available applications."""
    apps = [
        "Gmail (web)",
        "Google Search",
        "YouTube",
        "GitHub",
        "Twitter",
        "Facebook",
        "LinkedIn",
        "Reddit",
        "Calculator",
        "Notepad",
        "Paint",
        "Microsoft Word",
        "Microsoft Excel",
        "Chrome",
        "Firefox",
        "Edge",
        "VS Code",
    ]
    return "Available apps to open:\n• " + "\n• ".join(apps)

# ==================== ALL TOOLS LIST ====================

EXTENDED_TOOLS = [
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
        "description": "Open an application or website by name",
        "inputSchema": {
            "type": "object",
            "properties": {
                "app_name": {"type": "string", "description": "App name (e.g., 'Gmail', 'Calculator', 'Chrome', 'Notepad')"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to_email": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body text"}
            },
            "required": ["to_email", "subject", "body"]
        }
    },
    {
        "name": "configure_email",
        "description": "Configure email settings for sending emails",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Your email address"},
                "password": {"type": "string", "description": "Email password or app password"},
                "smtp_server": {"type": "string", "description": "SMTP server (default: smtp.gmail.com)"},
                "smtp_port": {"type": "integer", "description": "SMTP port (default: 587)"}
            },
            "required": ["email", "password"]
        }
    },
    {
        "name": "open_file",
        "description": "Open a file with its default application",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Full path to the file"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "open_folder",
        "description": "Open a folder in file explorer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Full path to the folder"}
            },
            "required": ["folder_path"]
        }
    },
    {
        "name": "get_available_apps",
        "description": "Get list of applications that can be opened",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

# ==================== TOOL EXECUTION ====================

async def execute_extended_tool(name: str, arguments: dict) -> str:
    """Execute an extended tool."""
    if name == "open_website":
        return open_website(arguments.get("url", ""))
    elif name == "open_application":
        return open_application(arguments.get("app_name", ""))
    elif name == "send_email":
        return send_email(
            arguments.get("to_email", ""),
            arguments.get("subject", ""),
            arguments.get("body", "")
        )
    elif name == "configure_email":
        return configure_email(
            arguments.get("email", ""),
            arguments.get("password", ""),
            arguments.get("smtp_server", "smtp.gmail.com"),
            arguments.get("smtp_port", 587)
        )
    elif name == "open_file":
        return open_file(arguments.get("file_path", ""))
    elif name == "open_folder":
        return open_folder(arguments.get("folder_path", ""))
    elif name == "get_available_apps":
        return get_available_apps()
    else:
        return f"Unknown tool: {name}"
