# Enhanced CLI for LangGraph Context Switching

The Resume LLM CLI now provides enhanced support for LangGraph's context switching capabilities. Here's how to use the new features:

## Interactive Chat Mode

Start an interactive chat session with persistent context:

```bash
# Basic chat
resume-llm chat

# Chat with resume context
resume-llm chat -r path/to/resume.json

# Chat with full context
resume-llm chat -r path/to/resume.json -j path/to/job.txt -c "Company Name"
```

### Chat Commands

During the chat session, you can use these commands:
- `/clear` - Clear conversation history
- `/context` - Show current context
- `/help` - Show help message
- `quit` or `exit` - End the session

## Enhanced Optimization

The optimize command now supports interactive mode and better context management:

```bash
# Basic optimization
resume-llm optimize resume.json job.txt

# Optimization with company context
resume-llm optimize resume.json job.txt -c "Google"

# Optimization with interactive follow-up
resume-llm optimize resume.json job.txt -c "Google" -i

# Save results to file
resume-llm optimize resume.json job.txt -o optimized_resume.txt
```

## Quick Analysis and Advice

Get focused responses without full optimization:

```bash
# Analyze a resume
resume-llm analyze -r resume.json

# Get career advice
resume-llm advice "How can I transition from backend to full-stack development?"
```

## LangGraph Features

The enhanced CLI takes advantage of LangGraph's capabilities:

1. **Persistent Context**: Conversation history is maintained within a session
2. **Context Switching**: Can switch between different types of queries while maintaining context
3. **Tool Integration**: Automatically uses the appropriate tools based on your queries
4. **State Management**: Manages resume, job description, and company context throughout the conversation

## Data Quality and Validation

### JSON Resume Validation

The CLI now includes comprehensive validation for JSON Resume compliance:

```bash
# Validate a JSON Resume file
resume-llm validate my_resume.json

# Validate with detailed output
resume-llm validate my_resume.json --verbose

# Validate multiple files
resume-llm validate resume1.json resume2.json
```

### Automatic Validation During Optimization

All optimization commands now include automatic validation:

```bash
# Optimization with automatic validation
resume-llm optimize resume.json job.txt -o optimized.json
# Output includes: ✅ Saved resume is valid JSON Resume format!
```

### Validation Features

- **Schema Compliance**: Validates against official JSON Resume schema
- **Null Value Removal**: Automatically removes null values from optimized resumes
- **JSON Extraction**: Intelligently extracts JSON Resume from LLM responses
- **Error Reporting**: Detailed validation messages with field paths
- **Clean Output**: Guarantees schema-compliant resume files

## Example Workflow

```bash
# Start with resume and job context
resume-llm chat -r my_resume.json -j job_posting.txt -c "TechCorp"

# In the chat session:
# 1. "Please analyze my resume for this job"
# 2. "What specific skills should I highlight?"
# 3. "Can you optimize my work experience section?"
# 4. "How should I tailor my summary?"
# 5. "/clear" (to start fresh while keeping context)
# 6. "Generate a cover letter for this position"
```

This workflow demonstrates how LangGraph maintains context across different types of requests while allowing you to build on previous conversations.
