"""CLI commands for interacting with role-based LLM agents."""

import asyncio
from typing import Optional

import click

from ..agents import ResumeAgent
from ..models.resume import JSONResume
from ..services.llm import llm_service


@click.group()
def agent():
    """Commands for interacting with LLM agents."""


@agent.command()
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini)")
@click.option(
    "--resume-file", "-r", type=click.Path(exists=True), help="Path to resume JSON file"
)
@click.option(
    "--job-file",
    "-j",
    type=click.Path(exists=True),
    help="Path to job description file",
)
@click.option("--company", "-c", help="Company name")
def optimize_resume(
    provider: Optional[str],
    resume_file: Optional[str],
    job_file: Optional[str],
    company: Optional[str],
):
    """Optimize a resume for a specific job using the recruiter agent."""

    async def run_optimization():
        resume_agent = ResumeAgent(provider=provider)

        if not resume_file:
            click.echo("❌ Resume file is required. Use --resume-file to specify.")
            return

        if not job_file:
            click.echo(
                "❌ Job description file is required. Use --job-file to specify."
            )
            return

        try:
            # Load resume
            with open(resume_file, "r", encoding="utf-8") as f:
                resume_data = JSONResume.model_validate_json(f.read())

            # Load job description
            with open(job_file, "r", encoding="utf-8") as f:
                job_description = f.read()

            click.echo(f"🔍 Optimizing resume for {company or 'the position'}...")
            click.echo(f"📄 Using resume: {resume_file}")
            click.echo(f"📋 Using job description: {job_file}")
            click.echo(f"🤖 Using provider: {provider or 'default'}")
            click.echo()

            result = await resume_agent.optimize_resume(
                resume_data=resume_data.model_dump(),
                job_description=job_description,
                company_name=company,
            )

            click.echo("✅ Optimization complete!")
            click.echo("=" * 50)
            click.echo(result)

        except (RuntimeError, ValueError, FileNotFoundError) as e:
            click.echo(f"❌ Error: {e}")

    asyncio.run(run_optimization())


@agent.command()
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini)")
@click.option(
    "--resume-file", "-r", type=click.Path(exists=True), help="Path to resume JSON file"
)
def analyze_resume(provider: Optional[str], resume_file: Optional[str]):
    """Analyze a resume using the recruiter agent."""

    async def run_analysis():
        resume_agent = ResumeAgent(provider=provider)

        if not resume_file:
            click.echo("❌ Resume file is required. Use --resume-file to specify.")
            return

        try:
            # Load resume
            with open(resume_file, "r", encoding="utf-8") as f:
                resume_data = JSONResume.model_validate_json(f.read())

            click.echo(f"🔍 Analyzing resume: {resume_file}")
            click.echo(f"🤖 Using provider: {provider or 'default'}")
            click.echo()

            result = await resume_agent.analyze_resume(resume_data.model_dump())

            click.echo("✅ Analysis complete!")
            click.echo("=" * 50)
            click.echo(result)

        except (RuntimeError, ValueError, FileNotFoundError) as e:
            click.echo(f"❌ Error: {e}")

    asyncio.run(run_analysis())


@agent.command()
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini)")
@click.argument("company_name")
@click.argument("role_title")
def research_company(provider: Optional[str], company_name: str, role_title: str):
    """Research a company for resume optimization."""

    async def run_research():
        resume_agent = ResumeAgent(provider=provider)

        click.echo(f"🔍 Researching {company_name} for {role_title} position...")
        click.echo(f"🤖 Using provider: {provider or 'default'}")
        click.echo()

        try:
            result = await resume_agent.research_company(company_name, role_title)

            click.echo("✅ Research complete!")
            click.echo("=" * 50)
            click.echo(result)

        except (RuntimeError, ValueError) as e:
            click.echo(f"❌ Error: {e}")

    asyncio.run(run_research())


@agent.command()
@click.option("--provider", "-p", help="LLM provider to use (openai, gemini)")
def chat(provider: Optional[str]):
    """Interactive chat with the recruiter agent."""

    async def run_chat():
        resume_agent = ResumeAgent(provider=provider)

        click.echo("💬 Starting chat with recruiter agent. Type 'quit' to exit.")
        click.echo(f"🤖 Using provider: {provider or 'default'}")
        click.echo("=" * 50)

        while True:
            try:
                user_input = click.prompt("You", type=str)

                if user_input.lower() in ["quit", "exit", "bye"]:
                    click.echo("👋 Goodbye!")
                    break

                click.echo("🤖 Thinking...")
                response = await resume_agent.chat(user_input)

                click.echo(f"Recruiter: {response}")
                click.echo("-" * 30)

            except KeyboardInterrupt:
                click.echo("\n👋 Goodbye!")
                break
            except (RuntimeError, ValueError) as e:
                click.echo(f"❌ Error: {e}")

    asyncio.run(run_chat())


@agent.command()
def list_roles():
    """List available LLM roles and their configurations."""
    click.echo("📋 Available LLM Roles:")
    click.echo("=" * 50)

    role_info = llm_service.get_role_info()

    for role_name, config in role_info.items():
        click.echo(f"\n🎭 Role: {role_name.upper()}")
        click.echo(f"   Temperature: {config['temperature']}")
        click.echo(f"   Max Tokens: {config['max_tokens'] or 'Not set'}")
        click.echo(f"   Model Preferences: {config['model_preferences']}")
        click.echo(f"   System Prompt Preview: {config['system_prompt_preview']}")


@agent.command()
def list_providers():
    """List available LLM providers."""
    click.echo("🔌 LLM Provider Status:")
    click.echo("=" * 50)

    provider_info = llm_service.get_provider_info()

    for provider_name, info in provider_info.items():
        status = "✅ Available" if info["available"] else "❌ Not Available"
        is_default = "🌟 Default" if info["is_default"] else ""

        click.echo(f"{provider_name}: {status} {is_default}")

    available_providers = llm_service.get_available_providers()
    if available_providers:
        click.echo(f"\n🎯 Recommended provider: {llm_service.get_default_provider()}")
    else:
        click.echo("\n⚠️  No providers available. Please configure your API keys.")


if __name__ == "__main__":
    agent()
