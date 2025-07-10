"""Simple test runner for Gemini integration tests.

To run with timing information:
- pytest tests/test_gemini_integration.py -v  # Show test durations
- pytest tests/test_gemini_integration.py --durations=5  # Show 5 slowest tests
"""

import asyncio
import os
import time

import pytest

from resume_llm.config.settings import settings
from resume_llm.services.llm import llm_service


@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic Gemini functionality."""
    print("🧪 Basic Gemini Functionality Tests")
    print("-" * 40)

    passed = 0
    total = 4

    # Test 1: Provider availability
    try:
        providers = llm_service.get_available_providers()
        if "gemini" in providers:
            print("✅ Test 1: Gemini provider is available")
            passed += 1
        else:
            print("❌ Test 1: Gemini provider not available")
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
        print(f"❌ Test 1: Error checking provider availability: {e}")

    # Test 2: Model creation
    try:
        _ = llm_service.get_model(provider="gemini", model="gemma-3n-e4b-it")
        print("✅ Test 2: Model creation successful")
        passed += 1
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
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
            passed += 1
        else:
            print("❌ Test 3: Empty or invalid response")
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
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
            passed += 1
        else:
            print(
                f"❌ Test 4: Resume task failed or irrelevant response: '{response[:50]}...'"
            )
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
        print(f"❌ Test 4: Resume task failed: {e}")

    print("-" * 40)
    print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    return passed == total


@pytest.mark.asyncio
async def test_performance():
    """Test response time and quality."""
    print("\n🚀 Performance Tests")
    print("-" * 40)

    start_time = time.perf_counter()

    try:
        response = await llm_service.generate_response(
            messages=[
                "Write a one-sentence professional summary for a Python developer."
            ],
            provider="gemini",
            model="gemma-3n-e4b-it",
        )

        response_time = time.perf_counter() - start_time

        print(f"✅ Response time: {response_time:.2f} seconds")
        print(f"✅ Response length: {len(response)} characters")
        print(f"✅ Response preview: '{response[:100]}...'")

        # Assert performance expectations
        assert response_time < 10, f"Response too slow: {response_time:.2f}s"
        assert len(response) > 10, "Response too short"
        assert response.strip(), "Empty response"

        print("✅ Performance: All assertions passed")
        return True

    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
        print(f"❌ Performance test failed: {e}")
        return False


def check_environment():
    """Check if environment is properly set up."""
    print("🔧 Environment Check")
    print("-" * 40)

    checks_passed = 0
    total_checks = 2

    # Check 1: Google API key
    if os.getenv("GOOGLE_API_KEY"):
        print("✅ GOOGLE_API_KEY is set")
        checks_passed += 1
    else:
        print("❌ GOOGLE_API_KEY not found in environment")

    # Check 2: Settings configuration
    try:
        if hasattr(settings, "google_api_key"):
            print("✅ Settings configuration includes google_api_key")
            checks_passed += 1
        else:
            print("❌ Settings configuration missing google_api_key")
    except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
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
        print("2. Update settings configuration")
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
        print("✅ Model: gemma-3n-e4b-it")
        print("✅ Provider: Google Gemini")
        print("✅ Integration: Complete")
    elif basic_ok:
        print("⚠️ BASIC TESTS PASSED, performance could be better.")
    else:
        print("❌ TESTS FAILED. Please check your configuration.")

    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
