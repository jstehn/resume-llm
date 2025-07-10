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
from ..utils.json_extractor import save_json_resume_from_response
from ..utils.json_resume_validator import json_resume_validator
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
@click.option("--company", "-c", help="Company name for context")
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Start interactive mode after optimization",
)
def optimize(
    resume_file: Path,
    job_description_file: Path,
    output: Optional[Path],
    provider: Optional[str],
    company: Optional[str],
    interactive: bool,
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
            resume_agent = ResumeAgent(provider=provider)

            # Convert JSONResume to dict for the agent
            resume_data = resume.model_dump(mode="json")

            # Use the optimize method with context
            result = await resume_agent.optimize_resume(
                resume_data=resume_data,
                job_description=job_description,
                company_name=company,
            )

            # Display results
            click.echo("\n📊 Optimization Results:")
            click.echo(result)

            # Save output if specified
            if output:
                try:
                    # Try to extract JSON Resume from the response
                    if save_json_resume_from_response(result, str(output)):
                        click.echo(f"\n💾 JSON Resume saved to {output}")

                        # Validate the saved resume
                        is_valid, errors = json_resume_validator.validate_resume_string(
                            open(output, "r", encoding="utf-8").read()
                        )
                        if is_valid:
                            click.echo("✅ Saved resume is valid JSON Resume format!")
                        else:
                            click.echo("⚠️  Saved resume has validation issues:")
                            for error in errors[:3]:  # Show first 3 errors
                                click.echo(f"   • {error}")
                    else:
                        # Fallback: save the full response
                        with open(output, "w", encoding="utf-8") as f:
                            f.write(result)
                        click.echo(f"\n💾 Full response saved to {output}")
                        click.echo("⚠️  Could not extract JSON Resume from response")
                except (OSError, IOError) as e:
                    click.echo(f"❌ Error saving output: {e}")

            # Start interactive mode if requested
            if interactive:
                click.echo("\n🔄 Starting interactive mode...")
                click.echo(
                    "You can now continue the conversation about this resume optimization."
                )
                click.echo("Type 'quit' or 'exit' to end the session.")
                click.echo("-" * 50)

                # Set up context for interactive mode
                # Use json.dumps directly since resume_data is already serialized from model_dump(mode='json')
                context = {
                    "current_resume": json.dumps(resume_data, indent=2),
                    "job_description": job_description,
                    "company_name": company,
                }

                try:
                    while True:
                        try:
                            user_input = input("\n💬 You: ").strip()

                            if user_input.lower() in ["quit", "exit"]:
                                click.echo("👋 Goodbye!")
                                break

                            if not user_input:
                                continue

                            click.echo("🤖 Agent: ", nl=False)
                            response = await resume_agent.chat(user_input, **context)
                            click.echo(response)

                        except KeyboardInterrupt:
                            click.echo("\n👋 Goodbye!")
                            break
                        except EOFError:
                            click.echo("\n👋 Goodbye!")
                            break
                        except Exception as e:
                            click.echo(f"\n❌ Error: {e}")
                            continue

                except Exception as e:
                    click.echo(f"❌ Error in interactive mode: {e}")

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
            resume_json = f.read()

        # Validate against JSON Resume schema
        is_valid, errors = json_resume_validator.validate_resume_string(resume_json)

        if is_valid:
            click.echo("✅ Resume is valid JSON Resume format!")

            # Show basic info
            resume_data = json.loads(resume_json)
            if "basics" in resume_data:
                basics = resume_data["basics"]
                click.echo(f"   Name: {basics.get('name', 'N/A')}")
                click.echo(f"   Email: {basics.get('email', 'N/A')}")

            click.echo(f"   Work experiences: {len(resume_data.get('work', []))}")
            click.echo(f"   Skills: {len(resume_data.get('skills', []))}")
            click.echo(f"   Education: {len(resume_data.get('education', []))}")
        else:
            click.echo("❌ Resume validation failed:")
            for error in errors:
                click.echo(f"   • {error}")

    except Exception as e:
        click.echo(f"❌ Error validating resume: {e}")
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


@main.command()
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini, etc.)")
@click.option(
    "--resume-file",
    "-r",
    type=click.Path(exists=True, path_type=Path),
    help="Resume file to load into context",
)
@click.option(
    "--job-file",
    "-j",
    type=click.Path(exists=True, path_type=Path),
    help="Job description file to load into context",
)
@click.option("--company", "-c", help="Company name to include in context")
def chat(
    provider: Optional[str],
    resume_file: Optional[Path],
    job_file: Optional[Path],
    company: Optional[str],
):
    """Start an interactive chat session with the Resume Agent."""

    async def run_chat():
        # Initialize the agent with context
        resume_agent = ResumeAgent(provider=provider)

        # Load context if files are provided
        context = {}
        if resume_file:
            try:
                with open(resume_file, "r", encoding="utf-8") as f:
                    resume_data = json.load(f)
                context["current_resume"] = json.dumps(resume_data, indent=2)
                click.echo(f"📄 Loaded resume from {resume_file}")
            except Exception as e:
                click.echo(f"❌ Error loading resume: {e}")
                return

        if job_file:
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    job_description = f.read()
                context["job_description"] = job_description
                click.echo(f"💼 Loaded job description from {job_file}")
            except Exception as e:
                click.echo(f"❌ Error loading job description: {e}")
                return

        if company:
            context["company_name"] = company
            click.echo(f"🏢 Company context set to: {company}")

        # Welcome message
        click.echo("\n🤖 Resume Agent Chat Session")
        click.echo(
            "Type your messages below. Use 'quit', 'exit', or Ctrl+C to end the session."
        )
        click.echo("Commands:")
        click.echo("  /clear - Clear conversation history")
        click.echo("  /context - Show current context")
        click.echo("  /help - Show this help message")
        click.echo("-" * 50)

        try:
            while True:
                try:
                    # Get user input
                    user_input = input("\n💬 You: ").strip()

                    # Handle special commands
                    if user_input.lower() in ["quit", "exit"]:
                        click.echo("👋 Goodbye!")
                        break

                    if user_input == "/clear":
                        resume_agent.clear_conversation_history()
                        click.echo("🧹 Conversation history cleared.")
                        continue

                    if user_input == "/context":
                        click.echo("📋 Current context:")
                        for key, value in context.items():
                            if key == "current_resume":
                                click.echo(
                                    f"  📄 Resume: {len(value)} characters loaded"
                                )
                            elif key == "job_description":
                                click.echo(
                                    f"  💼 Job description: {len(value)} characters loaded"
                                )
                            else:
                                click.echo(f"  {key}: {value}")
                        continue

                    if user_input == "/help":
                        click.echo("Commands:")
                        click.echo("  /clear - Clear conversation history")
                        click.echo("  /context - Show current context")
                        click.echo("  /help - Show this help message")
                        click.echo("  quit/exit - End the session")
                        continue

                    if not user_input:
                        continue

                    # Send message to agent with context
                    click.echo("🤖 Agent: ", nl=False)
                    response = await resume_agent.chat(user_input, **context)
                    click.echo(response)

                except KeyboardInterrupt:
                    click.echo("\n👋 Goodbye!")
                    break
                except EOFError:
                    click.echo("\n👋 Goodbye!")
                    break
                except Exception as e:
                    click.echo(f"\n❌ Error: {e}")
                    continue

        except Exception as e:
            click.echo(f"❌ Error in chat session: {e}")

    # Run the async chat session
    asyncio.run(run_chat())


