# Resume LLM - Role-Based LLM Configuration

This setup provides a structured approach to using Large Language Models with specific roles and behaviors for resume optimization.

## Overview

The system now supports role-based LLM interactions with pre-configured prompts and behaviors:

- **Recruiter Agent**: Acts as a professional tech recruiter
- **Resume Optimizer**: Focuses on ATS optimization and formatting
- **Career Advisor**: Provides strategic career guidance
- **General Assistant**: Handles basic application help

## Quick Start

1. **Configure your API keys** in `.env`:
```bash
# Choose one or more providers
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
ANTHROPIC_API_KEY=your-anthropic-key
```

2. **Check available providers**:
```bash
resume-llm agent list-providers
```

3. **See available roles**:
```bash
resume-llm agent list-roles
```

## Using the Recruiter Agent

The recruiter agent implements your system prompt and provides professional resume feedback.

### Analyze a Resume
```bash
resume-llm agent analyze-resume --resume-file path/to/resume.json --provider openai
```

### Optimize for a Job
```bash
resume-llm agent optimize-resume \
  --resume-file path/to/resume.json \
  --job-file path/to/job_description.txt \
  --company "Google" \
  --provider openai
```

### Research a Company
```bash
resume-llm agent research-company "Microsoft" "Data Scientist"
```

### Interactive Chat
```bash
resume-llm agent chat --provider openai
```

## Programming Interface

### Basic Usage
```python
from resume_llm.agents import ResumeAgent
from resume_llm.models.resume import JSONResume

# Create resume agent
agent = ResumeAgent(provider="openai")

# Load resume data
with open("resume.json") as f:
    resume = JSONResume.model_validate_json(f.read())

# Get analysis
analysis = await agent.analyze_resume(resume)
print(analysis)
```

### Direct LLM Service Usage
```python
from resume_llm.services.llm import llm_service
from resume_llm.config.llm_prompts import LLMRole

# Generate response with recruiter role
response = await llm_service.generate_role_based_response(
    role=LLMRole.RECRUITER,
    user_message="Please analyze this resume...",
    provider="openai"
)
```

### Custom Role Configuration
```python
from resume_llm.config.llm_prompts import LLMRole, LLMPromptConfig

# Get role configuration
config = LLMPromptConfig.get_model_config(LLMRole.RECRUITER, "openai")
print(f"Temperature: {config['temperature']}")
print(f"Model: {config['model']}")
```

## File Structure

```
src/resume_llm/
├── config/
│   └── llm_prompts.py          # Role definitions and system prompts
├── agents/
│   └── main_agent.py           # Unified resume agent
├── services/
│   └── llm.py                  # Enhanced LLM service with role support
└── cli/
    └── agents.py               # CLI commands for agents
```

## API Integration

The role-based system can be integrated into your FastAPI routes:

```python
from fastapi import APIRouter
from resume_llm.agents import ResumeAgent

router = APIRouter()

@router.post("/analyze-resume")
async def analyze_resume(resume_data: JSONResume, provider: str = "openai"):
    agent = ResumeAgent(provider=provider)
    return await agent.analyze_resume(resume_data)
```

## Configuration Options

### Role-Specific Settings
Each role has its own configuration:
- **System Prompt**: Role-specific instructions and behavior
- **Temperature**: Creativity level (0.0-2.0)
- **Model Preferences**: Preferred models per provider
- **Max Tokens**: Optional token limits

### Provider Selection
- Automatic fallback to available providers
- Role-specific model preferences
- Temperature and parameter optimization per role

## Best Practices

1. **Provider Selection**: Use OpenAI for most consistent results, Gemini for cost-effectiveness
2. **Role Matching**: Use the recruiter agent for resume feedback, optimizer for ATS focus
3. **Error Handling**: Always check provider availability before making requests
4. **Rate Limiting**: Consider implementing rate limiting for production use

## Example Workflow

1. **Initial Analysis**:
   ```bash
   resume-llm agent analyze-resume --resume-file resume.json
   ```

2. **Company Research**:
   ```bash
   resume-llm agent research-company "Google" "Software Engineer"
   ```

3. **Job-Specific Optimization**:
   ```bash
   resume-llm agent optimize-resume \
     --resume-file resume.json \
     --job-file google_job.txt \
     --company "Google"
   ```

4. **Interactive Refinement**:
   ```bash
   resume-llm agent chat
   ```

This setup provides a clear, structured approach to using LLMs with specific roles and behaviors, making it easy to get consistent, professional results for resume optimization tasks.
