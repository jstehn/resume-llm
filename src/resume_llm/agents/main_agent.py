"""Unified Resume Recruiter Agent using LangGraph and LangChain."""

import json
from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from ..config.llm_prompts import LLMPromptConfig, LLMRole
from ..services.llm import llm_service


class ResumeAgentState(TypedDict):
    """State for the Resume Recruiter Agent."""

    messages: Annotated[List[BaseMessage], add_messages]
    current_resume: Optional[str]
    job_description: Optional[str]
    company_name: Optional[str]
    session_context: Dict[str, Any]


# Define tools for the agent
@tool
def analyze_resume_tool(resume_json: str) -> str:
    """Analyze a resume and provide recruiter feedback.

    Args:
        resume_json: JSON string representation of the resume data
    """
    return f"""
I need to analyze this resume from a recruiter's perspective:

{resume_json}

Please provide constructive feedback on:
1. Overall impression and readability
2. Content relevance for tech/data roles
3. Areas for improvement
4. Strengths to highlight
5. Specific recommendations for optimization
"""


@tool
def optimize_resume_tool(
    resume_json: str, job_description: str, company_name: str = "Not specified"
) -> str:
    """Optimize a resume for a specific job posting.

    Args:
        resume_json: JSON string representation of the resume data
        job_description: The job description to optimize for
        company_name: Name of the target company
    """
    return f"""
I need to optimize this resume for a specific job opportunity:

**Job Description:**
{job_description}

**Company:** {company_name}

**Current Resume:**
{resume_json}

Please provide:
1. Analysis of job requirements vs. current resume
2. Specific suggestions for optimization
3. A tailored resume in JSON Resume format
4. Explanation of changes made and why
5. Any missing skills or experiences I should ask the candidate about

Follow your resume building process and technical requirements.
"""


@tool
def research_company_tool(company_name: str, role_title: str) -> str:
    """Research a company and provide insights for resume optimization.

    Args:
        company_name: Name of the company to research
        role_title: The role/position title
    """
    return f"""
I need to research {company_name} for a {role_title} position. Please provide:

1. Company overview and culture
2. Known values and mission
3. Technical stack and tools they likely use
4. Hiring process insights if available
5. Key points to emphasize in a resume for this company
6. Any specific keywords or skills they prioritize

This information will help me tailor a resume and cover letter for this opportunity.
"""


@tool
def generate_session_notes_tool(
    session_name: str,
    company_name: str,
    role_title: str,
    key_focus_areas: str,
    questions_and_responses: str,
) -> str:
    """Generate session notes in the specified format.

    Args:
        session_name: Name of the session
        company_name: Target company name
        role_title: Target role title
        key_focus_areas: Bullet-pointed list of focus areas
        questions_and_responses: Q&A formatted text
    """
    current_date = datetime.now().strftime("%Y-%m-%d")

    return f"""
Please format these session notes according to the standard template:

Session: {session_name}
Date: {current_date}
Company: {company_name}
Role: {role_title}

Key Focus Areas:
{key_focus_areas}

Questions and Responses:
{questions_and_responses}

Please format this as session notes using the template format you know.
"""


@tool
def provide_career_advice_tool(question: str, context: str = "") -> str:
    """Provide career advice as a tech recruiter.

    Args:
        question: The career advice question
        context: Additional context about the person's situation
    """
    advice_prompt = f"Career advice question: {question}\n\n"
    if context:
        advice_prompt += f"Context: {context}\n\n"

    advice_prompt += """
Please provide professional career advice from a tech recruiter's perspective.
Consider market trends, industry best practices, and practical next steps.
"""
    return advice_prompt


