import json
from typing import Any, TypedDict

from jsonschema import ValidationError
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import END, START, StateGraph

from resume_llm.utils.jsonresume_validator import validate_resume

SYSTEM_PROMPT = """\
You are an expert resume editor. You tailor a candidate's resume to a specific
job description. The resume is in the JSON Resume format (https://jsonresume.org).

Rules:
- Use only facts from the original resume. Never invent employers, titles, dates,
  degrees, metrics, or skills the candidate did not list.
- Lead with the experience, projects, and skills most relevant to the job.
  Reorder entries and highlights so the strongest matches come first.
- Drop or shorten content that is irrelevant to the job, so the resume stays tight.
- Rephrase the summary and highlights to use the job description's vocabulary,
  but only where it truthfully describes what the candidate did.
- Keep the "basics" contact details unchanged.
- Keep dates in the original ISO 8601 format (YYYY, YYYY-MM, or YYYY-MM-DD).

Respond with only the tailored resume as a single JSON object that conforms to
the JSON Resume schema. No commentary and no Markdown.
"""


class TailoringError(Exception):
    """Raised when the LLM fails to produce a valid tailored resume."""


class TailorState(TypedDict):
    resume: dict[str, Any]
    job_description: str
    tailored: dict[str, Any] | None
    error: str | None
    attempts: int


def build_agent(llm: BaseChatModel, max_attempts: int = 2):
    """
    Builds a LangGraph agent that tailors a JSON resume to a job description.
    Args:
        llm (BaseChatModel): Chat model from resume_llm.llms.get_llm.
        max_attempts (int): LLM calls allowed before giving up on invalid output.
    Returns:
        Compiled LangGraph graph that takes and returns a TailorState.
    """
    parser = JsonOutputParser()

    def tailor(state: TailorState) -> dict[str, Any]:
        prompt = (
            f"Job description:\n{state['job_description']}\n\n"
            f"Original resume:\n{json.dumps(state['resume'], indent=2)}"
        )
        if state["error"]:
            prompt += (
                f"\n\nYour previous answer was rejected: {state['error']}\n"
                "Return the full corrected resume."
            )
        response = llm.invoke([SystemMessage(SYSTEM_PROMPT), HumanMessage(prompt)])
        attempts = state["attempts"] + 1
        try:
            tailored = parser.parse(str(response.content))
        except OutputParserException as e:
            return {
                "tailored": None,
                "error": f"invalid JSON: {e}",
                "attempts": attempts,
            }
        if not isinstance(tailored, dict):
            return {
                "tailored": None,
                "error": "expected a JSON object",
                "attempts": attempts,
            }
        return {"tailored": tailored, "error": None, "attempts": attempts}

    def validate(state: TailorState) -> dict[str, Any]:
        if state["tailored"] is None:
            return {}
        try:
            validate_resume(state["tailored"])
        except ValidationError as e:
            path = "/".join(str(p) for p in e.absolute_path) or "<root>"
            return {"error": f"schema violation at {path}: {e.message}"}
        return {"error": None}

    def route(state: TailorState) -> str:
        if state["error"] and state["attempts"] < max_attempts:
            return "tailor"
        return END

    graph = StateGraph(TailorState)
    graph.add_node("tailor", tailor)
    graph.add_node("validate", validate)
    graph.add_edge(START, "tailor")
    graph.add_edge("tailor", "validate")
    graph.add_conditional_edges("validate", route, ["tailor", END])
    return graph.compile()


def tailor_resume(
    llm: BaseChatModel,
    resume: dict[str, Any],
    job_description: str,
    max_attempts: int = 2,
) -> dict[str, Any]:
    """
    Tailors a JSON resume to a job description.
    Args:
        llm (BaseChatModel): Chat model from resume_llm.llms.get_llm.
        resume (dict): The original JSON resume.
        job_description (str): The job posting text.
        max_attempts (int): LLM calls allowed before giving up on invalid output.
    Returns:
        dict: The tailored resume, valid against the JSON Resume schema.
    Raises:
        TailoringError: If no valid resume was produced within max_attempts.
    """
    agent = build_agent(llm, max_attempts)
    state = agent.invoke(
        {
            "resume": resume,
            "job_description": job_description,
            "tailored": None,
            "error": None,
            "attempts": 0,
        }
    )
    if state["error"] or state["tailored"] is None:
        raise TailoringError(
            f"No valid resume after {state['attempts']} attempt(s): {state['error']}"
        )
    return state["tailored"]
