"""
MCP Server - Exposes AI Assistant tools locally
Allows Claude Code to directly invoke tools via Model Context Protocol
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
from mcp.types import Tool, TextContent, ToolResult

# Tool implementations (shared with Flask app)

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
            return f"No detailed results found for '{query}'. You can search manually online."
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

# Tool definitions for MCP
TOOLS = [
    {
        "name": "play_youtube",
        "description": "Play a song or video on YouTube by searching and auto-playing",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Song or video name to play"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_web",
        "description": "Search the web for information using DuckDuckGo",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get current weather information",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_news",
        "description": "Get latest news headlines",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "send_whatsapp",
        "description": "Send a WhatsApp message to a contact",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contact_name": {
                    "type": "string",
                    "description": "Contact name (must exist in contacts.json)"
                },
                "message": {
                    "type": "string",
                    "description": "Message to send"
                }
            },
            "required": ["contact_name", "message"]
        }
    },
    {
        "name": "get_system_info",
        "description": "Get system performance information (CPU, RAM, disk usage)",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_time",
        "description": "Get the current time",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_date",
        "description": "Get today's date",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "search_wikipedia",
        "description": "Search Wikipedia for information about a person or topic",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Person or topic to search"
                }
            },
            "required": ["query"]
        }
    }
]

# Tool execution
async def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool by name with given arguments"""
    if name == "play_youtube":
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
    else:
        return f"Unknown tool: {name}"

# Initialize MCP server
server = Server("ai-assistant-mcp")

@server.list_tools()
async def list_tools():
    """List all available tools"""
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[ToolResult]:
    """Handle tool calls from Claude"""
    try:
        result = await execute_tool(name, arguments)
        return [ToolResult(
            type="text",
            text=result
        )]
    except Exception as e:
        return [ToolResult(
            type="text",
            text=f"Error executing {name}: {str(e)}",
            isError=True
        )]

async def main():
    """Run the MCP server"""
    print("Starting AI Assistant MCP Server on stdio...")
    print("Tools available: play_youtube, search_web, get_weather, get_news, send_whatsapp, get_system_info, get_time, get_date, search_wikipedia")
    async with server:
        await server.start()

if __name__ == "__main__":
    asyncio.run(main())
