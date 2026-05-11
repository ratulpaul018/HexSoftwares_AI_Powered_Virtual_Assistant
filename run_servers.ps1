# PowerShell script to run both Flask app and MCP server

Write-Host "Starting AI Assistant - Flask + MCP Server" -ForegroundColor Cyan

# Start Flask app in background
Write-Host "Starting Flask app on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$pwd' && python app.py`"" -WindowStyle Normal

# Wait a moment for Flask to start
Start-Sleep -Seconds 3

# Start MCP server in another window
Write-Host "Starting MCP server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$pwd' && python mcp_server.py`"" -WindowStyle Normal

Write-Host "`n✓ Both servers are starting!`n" -ForegroundColor Green
Write-Host "Flask Web UI: http://localhost:8000" -ForegroundColor Cyan
Write-Host "MCP Server: Running on stdio (local, no port)" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
