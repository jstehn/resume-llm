# Dev Container Environment Setup

This project includes a fully configured development container that automatically sets up the Python environment and loads your API keys.

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
1. Open the project in VS Code
2. When prompted, click "Reopen in Container"
3. The container will automatically:
   - Install all Python dependencies
   - Load environment variables from `.env` if it exists
   - Configure VS Code extensions for Python development
   - Set up the development environment

### Option 2: Manual Environment Setup
If you're not using the dev container:

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Load environment variables
source load_env.sh
```

## 🔑 Environment Variables

The dev container automatically detects and loads API keys from your `.env` file:

### Supported Providers:
- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Google Gemini**: Set `GOOGLE_API_KEY` for Gemini models (Free tier available!)
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models

### Setup Instructions:

1. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys**:
   ```bash
   # Edit .env file
   GOOGLE_API_KEY=your-google-api-key-here
   OPENAI_API_KEY=your-openai-api-key-here
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

3. **Verify setup**:
   ```bash
   python run_tests.py
   ```

## 🧪 Testing

The container includes comprehensive test suites:

```bash
# Run all tests
python run_tests.py

# Test specific components
python tests/test_gemini_integration.py
python tests/test_gemini_resume_scenarios.py

# Run with pytest
pytest tests/ -v
```

## 🛠 Development Tools

The dev container includes:
- **Python 3.12** with all dependencies
- **VS Code extensions**: Python, Pylint, Black formatter, Jupyter
- **Port forwarding**: Port 8000 for the API server
- **Environment detection**: Automatic API key validation
- **Test runners**: pytest and custom test suites

## 📁 File Structure

```
.devcontainer/
├── devcontainer.json          # Container configuration
├── setup.sh                   # Automatic setup script
└── devcontainer.env.example   # Alternative env file location

load_env.sh                     # Manual environment loader
run_tests.py                    # Comprehensive test runner
```

## 🔧 Customization

### Adding New API Keys
1. Add to `.env` file
2. Update `src/resume_llm/config/settings.py`
3. Add provider to `src/resume_llm/services/llm.py`

### Modifying Container
Edit `.devcontainer/devcontainer.json` to:
- Add VS Code extensions
- Change Python version
- Add additional tools
- Modify port forwarding

## 🎯 Quick Commands

Once the container is running:

```bash
# Test Gemini integration
python run_tests.py

# Start API server
python -m resume_llm.api.main

# Use CLI tool
python -m resume_llm.cli.main --help

# Load environment variables manually
source load_env.sh
```

## 🚨 Troubleshooting

### Container won't start
- Ensure Docker is running
- Check `.devcontainer/devcontainer.json` syntax

### API keys not working
- Verify `.env` file exists and has correct format
- Check for spaces or quotes around API keys
- Restart container after adding new keys

### Tests failing
- Run `source load_env.sh` to load environment variables
- Verify API keys are valid
- Check internet connection for API calls

### Missing dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or rebuild container
# Ctrl+Shift+P -> "Dev Containers: Rebuild Container"
```
