"""Simple test runner for Gemini integration tests."""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resume_llm.services.llm import llm_service


@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic Gemini functionality."""
    print("🧪 Basic Gemini Functionality Tests")
    print("-" * 40)

    tests_passed = 0
    total_tests = 4

    # Test 1: Provider availability
    try:
        providers = llm_service.get_available_providers()
        if "gemini" in providers:
            print("✅ Test 1: Gemini provider is available")
            tests_passed += 1
        else:
            print("❌ Test 1: Gemini provider not available")
    except Exception as e:
        print(f"❌ Test 1: Error checking provider availability: {e}")

    # Test 2: Model creation
    try:
        model = llm_service.get_model(provider="gemini", model="gemma-3n-e4b-it")
        print("✅ Test 2: Model creation successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: Model creation failed: {e}")

    # Test 3: Simple response
    try:
        response = await llm_service.generate_response(
            messages=["Say 'Hello' in exactly one word."],
            provider="gemini",
            model="gemma-3n-e4b-it",
        )
        if response and len(response.strip()) > 0:
            print(f"✅ Test 3: Simple response generated: '{response[:50]}...'")
            tests_passed += 1
        else:
            print("❌ Test 3: Empty or invalid response")
    except Exception as e:
        print(f"❌ Test 3: Response generation failed: {e}")

    # Test 4: Resume-specific task
    try:
        response = await llm_service.generate_response(
            messages=[
                "List 2 important skills for a software engineer. Be very brief."
            ],
            provider="gemini",
            model="gemma-3n-e4b-it",
        )
        if response and any(
            word in response.lower()
            for word in [
                "problem-solving",
                "programming",
                "coding",
                "software",
                "development",
                "python",
                "java",
            ]
        ):
            print(f"✅ Test 4: Resume task completed: '{response[:50]}...'")
            tests_passed += 1
        else:
            print(
                f"❌ Test 4: Resume task failed or irrelevant response: '{response[:50]}...'"
            )
    except Exception as e:
        print(f"❌ Test 4: Resume task failed: {e}")

    print("-" * 40)
    print(
        f"📊 Results: {tests_passed}/{total_tests} tests passed ({tests_passed/total_tests*100:.1f}%)"
    )

    return tests_passed == total_tests


@pytest.mark.asyncio
async def test_performance():
    """Test response time and quality."""
    print("\n🚀 Performance Tests")
    print("-" * 40)

    import time

    start_time = time.time()

    try:
        response = await llm_service.generate_response(
            messages=[
                "Write a one-sentence professional summary for a Python developer."
            ],
            provider="gemini",
            model="gemma-3n-e4b-it",
        )

        end_time = time.time()
        response_time = end_time - start_time

        print(f"✅ Response time: {response_time:.2f} seconds")
        print(f"✅ Response length: {len(response)} characters")
        print(f"✅ Response preview: '{response[:100]}...'")

        if response_time < 10:  # Reasonable response time
            print("✅ Performance: Good response time")
            return True
        else:
            print("⚠️ Performance: Slow response time")
            return False

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def check_environment():
    """Check if environment is properly set up."""
    print("🔧 Environment Check")
    print("-" * 40)

    checks_passed = 0
    total_checks = 3

    # Check 1: Google API key
    if os.getenv("GOOGLE_API_KEY"):
        print("✅ GOOGLE_API_KEY is set")
        checks_passed += 1
    else:
        print("❌ GOOGLE_API_KEY not found in environment")

    # Check 2: Package installation
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        print("✅ langchain-google-genai package is installed")
        checks_passed += 1
    except ImportError:
        print("❌ langchain-google-genai package not installed")

    # Check 3: Settings configuration
    try:
        from resume_llm.config.settings import settings

        if hasattr(settings, "google_api_key"):
            print("✅ Settings configuration includes google_api_key")
            checks_passed += 1
        else:
            print("❌ Settings configuration missing google_api_key")
    except Exception as e:
        print(f"❌ Settings configuration error: {e}")

    print(f"📊 Environment: {checks_passed}/{total_checks} checks passed")
    return checks_passed == total_checks


async def main():
    """Run all tests."""
    print("🎯 Gemini Integration Test Suite")
    print("=" * 50)

    # Environment check
    env_ok = check_environment()

    if not env_ok:
        print("\n❌ Environment not properly configured. Please:")
        print("1. Set GOOGLE_API_KEY environment variable")
        print("2. Install langchain-google-genai package")
        print("3. Update settings configuration")
        return

    # Basic functionality tests
    basic_ok = await test_basic_functionality()

    # Performance tests
    perf_ok = await test_performance()

    # Final summary
    print("\n" + "=" * 50)
    print("🏁 FINAL RESULTS")
    print("=" * 50)

    if basic_ok and perf_ok:
        print("🎉 ALL TESTS PASSED! Gemini integration is working perfectly.")
        print(f"✅ Model: gemma-3n-e4b-it")
        print(f"✅ Provider: Google Gemini")
        print(f"✅ Integration: Complete")
    elif basic_ok:
        print("⚠️ BASIC TESTS PASSED, performance could be better.")
    else:
        print("❌ TESTS FAILED. Please check your configuration.")

    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
