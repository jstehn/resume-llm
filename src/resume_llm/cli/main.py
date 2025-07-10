"""Main CLI entry point for Resume LLM."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import click
import uvicorn

from ..agents import ResumeAgent
from ..api.main import app
from ..database.connection import init_db
from ..models.resume import JSONResume
from ..services.llm import llm_service
from .agents import agent


@click.group()
@click.version_option()
def main():
    """Resume LLM - AI-powered resume refinement tool."""
    # Initialize database on startup
    init_db()


@main.command()
def init():
    """Initialize the Resume LLM database and configuration."""
    click.echo("Initializing Resume LLM...")

    try:
        init_db()
        click.echo("✅ Database initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Error initializing database: {e}")
        raise

    # Check LLM providers
    click.echo("\nChecking LLM providers...")
    provider_list = llm_service.get_provider_info()

    for name, info in provider_list.items():
        status = "✅ Available" if info["available"] else "❌ Not available"
        default = " (default)" if info["is_default"] else ""
        click.echo(f"  {name}: {status}{default}")

    if not llm_service.get_available_providers():
        click.echo("\n⚠️  Warning: No LLM providers are available.")
        click.echo("Please configure an API key.")

    click.echo("\n🎉 Resume LLM is ready to use!")


@main.command()
@click.argument("resume_file", type=click.Path(exists=True, path_type=Path))
@click.argument("job_description_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file for optimized resume",
)
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini, etc.)")
def optimize(
    resume_file: Path,
    job_description_file: Path,
    output: Optional[Path],
):
    """Optimize a resume for a specific job description."""
    _ = output  # Acknowledge unused parameter for now
    click.echo("🔍 Analyzing resume and job description...")

    try:
        # Load resume
        with open(resume_file, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        resume = JSONResume(**resume_data)

        # Load job description
        with open(job_description_file, "r", encoding="utf-8") as f:
            job_description = f.read()

    except Exception as e:
        click.echo(f"❌ Error loading files: {e}")
        raise

    # Run optimization
    async def run_optimization():
        try:
            resume_agent = ResumeAgent()

            # Convert JSONResume to dict for the agent
            resume_data = resume.model_dump()

            # Use the optimize method
            result = await resume_agent.optimize_resume(
                resume_data=resume_data,
                job_description=job_description,
                company_name=None,  # Add company name option if needed
            )

            # Display results
            click.echo("\n📊 Optimization Results:")
            click.echo(result)

        except Exception as e:
            click.echo(f"❌ Error during optimization: {e}")
            raise e

    # Run the async function
    asyncio.run(run_optimization())


@main.command()
def providers():
    """List available LLM providers and their status."""
    click.echo("🤖 Available LLM Providers:")

    providers_list = llm_service.get_provider_info()

    for name, info in providers_list.items():
        status = "✅ Available" if info["available"] else "❌ Not available"
        default = " (default)" if info["is_default"] else ""
        click.echo(f"  {name}: {status}{default}")

    if not llm_service.get_available_providers():
        click.echo("\n⚠️  No providers are currently available.")
        click.echo("To set up providers:")
        click.echo("  • OpenAI: Set OPENAI_API_KEY environment variable")
        click.echo("  • Google Gemini: Set GOOGLE_API_KEY environment variable")
        click.echo("  • Anthropic Claude: Set ANTHROPIC_API_KEY environment variable")


@main.command()
@click.argument("resume_file", type=click.Path(exists=True, path_type=Path))
def validate(resume_file: Path):
    """Validate a JSON Resume file."""
    click.echo(f"🔍 Validating {resume_file}...")

    try:
        with open(resume_file, "r", encoding="utf-8") as f:
            resume_data = json.load(f)

        resume = JSONResume(**resume_data)

        click.echo("✅ Resume is valid!")
        click.echo(f"   Name: {resume.basics.name}")
        click.echo(f"   Email: {resume.basics.email}")
        click.echo(f"   Work experiences: {len(resume.work or [])}")
        click.echo(f"   Skills: {len(resume.skills or [])}")
        click.echo(f"   Education: {len(resume.education or [])}")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}")
    except Exception as e:
        click.echo(f"❌ Invalid resume format: {e}")
        raise e


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=8000, help="Port to bind the server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host: str, port: int, reload: bool):
    """Start the Resume LLM API server."""
    click.echo(f"🚀 Starting Resume LLM API server on {host}:{port}")

    try:
        uvicorn.run(app, host=host, port=port, reload=reload)
    except ImportError:
        click.echo(
            "❌ API dependencies not available. Install with: pip install 'resume-llm[api]'"
        )
    except Exception as e:
        click.echo(f"❌ Error starting server: {e}")
        raise e


# Add agent subcommands
main.add_command(agent)


if __name__ == "__main__":
    main()
