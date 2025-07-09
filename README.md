# Resume LLM

An AI-powered resume refinement tool that helps you tailor your resume for specific job applications using Large Language Models and the JSON Resume standard.

## Status

Currently, the agents are not yet well tested. Functionality is redumentary as I focus on building out the infrastructure that the agent can utilize (users, api, resume history, jobs, etc.).

## Features

- **Resume Ingestion**: Convert resumes from various formats (PDF, text, JSON Resume) into a standardized JSON format
- **AI-Powered Analysis**: Use LangGraph agents to analyze job descriptions and identify key requirements
- **Smart Optimization**: Get specific suggestions for improving your resume for each job application
- **Multiple LLM Support**: Works with OpenAI GPT models, local Ollama models, or other LangChain-compatible providers
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
- **PDF Generation**: ReportLab for professional resume PDFs
- **Database**: SQLite for simplicity and portability

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
from resume_llm.agents.resume_agent import ResumeAgent

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
- `OLLAMA_BASE_URL`: Ollama server URL for local models (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Default Ollama model (default: `llama2`)

### LLM Providers

The system supports multiple LLM providers:

1. **OpenAI**: Set `OPENAI_API_KEY` environment variable
2. **Ollama (Local)**: Install and run [Ollama](https://ollama.ai/) locally
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
- [x] Multiple LLM provider support (OpenAI, Ollama)
- [ ] Web interface (React/Vue.js frontend)
- [ ] Advanced PDF templates and styling
- [ ] Resume analytics and improvement tracking
- [ ] Integration with job boards (LinkedIn, Indeed)
- [ ] Resume scoring and ATS optimization
- [ ] Cover letter generation
- [ ] Interview preparation assistance

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [JSON Resume](https://jsonresume.org/) for the resume schema standard
- [LangChain](https://langchain.com/) for the LLM framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) for agent workflow orchestration
- The open source community for inspiration and tools

---

**Note**: This tool is designed to assist with resume optimization, but human review and customization are always recommended for the best results.
