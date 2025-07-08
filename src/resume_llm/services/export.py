"""PDF export service for generating resume PDFs."""

from pathlib import Path
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from jinja2 import Template
import tempfile

from ..models.resume import JSONResume


class PDFExportService:
    """Service for exporting resumes to PDF format."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=6,
            spaceAfter=3,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=3,
            fontName='Helvetica-Oblique'
        ))
    
    def _format_date_range(self, start_date, end_date):
        """Format date range for display."""
        if not start_date:
            return ""
        
        start_str = start_date.strftime("%m/%Y") if start_date else ""
        end_str = end_date.strftime("%m/%Y") if end_date else "Present"
        
        return f"{start_str} - {end_str}"
    
    def generate_pdf(
        self,
        resume: JSONResume,
        output_path: Path,
        template: str = "default"
    ) -> Path:
        """Generate a PDF from a JSON Resume."""
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        story = []
        
        # Header with name and contact info
        self._add_header(story, resume)
        
        # Summary/Objective
        if resume.basics.summary:
            self._add_summary(story, resume.basics.summary)
        
        # Work Experience
        if resume.work:
            self._add_work_experience(story, resume.work)
        
        # Education
        if resume.education:
            self._add_education(story, resume.education)
        
        # Skills
        if resume.skills:
            self._add_skills(story, resume.skills)
        
        # Projects
        if resume.projects:
            self._add_projects(story, resume.projects)
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _add_header(self, story, resume):
        """Add header with name and contact information."""
        # Name
        story.append(Paragraph(resume.basics.name, self.styles['CustomTitle']))
        
        # Contact info
        contact_parts = []
        if resume.basics.email:
            contact_parts.append(resume.basics.email)
        if resume.basics.phone:
            contact_parts.append(resume.basics.phone)
        if resume.basics.location and resume.basics.location.city:
            location = f"{resume.basics.location.city}"
            if resume.basics.location.region:
                location += f", {resume.basics.location.region}"
            contact_parts.append(location)
        
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            contact_style = ParagraphStyle(
                name='Contact',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=12
            )
            story.append(Paragraph(contact_text, contact_style))
        
        story.append(Spacer(1, 0.1*inch))
    
    def _add_summary(self, story, summary):
        """Add summary/objective section."""
        story.append(Paragraph("Summary", self.styles['SectionHeading']))
        story.append(Paragraph(summary, self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    def _add_work_experience(self, story, work_experiences):
        """Add work experience section."""
        story.append(Paragraph("Work Experience", self.styles['SectionHeading']))
        
        for job in work_experiences:
            # Job title and company
            story.append(Paragraph(job.position, self.styles['JobTitle']))
            
            company_line = job.name
            if hasattr(job, 'start_date') or hasattr(job, 'end_date'):
                date_range = self._format_date_range(
                    getattr(job, 'start_date', None),
                    getattr(job, 'end_date', None)
                )
                if date_range:
                    company_line += f" | {date_range}"
            
            story.append(Paragraph(company_line, self.styles['Company']))
            
            # Job description/summary
            if job.summary:
                story.append(Paragraph(job.summary, self.styles['Normal']))
            
            # Highlights/achievements
            if job.highlights:
                for highlight in job.highlights:
                    story.append(Paragraph(f"• {highlight}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.1*inch))
    
    def _add_education(self, story, education_list):
        """Add education section."""
        story.append(Paragraph("Education", self.styles['SectionHeading']))
        
        for edu in education_list:
            # Degree and institution
            degree_text = ""
            if edu.study_type and edu.area:
                degree_text = f"{edu.study_type} in {edu.area}"
            elif edu.area:
                degree_text = edu.area
            elif edu.study_type:
                degree_text = edu.study_type
            
            if degree_text:
                story.append(Paragraph(degree_text, self.styles['JobTitle']))
            
            institution_line = edu.institution
            if hasattr(edu, 'start_date') or hasattr(edu, 'end_date'):
                date_range = self._format_date_range(
                    getattr(edu, 'start_date', None),
                    getattr(edu, 'end_date', None)
                )
                if date_range:
                    institution_line += f" | {date_range}"
            
            story.append(Paragraph(institution_line, self.styles['Company']))
            
            if edu.score:
                story.append(Paragraph(f"GPA: {edu.score}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.05*inch))
    
    def _add_skills(self, story, skills_list):
        """Add skills section."""
        story.append(Paragraph("Skills", self.styles['SectionHeading']))
        
        # Group skills by category or display as list
        skills_by_category = {}
        other_skills = []
        
        for skill in skills_list:
            if skill.keywords:
                # Use the skill name as category and keywords as skills
                skills_by_category[skill.name] = skill.keywords
            else:
                other_skills.append(skill.name)
        
        # Display categorized skills
        for category, skill_list in skills_by_category.items():
            skills_text = f"<b>{category}:</b> " + ", ".join(skill_list)
            story.append(Paragraph(skills_text, self.styles['Normal']))
        
        # Display other skills
        if other_skills:
            if skills_by_category:
                other_text = f"<b>Other:</b> " + ", ".join(other_skills)
            else:
                other_text = ", ".join(other_skills)
            story.append(Paragraph(other_text, self.styles['Normal']))
        
        story.append(Spacer(1, 0.1*inch))
    
    def _add_projects(self, story, projects_list):
        """Add projects section."""
        story.append(Paragraph("Projects", self.styles['SectionHeading']))
        
        for project in projects_list:
            # Project name
            story.append(Paragraph(project.name, self.styles['JobTitle']))
            
            # Project description
            if project.description:
                story.append(Paragraph(project.description, self.styles['Normal']))
            
            # Project highlights
            if project.highlights:
                for highlight in project.highlights:
                    story.append(Paragraph(f"• {highlight}", self.styles['Normal']))
            
            # Technologies used
            if project.keywords:
                tech_text = f"<b>Technologies:</b> " + ", ".join(project.keywords)
                story.append(Paragraph(tech_text, self.styles['Normal']))
            
            story.append(Spacer(1, 0.1*inch))


# Global service instance
pdf_export_service = PDFExportService()
