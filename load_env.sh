#!/bin/bash
# Source this file to load environment variables from .env
# Usage: source load_env.sh

if [ -f .env ]; then
    echo "🔑 Loading environment variables from .env..."
    set -a
    source .env
    set +a
    echo "✅ Environment variables loaded!"

    # Show which providers are configured
    echo "📋 Configured LLM providers:"
    [ ! -z "$OPENAI_API_KEY" ] && echo "  ✅ OpenAI"
    [ ! -z "$GOOGLE_API_KEY" ] && echo "  ✅ Google Gemini"
    [ ! -z "$ANTHROPIC_API_KEY" ] && echo "  ✅ Anthropic Claude"
    echo "  ℹ️  Ollama (check if service is running)"
else
    echo "❌ .env file not found!"
    echo "💡 Create one from .env.example:"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your API keys"
fi
