#!/bin/bash
# Development container setup script

echo "🚀 Setting up Resume LLM development environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Check for .env file and provide guidance
if [ -f .env ]; then
    echo "✅ .env file found!"
    echo "🔑 Environment variables will be loaded from .env file"

    # Load environment variables for the current session
    set -a
    source .env
    set +a

    echo "📋 Available LLM providers:"
    if [ ! -z "$OPENAI_API_KEY" ]; then
        echo "  ✅ OpenAI (API key configured)"
    else
        echo "  ❌ OpenAI (no API key)"
    fi

    if [ ! -z "$GOOGLE_API_KEY" ]; then
        echo "  ✅ Google Gemini (API key configured)"
    else
        echo "  ❌ Google Gemini (no API key)"
    fi

    if [ ! -z "$ANTHROPIC_API_KEY" ]; then
        echo "  ✅ Anthropic Claude (API key configured)"
    else
        echo "  ❌ Anthropic Claude (no API key)"
    fi

    echo "  ℹ️  Ollama (local - check if running)"

else
    echo "⚠️  .env file not found"
    echo "📝 To configure API keys:"
    echo "   1. Copy .env.example to .env"
    echo "   2. Edit .env with your API keys"
    echo "   3. Restart the dev container or source .env"
    echo ""
    echo "   cp .env.example .env"
    echo "   # Edit .env with your keys"
fi

# Set up Python path
export PYTHONPATH="/workspaces/resume-llm/src:$PYTHONPATH"

echo ""
echo "🎯 Quick start commands:"
echo "   # Test Gemini integration"
echo "   python run_tests.py"
echo ""
echo "   # Start the API server"
echo "   python -m resume_llm.api.main"
echo ""
echo "   # Use the CLI"
echo "   python -m resume_llm.cli.main --help"
echo ""
echo "✨ Development environment ready!"
