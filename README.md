# resume-llm

This project seeks to create a simple open source tool for resume refinement using a variety of open source tools. This was inspired by my experience applying to jobs. I have an broad range of skills and experiences working in different fields, startups, and contract work. It lead to long resumes that provided more information than most employers needed and attempting to tailor a resume sometimes lead to me realizing there were important things I missed. What if I had an AI assistant to help speed through the process? I wanted something that could identify key skills that I should include and prompted me to think closely about the application. In the end, I'd have a much tighter resume and the recruiter or hiring manager would have a document that was far more useful.

- [JSON Resume](https://jsonresume.org/): The open source initiative to create a JSON-based standard for resumes. For developers, by developers.
- [LangGraph](https://www.langchain.com/langgraph): To design agents that reliably handle complex tasks.

A rough roadmap of features include:
1) Resume ingestion and conversion into a JSON resume format.
2) Tracking different users with different configurations, api keys, and work experience.
3) Resume version storage that can also be .
4) A stateful AI agent that can converse with the user to help tailor the resume to a specific job description.
6) Exporting the resume as a PDF.
7) Bring your own models. Local LLMs or use whatever API you'd like!
