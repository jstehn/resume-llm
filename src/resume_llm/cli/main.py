"""Main CLI entry point for Resume LLM."""

import click
import asyncio
import json
from pathlib import Path
from typing import Optional

from ..database.connection import init_db
from ..services.llm import llm_service
from ..agents.resume_agent import ResumeAgent
from ..models.resume import JSONResume


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
        return
    
    # Check LLM providers
    click.echo("\nChecking LLM providers...")
    providers = llm_service.get_provider_info()
    
    for name, info in providers.items():
        status = "✅ Available" if info["available"] else "❌ Not available"
        default = " (default)" if info["is_default"] else ""
        click.echo(f"  {name}: {status}{default}")
    
    if not llm_service.get_available_providers():
        click.echo("\n⚠️  Warning: No LLM providers are available.")
        click.echo("Please configure an API key or set up Ollama for local models.")
    
    click.echo("\n🎉 Resume LLM is ready to use!")


@main.command()
@click.argument("resume_file", type=click.Path(exists=True, path_type=Path))
@click.argument("job_description_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for optimized resume")
@click.option("--provider", "-p", help="LLM provider to use (openai, ollama)")
def optimize(
    resume_file: Path,
    job_description_file: Path,
    output: Optional[Path],
    provider: Optional[str]
):
    """Optimize a resume for a specific job description."""
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
        return
    
    # Run optimization
    async def run_optimization():
        try:
            agent = ResumeAgent()
            result = await agent.run(resume, job_description)
            
            # Display results
            click.echo("\n📊 Analysis Results:")
            analysis = result.get("analysis_results", {})
            
            if "suggestions" in analysis:
                suggestions = analysis["suggestions"]
                if isinstance(suggestions, dict) and "raw_suggestions" not in suggestions:
                    click.echo("💡 Suggestions:")
                    for key, value in suggestions.items():
                        if isinstance(value, list):
                            click.echo(f"  {key}:")
                            for item in value:
                                click.echo(f"    • {item}")
                        else:
                            click.echo(f"  {key}: {value}")
                else:
                    click.echo("💡 Suggestions:")
                    click.echo(suggestions.get("raw_suggestions", "No structured suggestions available"))
            
            # Handle optimized resume
            optimized_resume = result.get("optimized_resume")
            if optimized_resume:
                output_file = output or resume_file.parent / f"{resume_file.stem}_optimized.json"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(optimized_resume.model_dump(), f, indent=2, default=str)
                
                click.echo(f"\n✅ Optimized resume saved to: {output_file}")
            else:
                click.echo("\n⚠️  Could not generate optimized resume")
            
            # Show change summary
            change_summary = result.get("change_summary")
            if change_summary:
                click.echo(f"\n📝 Summary of Changes:")
                click.echo(change_summary)
        
        except Exception as e:
            click.echo(f"❌ Error during optimization: {e}")
    
    # Run the async function
    asyncio.run(run_optimization())


@main.command()
def providers():
    """List available LLM providers and their status."""
    click.echo("🤖 Available LLM Providers:")
    
    providers = llm_service.get_provider_info()
    
    for name, info in providers.items():
        status = "✅ Available" if info["available"] else "❌ Not available"
        default = " (default)" if info["is_default"] else ""
        click.echo(f"  {name}: {status}{default}")
    
    if not llm_service.get_available_providers():
        click.echo("\n⚠️  No providers are currently available.")
        click.echo("To set up providers:")
        click.echo("  • OpenAI: Set OPENAI_API_KEY environment variable")
        click.echo("  • Ollama: Install and run Ollama locally")


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


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=8000, help="Port to bind the server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host: str, port: int, reload: bool):
    """Start the Resume LLM API server."""
    click.echo(f"🚀 Starting Resume LLM API server on {host}:{port}")
    
    try:
        import uvicorn
        from ..api.main import app
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload
        )
    except ImportError:
        click.echo("❌ API dependencies not available. Install with: pip install 'resume-llm[api]'")
    except Exception as e:
        click.echo(f"❌ Error starting server: {e}")


if __name__ == "__main__":
    main()
