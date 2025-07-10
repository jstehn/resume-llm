#!/bin/bash
# Development container setup script

echo "🚀 Setting up Resume LLM development environment..."

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
