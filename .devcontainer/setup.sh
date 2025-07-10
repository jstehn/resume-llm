#!/bin/bash
# Development container setup script

echo "🚀 Setting up Resume LLM development environment..."

# --- Load Environment Variables ---
DEVCONTAINER_ENV_FILE=".devcontainer/devcontainer.env"

if [ -f "$DEVCONTAINER_ENV_FILE" ]; then
    echo "✅ $DEVCONTAINER_ENV_FILE file found!"
    echo "🔑 Environment variables will be loaded from $DEVCONTAINER_ENV_FILE"

    set -a
    source "$DEVCONTAINER_ENV_FILE"
    set +a

    echo "📋 LLM Provider API Key Status:"
    if [ ! -z "$OPENAI_API_KEY" ]; then echo "  ✅ OpenAI (API key configured)"; else echo "  ❌ OpenAI (OPENAI_API_KEY not found)"; fi
    if [ ! -z "$GOOGLE_API_KEY" ]; then echo "  ✅ Google Gemini (API key configured)"; else echo "  ❌ Google Gemini (GOOGLE_API_KEY not found)"; fi
    if [ ! -z "$ANTHROPIC_API_KEY" ]; then echo "  ✅ Anthropic Claude (API key configured)"; else echo "  ❌ Anthropic Claude (ANTHROPIC_API_KEY not found)"; fi
else
    echo "⚠️  $DEVCONTAINER_ENV_FILE file not found. API keys might not be set."
    echo "   Consider creating it: cp .devcontainer/devcontainer.env.example .devcontainer/devcontainer.env"
fi

echo ""

# --- Install Project and Development Dependencies using pip ---
echo "📦 Installing project dependencies and 'dev' optional dependencies from pyproject.toml..."
pip3 install --user --upgrade --no-cache-dir -e ".[dev]" || \
{
    echo "❌ ERROR: Failed to install Python dependencies from pyproject.toml."
    echo "Please check your pyproject.toml file and your internet connection."
    exit 1
}
echo "✅ All project and development dependencies installed successfully."

echo ""

# --- Confirm PYTHONPATH ---
echo "🌐 Final PYTHONPATH is: $PYTHONPATH"

echo ""

# --- Quick Start Commands ---
echo "🎯 Quick start commands:"
echo "   # To run tests:"
echo "   python run_tests.py"
echo ""
echo "   # To start the API server:"
echo "   python -m resume_llm.api.main"
echo ""
echo "   # To use the command-line interface:"
echo "   resume-llm --help"
echo ""

echo "✨ Development environment ready!"