@main.command()
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini, etc.)")
@click.option(
    "--resume-file",
    "-r",
    type=click.Path(exists=True, path_type=Path),
    help="Resume file to analyze",
)
def analyze(provider: Optional[str], resume_file: Optional[Path]):
    """Analyze a resume with the Resume Agent."""

    if not resume_file:
        click.echo("❌ Resume file is required. Use --resume-file to specify.")
        return

    async def run_analysis():
        try:
            # Load resume
            with open(resume_file, "r", encoding="utf-8") as f:
                resume_data = json.load(f)

            # Initialize agent
            resume_agent = ResumeAgent(provider=provider)

            # Analyze resume
            click.echo("🔍 Analyzing resume...")
            result = await resume_agent.analyze_resume(resume_data)

            # Display results
            click.echo("\n📊 Analysis Results:")
            click.echo(result)

        except Exception as e:
            click.echo(f"❌ Error during analysis: {e}")
            raise e

    # Run the async analysis
    asyncio.run(run_analysis())


@main.command()
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini, etc.)")
@click.argument("question", required=True)
def advice(provider: Optional[str], question: str):
    """Get career advice from the Resume Agent."""

    async def run_advice():
        try:
            # Initialize agent
            resume_agent = ResumeAgent(provider=provider)

            # Get advice
            click.echo("🤔 Getting career advice...")
            result = await resume_agent.provide_career_advice(question)

            # Display results
            click.echo("\n💡 Career Advice:")
            click.echo(result)

        except Exception as e:
            click.echo(f"❌ Error getting advice: {e}")
            raise e

    # Run the async advice
    asyncio.run(run_advice())


# Add agent subcommands
main.add_command(agent)


if __name__ == "__main__":
    main()
