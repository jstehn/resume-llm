"""Resume analysis and optimization agent using LangGraph."""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import json

from ..services.llm import llm_service
from ..models.resume import JSONResume
from ..models.job import JobAnalysisResponse


class ResumeAgentState(TypedDict):
    """State for the resume optimization agent."""
    messages: Annotated[List[BaseMessage], "List of conversation messages"]
    resume_data: Annotated[Optional[JSONResume], "Current resume data"]
    job_description: Annotated[Optional[str], "Job description for tailoring"]
    analysis_results: Annotated[Dict[str, Any], "Analysis results"]
    optimized_resume: Annotated[Optional[JSONResume], "Optimized resume"]
    user_feedback: Annotated[Optional[str], "User feedback on suggestions"]
    next_action: Annotated[Optional[str], "Next action to take"]


class ResumeAgent:
    """LangGraph-based agent for resume analysis and optimization."""
    
    def __init__(self):
        self.llm = llm_service.get_model()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph state graph."""
        workflow = StateGraph(ResumeAgentState)
        
        # Add nodes
        workflow.add_node("analyze_job", self.analyze_job_description)
        workflow.add_node("analyze_resume", self.analyze_resume)
        workflow.add_node("generate_suggestions", self.generate_suggestions)
        workflow.add_node("optimize_resume", self.optimize_resume)
        workflow.add_node("review_changes", self.review_changes)
        workflow.add_node("finalize", self.finalize_resume)
        
        # Add edges
        workflow.set_entry_point("analyze_job")
        workflow.add_edge("analyze_job", "analyze_resume")
        workflow.add_edge("analyze_resume", "generate_suggestions")
        workflow.add_edge("generate_suggestions", "optimize_resume")
        workflow.add_edge("optimize_resume", "review_changes")
        workflow.add_conditional_edges(
            "review_changes",
            self.should_continue,
            {
                "continue": "generate_suggestions",
                "finalize": "finalize",
                "end": END
            }
        )
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def analyze_job_description(self, state: ResumeAgentState) -> ResumeAgentState:
        """Analyze the job description to extract requirements."""
        job_description = state.get("job_description", "")
        if not job_description:
            state["analysis_results"]["error"] = "No job description provided"
            return state
        
        prompt = f"""
        Analyze the following job description and extract:
        1. Required skills and technologies
        2. Key responsibilities
        3. Experience requirements
        4. Education requirements
        5. Important keywords for ATS optimization
        
        Job Description:
        {job_description}
        
        Return your analysis as a structured JSON response.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        try:
            analysis = json.loads(response.content)
            state["analysis_results"].update(analysis)
        except json.JSONDecodeError:
            # Fallback if response isn't valid JSON
            state["analysis_results"]["raw_analysis"] = response.content
            state["analysis_results"]["error"] = "Could not parse analysis as JSON"
        
        return state
    
    async def analyze_resume(self, state: ResumeAgentState) -> ResumeAgentState:
        """Analyze the current resume against job requirements."""
        resume_data = state.get("resume_data")
        analysis_results = state.get("analysis_results", {})
        
        if not resume_data:
            state["analysis_results"]["resume_error"] = "No resume data provided"
            return state
        
        resume_json = resume_data.model_dump_json(indent=2)
        job_analysis = json.dumps(analysis_results, indent=2)
        
        prompt = f"""
        Compare this resume against the job requirements and provide:
        1. Missing skills that should be added
        2. Existing skills that should be emphasized
        3. Experience gaps to address
        4. Sections that need improvement
        5. ATS optimization suggestions
        
        Job Analysis:
        {job_analysis}
        
        Current Resume:
        {resume_json}
        
        Return your comparison as a structured JSON response.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        try:
            comparison = json.loads(response.content)
            state["analysis_results"]["resume_comparison"] = comparison
        except json.JSONDecodeError:
            state["analysis_results"]["resume_comparison"] = {
                "raw_comparison": response.content,
                "error": "Could not parse comparison as JSON"
            }
        
        return state
    
    async def generate_suggestions(self, state: ResumeAgentState) -> ResumeAgentState:
        """Generate specific suggestions for resume improvement."""
        analysis_results = state.get("analysis_results", {})
        resume_data = state.get("resume_data")
        
        if not resume_data or not analysis_results:
            return state
        
        analysis_json = json.dumps(analysis_results, indent=2)
        
        prompt = f"""
        Based on the job and resume analysis, generate specific, actionable suggestions:
        1. Specific bullet points to add or modify
        2. Skills to highlight or add
        3. Keywords to incorporate
        4. Section reorganization recommendations
        5. Content to remove or de-emphasize
        
        Analysis Results:
        {analysis_json}
        
        Provide concrete, implementable suggestions as a JSON response.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        try:
            suggestions = json.loads(response.content)
            state["analysis_results"]["suggestions"] = suggestions
        except json.JSONDecodeError:
            state["analysis_results"]["suggestions"] = {
                "raw_suggestions": response.content,
                "error": "Could not parse suggestions as JSON"
            }
        
        return state
    
    async def optimize_resume(self, state: ResumeAgentState) -> ResumeAgentState:
        """Apply optimizations to create an improved resume."""
        resume_data = state.get("resume_data")
        analysis_results = state.get("analysis_results", {})
        suggestions = analysis_results.get("suggestions", {})
        
        if not resume_data or not suggestions:
            return state
        
        resume_json = resume_data.model_dump_json(indent=2)
        suggestions_json = json.dumps(suggestions, indent=2)
        
        prompt = f"""
        Apply the suggested improvements to create an optimized resume.
        Return the complete optimized resume in JSON Resume format.
        
        Original Resume:
        {resume_json}
        
        Suggestions to Apply:
        {suggestions_json}
        
        Return ONLY the optimized resume as valid JSON Resume format.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        try:
            optimized_data = json.loads(response.content)
            optimized_resume = JSONResume(**optimized_data)
            state["optimized_resume"] = optimized_resume
        except (json.JSONDecodeError, ValueError) as e:
            state["analysis_results"]["optimization_error"] = f"Could not create optimized resume: {str(e)}"
        
        return state
    
    async def review_changes(self, state: ResumeAgentState) -> ResumeAgentState:
        """Review the changes and prepare for user feedback."""
        original_resume = state.get("resume_data")
        optimized_resume = state.get("optimized_resume")
        
        if not original_resume or not optimized_resume:
            state["next_action"] = "end"
            return state
        
        # Generate a summary of changes
        prompt = f"""
        Compare the original and optimized resumes and summarize:
        1. Major changes made
        2. New content added
        3. Content removed or modified
        4. Overall improvement strategy
        
        Original Resume Summary: {original_resume.basics.name} - {len(original_resume.work or [])} work experiences
        Optimized Resume Summary: {optimized_resume.basics.name} - {len(optimized_resume.work or [])} work experiences
        
        Provide a clear summary of changes for user review.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        state["analysis_results"]["change_summary"] = response.content
        state["next_action"] = "review"
        
        return state
    
    def should_continue(self, state: ResumeAgentState) -> str:
        """Determine if the agent should continue, finalize, or end."""
        user_feedback = state.get("user_feedback") or ""
        
        if "approve" in user_feedback.lower() or "finalize" in user_feedback.lower():
            return "finalize"
        elif "revise" in user_feedback.lower() or "change" in user_feedback.lower():
            return "continue"
        else:
            return "end"
    
    async def finalize_resume(self, state: ResumeAgentState) -> ResumeAgentState:
        """Finalize the optimized resume."""
        state["next_action"] = "complete"
        return state
    
    async def run(
        self,
        resume_data: JSONResume,
        job_description: str,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the resume optimization workflow."""
        initial_state = ResumeAgentState(
            messages=[],
            resume_data=resume_data,
            job_description=job_description,
            analysis_results={},
            optimized_resume=None,
            user_feedback=user_feedback,
            next_action=None
        )
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "analysis_results": result.get("analysis_results", {}),
            "optimized_resume": result.get("optimized_resume"),
            "change_summary": result.get("analysis_results", {}).get("change_summary"),
            "next_action": result.get("next_action")
        }
