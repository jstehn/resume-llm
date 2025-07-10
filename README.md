# Resume LLM

An AI-powered resume refinement tool that helps you tailor your resume for specific job applications using Large Language Models and the JSON Resume standard.

## Status

Currently, the agents are not yet well tested. Functionality is redumentary as I focus on building out the infrastructure that the agent can utilize (users, api, resume history, jobs, etc.).

## Features

- **Resume Ingestion**: Convert resumes from various formats (PDF, text, JSON Resume) into a standardized JSON format
- **AI-Powered Analysis**: Use LangGraph agents to analyze job descriptions and identify key requirements
- **Smart Optimization**: Get specific suggestions for improving your resume for each job application
- **JSON Resume Validation**: Comprehensive validation against the official JSON Resume schema
- **Schema Compliance**: Automatic null value removal and schema validation to ensure clean, compliant resumes
- **Multiple LLM Support**: Works with OpenAI GPT models, Google Gemini, or other LangChain-compatible providers
- **Version Control**: Track different versions of your resume and their modifications
- **User Management**: Support for multiple users with their own configurations and API keys
- **Conversation History**: Stateful AI agent that remembers previous interactions
- **PDF Export**: Generate professional PDF resumes from JSON Resume data
- **REST API**: Complete API for integration with web applications
- **CLI Interface**: Command-line tools for local usage

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **AI Framework**: LangChain, LangGraph for agent workflows
- **Resume Standard**: [JSON Resume](https://jsonresume.org/) for structured data
- **Schema Validation**: jsonschema library for JSON Resume compliance
- **PDF Generation**: ReportLab for professional resume PDFs
- **Database**: SQLite for simplicity and portability
- **Data Processing**: Automatic null value removal and JSON extraction from LLM responses

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/jstehn/resume-llm.git
cd resume-llm
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install the package**:
```bash
pip install -e .
```

4. **Set up environment variables** (copy and modify .env.example):
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Initialize the database**:
```bash
resume-llm init
```

## Quick Start

### Command Line Usage

1. **Check available LLM providers**:
```bash
resume-llm providers
```

2. **Validate a JSON Resume**:
```bash
resume-llm validate data/examples/sample_resume.json
```

3. **Optimize a resume for a job**:
```bash
resume-llm optimize resume.json job_description.txt --output optimized_resume.json
```

4. **Start the API server**:
```bash
resume-llm serve --host 0.0.0.0 --port 8000
```

### Python API Usage

```python
import asyncio
from resume_llm.models.resume import JSONResume
from resume_llm.agents import ResumeAgent

async def optimize_resume():
    # Load your resume (JSON Resume format)
    with open("my_resume.json", "r") as f:
        resume_data = JSONResume(**json.load(f))

    # Load job description
    with open("job_description.txt", "r") as f:
        job_description = f.read()

    # Create and run the optimization agent
    agent = ResumeAgent()
    result = await agent.run(resume_data, job_description)

    # Get the optimized resume
    optimized_resume = result.get("optimized_resume")
    suggestions = result.get("analysis_results", {}).get("suggestions", {})

    return optimized_resume, suggestions

# Run the optimization
asyncio.run(optimize_resume())
```

### REST API Usage

Start the API server:
```bash
resume-llm serve
```

Then use the API endpoints:

- `POST /api/v1/users/` - Create a new user
- `POST /api/v1/resumes/users/{user_id}/versions` - Upload a resume version
- `POST /api/v1/jobs/applications` - Create a job application
- `POST /api/v1/jobs/analyze` - Analyze resume-job match
- `POST /api/v1/jobs/applications/{id}/optimize` - Optimize resume for job

API documentation is available at `http://localhost:8000/docs` when the server is running.

## Configuration

### Environment Variables

- `DATABASE_URL`: SQLite database path (default: `sqlite:///./resume_llm.db`)
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `GOOGLE_API_KEY`: Google API key for Gemini models

### LLM Providers

The system supports multiple LLM providers:

1. **OpenAI**: Set `OPENAI_API_KEY` environment variable
2. **Google Gemini**: Set `GOOGLE_API_KEY` environment variable
3. **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable

The system will automatically detect available providers and use the best one available.

## Project Structure

```
resume-llm/
├── src/resume_llm/
│   ├── agents/           # LangGraph AI agents
│   ├── api/             # FastAPI REST API
│   ├── cli/             # Command-line interface
│   ├── config/          # Configuration management
│   ├── database/        # SQLAlchemy models and migrations
│   ├── models/          # Pydantic data models
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
├── data/
│   ├── examples/        # Sample resumes and job descriptions
│   ├── schemas/         # JSON schemas
│   └── templates/       # PDF templates
├── tests/               # Test suite
└── docs/               # Documentation
```

## Development

### Running Tests

```bash
pytest tests/
```

### Development Server

```bash
resume-llm serve --reload
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Roadmap

- [x] Resume ingestion and JSON Resume conversion
- [x] User management and configuration storage
- [x] Resume version control
- [x] LangGraph-based AI agent for resume optimization
- [x] PDF export functionality
- [x] Multiple LLM provider support (OpenAI, Gemini)
- [ ] Web interface (React/Vue.js frontend)
- [ ] Advanced PDF templates and styling
- [ ] Resume analytics and improvement tracking
- [ ] Integration with job boards (LinkedIn, Indeed)
- [ ] Resume scoring and ATS optimization
- [ ] Cover letter generation
- [ ] Interview preparation assistance

## Documentation

- **[README.md](README.md)** - Main project documentation
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Role-based LLM configuration and usage
- **[CLI_LANGGRAPH_GUIDE.md](CLI_LANGGRAPH_GUIDE.md)** - Enhanced CLI features and context switching
- **[JSON_RESUME_VALIDATION.md](JSON_RESUME_VALIDATION.md)** - JSON Resume validation and data quality guide
- **[STATUS.md](STATUS.md)** - Project status and completed features
- **[PRECOMMIT.md](PRECOMMIT.md)** - Pre-commit configuration and development practices

## Contributing

We welcome contributions! Please see the documentation files above for detailed information about the project structure and features.

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install in development mode: `pip install -e .`
4. Run tests: `pytest tests/`
5. Check code quality: `pre-commit run --all-files`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please check the documentation files or create an issue on GitHub.

## Schema Validation and Data Quality

### JSON Resume Compliance

The system ensures strict compliance with the [JSON Resume standard](https://jsonresume.org/):

- **Automatic Schema Validation**: All resumes are validated against the official JSON Resume schema
- **Null Value Removal**: Automatically removes null values that cause schema validation errors
- **JSON Extraction**: Intelligently extracts JSON Resume data from LLM responses
- **Clean Output**: Guarantees that saved resumes contain only valid, schema-compliant data

### Validation Features

```bash
# Validate a JSON Resume file
resume-llm validate my_resume.json

# Check validation status during optimization
resume-llm optimize resume.json job_description.txt -o optimized.json
# Output: ✅ Saved resume is valid JSON Resume format!
```

The validation system:
- Checks for required fields (at minimum: `basics.name`)
- Validates data types and formats (emails, URLs, dates)
- Ensures proper ISO 8601 date formatting
- Removes null values that break schema compliance
- Provides detailed error messages for any validation issues
