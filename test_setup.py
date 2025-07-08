"""Simple test script to verify the setup."""

import asyncio
import json
from pathlib import Path

from src.resume_llm.database.connection import init_db
from src.resume_llm.models.resume import JSONResume
from src.resume_llm.services.llm import llm_service
from src.resume_llm.agents.resume_agent import ResumeAgent


async def test_basic_functionality():
    """Test basic functionality of the resume LLM system."""
    print("🔍 Testing Resume LLM Setup...")
    
    # Initialize database
    print("📊 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # Check LLM providers
    print("\n🤖 Checking LLM providers...")
    try:
        providers = llm_service.get_provider_info()
        for name, info in providers.items():
            status = "✅ Available" if info["available"] else "❌ Not available"
            default = " (default)" if info["is_default"] else ""
            print(f"  {name}: {status}{default}")
    except Exception as e:
        print(f"❌ LLM provider check failed: {e}")
    
    # Test JSON Resume parsing
    print("\n📄 Testing JSON Resume parsing...")
    try:
        sample_resume_path = Path("data/examples/sample_resume.json")
        if sample_resume_path.exists():
            with open(sample_resume_path, "r", encoding="utf-8") as f:
                resume_data = json.load(f)
            
            resume = JSONResume(**resume_data)
            print(f"✅ Successfully parsed resume for: {resume.basics.name}")
            print(f"   Work experiences: {len(resume.work or [])}")
            print(f"   Skills: {len(resume.skills or [])}")
        else:
            print("❌ Sample resume file not found")
    except Exception as e:
        print(f"❌ JSON Resume parsing failed: {e}")
    
    # Test LLM integration (only if available)
    print("\n🧠 Testing LLM integration...")
    try:
        available_providers = llm_service.get_available_providers()
        if available_providers:
            response = await llm_service.generate_response([
                "Hello! Please respond with 'Resume LLM is working!' to confirm the connection."
            ])
            print(f"✅ LLM Response: {response[:100]}...")
        else:
            print("⚠️  No LLM providers available - skipping LLM test")
    except Exception as e:
        print(f"❌ LLM integration test failed: {e}")
    
    print("\n🎉 Basic functionality test completed!")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
