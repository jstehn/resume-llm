import argparse
import json
import sys
from pathlib import Path
from typing import Any

from resume_llm.agents.agent import TailoringError, tailor_resume
from resume_llm.llms import AVAILABLE_LLMS, get_llm


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the resume-llm command.
    Args:
        argv (list[str], optional): Arguments, defaults to sys.argv[1:].
    Returns:
        int: Process exit code.
    """
    parser = argparse.ArgumentParser(
        prog="resume-llm", description="Tailor a JSON resume with an LLM."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    tailor = subparsers.add_parser(
        "tailor", help="Tailor a resume to a job description."
    )
    tailor.add_argument("resume", type=Path, help="JSON Resume file.")
    tailor.add_argument(
        "job", type=Path, help="Job description text file, or - for stdin."
    )
    tailor.add_argument(
        "-o", "--output", type=Path, help="Write the result here instead of stdout."
    )
    tailor.add_argument("--provider", choices=AVAILABLE_LLMS, default="ollama")
    tailor.add_argument("--model", help="Model name. Defaults to the provider's.")
    tailor.add_argument(
        "--max-attempts",
        type=int,
        default=2,
        help="LLM calls allowed before giving up on invalid output.",
    )
    args = parser.parse_args(argv)

    resume = json.loads(args.resume.read_text(encoding="utf-8"))
    if str(args.job) == "-":
        job_description = sys.stdin.read()
    else:
        job_description = args.job.read_text(encoding="utf-8")

    # Skip the thinking phase of reasoning models (e.g. Qwen 3); output is JSON only
    llm_kwargs: dict[str, Any] = (
        {"reasoning": False} if args.provider == "ollama" else {}
    )
    llm = get_llm(args.provider, model=args.model, **llm_kwargs)

    try:
        tailored = tailor_resume(llm, resume, job_description, args.max_attempts)
    except TailoringError as e:
        print(f"resume-llm: {e}", file=sys.stderr)
        return 1

    output = json.dumps(tailored, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
