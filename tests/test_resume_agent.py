"""Tests for the LangGraph-based Resume Agent."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from resume_llm.agents.main_agent import ResumeAgent
from resume_llm.config.settings import settings


class TestResumeAgent:
    """Test the LangGraph-based Resume Agent."""

    @pytest.fixture
    def sample_resume_data(self):
        """Sample resume data for testing."""
        return {
            "basics": {
                "name": "John Doe",
                "email": "john@example.com",
                "summary": "Software developer with 3 years experience",
            },
            "work": [
                {
                    "company": "Tech Corp",
                    "position": "Software Developer",
                    "startDate": "2021-01-01",
                    "endDate": "2024-01-01",
                    "summary": "Developed web applications",
                }
            ],
            "skills": [{"name": "Python"}, {"name": "JavaScript"}, {"name": "React"}],
        }

    @pytest.fixture
    def sample_job_description(self):
        """Sample job description for testing."""
        return """
        We are looking for a Senior Python Developer with:
        - 3+ years Python experience
        - Django/Flask frameworks
        - React frontend experience
        - AWS cloud experience
        """

    def test_agent_initialization(self):
        """Test that the agent initializes properly with LangGraph components."""
        agent = ResumeAgent()

        # Check that the agent has the required components
        assert agent.workflow is not None
        assert len(agent.tools) == 5  # Should have 5 tools defined
        assert agent.conversation_history == []

        # Check that tools are properly defined
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = [
            "analyze_resume_tool",
            "optimize_resume_tool",
            "research_company_tool",
            "generate_session_notes_tool",
            "provide_career_advice_tool",
        ]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_agent_initialization_with_provider(self):
        """Test agent initialization with specific provider."""
        agent = ResumeAgent(provider="gemini")
        assert agent.provider == "gemini"

    @pytest.mark.asyncio
    async def test_chat_functionality(self, sample_resume_data):
        """Test the basic chat functionality of the agent."""
        agent = ResumeAgent()

        # Mock the LLM response
        mock_response = AIMessage(content="This is a test response from the agent.")

        with patch.object(
            agent.workflow, "ainvoke", return_value={"messages": [mock_response]}
        ):
            response = await agent.chat("Hello, can you help me with my resume?")

            assert isinstance(response, str)
            assert response == "This is a test response from the agent."
            assert len(agent.conversation_history) == 2  # User message + AI response

    @pytest.mark.asyncio
    async def test_analyze_resume(self, sample_resume_data):
        """Test the analyze_resume method."""
        agent = ResumeAgent()

        mock_response = AIMessage(
            content="Resume analysis: Good technical skills, needs more quantified achievements."
        )

        with patch.object(
            agent.workflow, "ainvoke", return_value={"messages": [mock_response]}
        ):
            response = await agent.analyze_resume(sample_resume_data)

            assert isinstance(response, str)
            assert "Resume analysis" in response

    @pytest.mark.asyncio
    async def test_optimize_resume(self, sample_resume_data, sample_job_description):
        """Test the optimize_resume method."""
        agent = ResumeAgent()

        mock_response = AIMessage(
            content="Optimized resume suggestions: Add AWS experience, highlight Python projects."
        )

        with patch.object(
            agent.workflow, "ainvoke", return_value={"messages": [mock_response]}
        ):
            response = await agent.optimize_resume(
                sample_resume_data, sample_job_description, "Tech Company"
            )

            assert isinstance(response, str)
            assert "Optimized resume" in response

    @pytest.mark.asyncio
    async def test_research_company(self):
        """Test the research_company method."""
        agent = ResumeAgent()

        mock_response = AIMessage(
            content="Company research: Tech-focused company, values innovation and agile development."
        )

        with patch.object(
            agent.workflow, "ainvoke", return_value={"messages": [mock_response]}
        ):
            response = await agent.research_company("Google", "Software Engineer")

            assert isinstance(response, str)
            assert "Company research" in response

    @pytest.mark.asyncio
    async def test_provide_career_advice(self):
        """Test the provide_career_advice method."""
        agent = ResumeAgent()

        mock_response = AIMessage(
            content="Career advice: Focus on building a strong portfolio and networking."
        )

        with patch.object(
            agent.workflow, "ainvoke", return_value={"messages": [mock_response]}
        ):
            response = await agent.provide_career_advice(
                "How can I transition to a senior role?",
                "Currently a mid-level developer with 3 years experience",
            )

            assert isinstance(response, str)
            assert "Career advice" in response

    @pytest.mark.asyncio
    async def test_generate_session_notes(self):
        """Test the generate_session_notes method."""
        agent = ResumeAgent()

        session_data = {
            "session_name": "Resume Review Session",
            "company_name": "Tech Corp",
            "role_title": "Senior Developer",
            "key_focus_areas": "• Technical skills\n• Leadership experience",
            "questions_and_responses": "Q: Experience with Python?\nA: 3 years professional experience",
        }

        mock_response = AIMessage(content="Session notes generated successfully.")

        with patch.object(
            agent.workflow, "ainvoke", return_value={"messages": [mock_response]}
        ):
            response = await agent.generate_session_notes(session_data)

            assert isinstance(response, str)

    def test_conversation_history_management(self):
        """Test that conversation history is properly managed."""
        agent = ResumeAgent()

        # Test that history starts empty
        assert len(agent.conversation_history) == 0

        # Test clearing history
        agent.conversation_history = [HumanMessage(content="test")]
        agent.clear_conversation_history()
        assert len(agent.conversation_history) == 0

        # Test getting history
        test_messages = [HumanMessage(content="test1"), AIMessage(content="response1")]
        agent.conversation_history = test_messages
        history = agent.get_conversation_history()
        assert len(history) == 2
        assert history[0].content == "test1"
        assert history[1].content == "response1"

    @pytest.mark.asyncio
    async def test_conversation_history_limit(self):
        """Test that conversation history is limited to prevent memory issues."""
        agent = ResumeAgent()

        # Fill conversation history beyond the limit
        for i in range(25):  # More than the 20 message limit
            agent.conversation_history.append(HumanMessage(content=f"message {i}"))

        mock_response = AIMessage(content="Test response")

        with patch.object(
            agent.workflow, "ainvoke", return_value={"messages": [mock_response]}
        ):
            await agent.chat("New message")

            # Should be limited to 20 messages + the new conversation (2 messages)
            assert len(agent.conversation_history) <= 22


class TestResumeAgentIntegration:
    """Integration tests for the Resume Agent with real LLM calls."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not settings.google_api_key and not settings.openai_api_key,
        reason="No API keys available",
    )
    async def test_real_agent_interaction(self):
        """Test real agent interaction with LLM (requires API key)."""
        agent = ResumeAgent()

        response = await agent.chat("Hello! Can you help me understand what you do?")

        assert isinstance(response, str)
        assert len(response) > 0
        assert len(agent.conversation_history) == 2

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not settings.google_api_key and not settings.openai_api_key,
        reason="No API keys available",
    )
    async def test_real_resume_analysis(self):
        """Test real resume analysis with LLM."""
        agent = ResumeAgent()

        simple_resume = {
            "basics": {"name": "Test User", "email": "test@example.com"},
            "work": [{"company": "Test Corp", "position": "Developer"}],
            "skills": [{"name": "Python"}],
        }

        response = await agent.analyze_resume(simple_resume)

        assert isinstance(response, str)
        assert len(response) > 50  # Should be a substantial response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
