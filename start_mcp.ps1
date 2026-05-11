# Start MCP Server with chosen backend
# Usage: .\start_mcp.ps1 ollama
#        .\start_mcp.ps1 lm_studio
#        .\start_mcp.ps1 jan

param(
    [string]$Backend = "ollama"
)

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Universal MCP Server - Free Forever Local AI       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Set environment variables based on backend
switch ($Backend.ToLower()) {
    "ollama" {
        Write-Host "✓ Using: Ollama (localhost:11434)" -ForegroundColor Green
        Write-Host "  Model: llama3.2" -ForegroundColor Green
        $env:LLM_BACKEND = "ollama"
        $env:LLM_MODEL = "llama3.2"
        $env:LLM_BASE_URL = "http://localhost:11434"
        Write-Host "`n📋 Make sure Ollama is running!" -ForegroundColor Yellow
        Write-Host "   Run: ollama serve" -ForegroundColor Yellow
    }
    "lm_studio" {
        Write-Host "✓ Using: LM Studio (localhost:1234)" -ForegroundColor Green
        Write-Host "  Model: mistral-7b (or your choice)" -ForegroundColor Green
        $env:LLM_BACKEND = "lm_studio"
        $env:LLM_MODEL = "mistral-7b"
        $env:LLM_BASE_URL = "http://localhost:1234"
        Write-Host "`n📋 Make sure LM Studio is running!" -ForegroundColor Yellow
        Write-Host "   1. Open LM Studio app" -ForegroundColor Yellow
        Write-Host "   2. Go to 'Local Server'" -ForegroundColor Yellow
        Write-Host "   3. Click 'Start Server'" -ForegroundColor Yellow
    }
    "jan" {
        Write-Host "✓ Using: Jan.ai (localhost:1337)" -ForegroundColor Green
        Write-Host "  Model: mistral-7b (or your choice)" -ForegroundColor Green
        $env:LLM_BACKEND = "jan"
        $env:LLM_MODEL = "mistral-7b"
        $env:LLM_BASE_URL = "http://localhost:1337"
        Write-Host "`n📋 Make sure Jan.ai is running!" -ForegroundColor Yellow
        Write-Host "   1. Open Jan.ai app" -ForegroundColor Yellow
        Write-Host "   2. Go to Settings → API" -ForegroundColor Yellow
        Write-Host "   3. Enable local API server" -ForegroundColor Yellow
    }
    default {
        Write-Host "❌ Unknown backend: $Backend" -ForegroundColor Red
        Write-Host "`nAvailable backends:" -ForegroundColor Yellow
        Write-Host "  • ollama (default)" -ForegroundColor Yellow
        Write-Host "  • lm_studio" -ForegroundColor Yellow
        Write-Host "  • jan" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Starting MCP Server..." -ForegroundColor Cyan
Write-Host ""

# Start the server
python mcp_server_universal.py