class ResumeAgent:
    """Unified Resume Recruiter Agent using LangGraph."""

    def __init__(self, provider: Optional[str] = None):
        """Initialize the agent with optional provider preference."""
        self.provider = provider
        self.tools = [
            analyze_resume_tool,
            optimize_resume_tool,
            research_company_tool,
            generate_session_notes_tool,
            provide_career_advice_tool,
        ]

        # Create the LangGraph workflow
        self.workflow = self._create_workflow()

        # Track conversation history
        self.conversation_history: List[BaseMessage] = []

    def _create_workflow(self):
        """Create the LangGraph workflow."""
        # Initialize the graph
        workflow = StateGraph(ResumeAgentState)

        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(self.tools))

        # Set entry point
        workflow.set_entry_point("agent")

        # Add edges
        workflow.add_conditional_edges(
            "agent", self._should_continue, {"continue": "tools", "end": END}
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    async def _agent_node(self, state: ResumeAgentState) -> ResumeAgentState:
        """Process the agent node."""
        messages = state["messages"]

        # Get the configured model
        model = llm_service.get_model(provider=self.provider, role=LLMRole.RECRUITER)

        # Use hasattr to check if model supports tool binding
        if hasattr(model, "bind_tools"):
            try:
                # Try to bind tools but suppress type errors for now
                model_with_tools = getattr(model, "bind_tools")(self.tools)
            except (AttributeError, NotImplementedError, TypeError):
                # Fallback if binding fails
                model_with_tools = model
        else:
            # Model doesn't support tool binding
            model_with_tools = model

        # Add system message if needed
        if not messages or not isinstance(messages[0], SystemMessage):
            system_prompt = LLMPromptConfig.get_system_prompt(LLMRole.RECRUITER)
            messages = [SystemMessage(content=system_prompt)] + messages

        # Generate response
        response = await model_with_tools.ainvoke(messages)

        # Update state
        return {
            "messages": [response],
            "current_resume": state.get("current_resume"),
            "job_description": state.get("job_description"),
            "company_name": state.get("company_name"),
            "session_context": state.get("session_context", {}),
        }

    def _should_continue(self, state: ResumeAgentState) -> Literal["continue", "end"]:
        """Determine if the agent should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # Check if the last message contains tool calls (for models that support it)
        if hasattr(last_message, "tool_calls") and getattr(
            last_message, "tool_calls", None
        ):
            return "continue"

        # Check if message content suggests tool usage
        if hasattr(last_message, "content") and last_message.content:
            content = last_message.content
            # Handle different content types
            if isinstance(content, str):
                content_str = content.lower()
            elif isinstance(content, list):
                content_str = str(content).lower()
            else:
                content_str = str(content).lower()

            tool_indicators = [
                "analyze_resume_tool",
                "optimize_resume_tool",
                "research_company_tool",
                "generate_session_notes_tool",
                "provide_career_advice_tool",
            ]
            if any(indicator in content_str for indicator in tool_indicators):
                return "continue"

        return "end"

    async def chat(self, message: str, **context) -> str:
        """Chat with the agent."""
        # Create initial state
        initial_state: ResumeAgentState = {
            "messages": [HumanMessage(content=message)],
            "current_resume": context.get("current_resume"),
            "job_description": context.get("job_description"),
            "company_name": context.get("company_name"),
            "session_context": context.get("session_context", {}),
        }

        # Add conversation history
        if self.conversation_history:
            initial_state["messages"] = (
                self.conversation_history + initial_state["messages"]
            )

        # Run the workflow
        result = await self.workflow.ainvoke(initial_state)

        # Extract response
        response_message = result["messages"][-1]
        response_content = response_message.content

        # Update conversation history
        self.conversation_history.extend(
            [HumanMessage(content=message), response_message]
        )

        # Keep conversation history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        return response_content

    async def analyze_resume(self, resume_data: Dict[str, Any]) -> str:
        """Analyze a resume using the agent."""
        resume_json = json.dumps(resume_data, indent=2)
        message = f"Please analyze this resume: {resume_json}"

        return await self.chat(message)

    async def optimize_resume(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        company_name: Optional[str] = None,
    ) -> str:
        """Optimize a resume for a specific job."""
        # Create a more focused message instead of adding everything to system prompt
        resume_json = json.dumps(resume_data, indent=2)

        message = f"""I need to optimize a resume for a specific job opportunity.

**Job Description:**
{job_description}

**Company:** {company_name or "Not specified"}

**Current Resume:**
{resume_json}

Please analyze the job requirements and provide specific suggestions for optimizing this resume to match the position. Focus on:
1. Key skills and experiences to highlight
2. Relevant keywords to include
3. Specific improvements to make each section more compelling
4. Any gaps that should be addressed

Then provide an optimized version of the resume in JSON Resume format."""

        context = {
            "current_resume": resume_json,
            "job_description": job_description,
            "company_name": company_name or "Not specified",
        }

        return await self.chat(message, **context)

    async def research_company(self, company_name: str, role_title: str) -> str:
        """Research a company for resume optimization."""
        message = f"Please research {company_name} for a {role_title} position."
        context = {"company_name": company_name}

        return await self.chat(message, **context)

    async def generate_session_notes(self, session_data: Dict[str, Any]) -> str:
        """Generate session notes."""
        message = (
            f"Please generate session notes for: {json.dumps(session_data, indent=2)}"
        )

        return await self.chat(message)

    async def provide_career_advice(
        self, question: str, context: Optional[str] = None
    ) -> str:
        """Provide career advice."""
        message = f"Career advice question: {question}"
        if context:
            message += f"\n\nContext: {context}"

        return await self.chat(message)

    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
