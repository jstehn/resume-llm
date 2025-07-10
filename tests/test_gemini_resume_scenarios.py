"""Integration tests for Gemini with real resume scenarios."""

import asyncio

from resume_llm.services.llm import llm_service


class GeminiResumeTests:
    """Test Gemini with real resume optimization scenarios."""

    def __init__(self):
        self.model_name = "gemini-2.0-flash-lite"
        self.test_results = []

    async def test_professional_summary_generation(self):
        """Test generating professional summaries."""
        print("\n🧪 Testing Professional Summary Generation...")

        test_cases = [
            {
                "input": (
                    "I'm a Python developer with 2 years experience in web development, "
                    "Django, and REST APIs."
                ),
                "expected_keywords": ["python", "web", "django", "api"],
            },
            {
                "input": (
                    "Frontend developer with React, JavaScript, and 3 years of experience "
                    "building user interfaces."
                ),
                "expected_keywords": ["react", "javascript", "frontend", "ui"],
            },
            {
                "input": (
                    "Data scientist with machine learning, pandas, and statistical "
                    "analysis experience."
                ),
                "expected_keywords": ["data", "machine learning", "analysis"],
            },
        ]

        for i, test_case in enumerate(test_cases, 1):
            try:
                prompt = (
                    f"Write a concise professional summary for this developer: "
                    f"{test_case['input']}. Keep it to 2-3 sentences."
                )

                response = await llm_service.generate_response(
                    messages=[prompt], provider="gemini", model=self.model_name
                )

                # Check if expected keywords are present
                keywords_found = [
                    kw
                    for kw in test_case["expected_keywords"]
                    if kw.lower() in response.lower()
                ]

                print(
                    f"  ✅ Test {i}: Generated summary "
                    f"({len(keywords_found)}/{len(test_case['expected_keywords'])} keywords found)"
                )
                print(f"     Summary: {response[:100]}...")

                self.test_results.append(
                    {
                        "test": f"Professional Summary {i}",
                        "status": "PASS" if keywords_found else "PARTIAL",
                        "keywords_found": keywords_found,
                    }
                )

            except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
                print(f"  ❌ Test {i} failed: {e}")
                self.test_results.append(
                    {
                        "test": f"Professional Summary {i}",
                        "status": "FAIL",
                        "error": str(e),
                    }
                )

    async def test_skill_recommendation(self):
        """Test skill recommendations for different roles."""
        print("\n🧪 Testing Skill Recommendations...")

        scenarios = [
            {
                "role": "Senior Python Developer",
                "experience": "5 years Python, Django, PostgreSQL",
                "target": "Technical Lead position",
            },
            {
                "role": "Frontend Engineer",
                "experience": "3 years React, TypeScript, CSS",
                "target": "Senior Frontend role at a startup",
            },
            {
                "role": "Full Stack Developer",
                "experience": "4 years MERN stack, AWS deployment",
                "target": "Full Stack Architect position",
            },
        ]

        for i, scenario in enumerate(scenarios, 1):
            try:
                prompt = f"""
                I'm applying for a {scenario['target']} role.
                My background: {scenario['experience']}
                Suggest 4 key skills I should highlight on my resume. Be specific and concise.
                """

                response = await llm_service.generate_response(
                    messages=[prompt], provider="gemini", model=self.model_name
                )

                print(f"  ✅ Test {i}: {scenario['role']} → {scenario['target']}")
                print(f"     Recommendations: {response[:150]}...")

                self.test_results.append(
                    {
                        "test": f"Skill Recommendation {i}",
                        "status": "PASS",
                        "scenario": scenario["role"],
                    }
                )

            except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
                print(f"  ❌ Test {i} failed: {e}")
                self.test_results.append(
                    {
                        "test": f"Skill Recommendation {i}",
                        "status": "FAIL",
                        "error": str(e),
                    }
                )

    async def test_job_match_analysis(self):
        """Test job description matching."""
        print("\n🧪 Testing Job Match Analysis...")

        job_description = """
        We're looking for a Senior Python Developer with:
        - 5+ years Python experience
        - Django/Flask web frameworks
        - PostgreSQL database experience
        - AWS cloud services
        - Team leadership experience
        - Agile development practices
        """

        candidate_profile = """
        Python Developer with 4 years experience:
        - Django web development
        - MySQL and PostgreSQL
        - Some AWS (EC2, S3)
        - Led 2 junior developers
        - Worked in Scrum teams
        """

        try:
            prompt = f"""
            Job Description: {job_description}

            Candidate Profile: {candidate_profile}

            Analyze the match and suggest 3 specific improvements for the resume to better
            align with this job. Be concise.
            """

            response = await llm_service.generate_response(
                messages=[prompt], provider="gemini", model=self.model_name
            )

            print("  ✅ Job match analysis completed")
            print(f"     Analysis: {response[:200]}...")

            self.test_results.append({"test": "Job Match Analysis", "status": "PASS"})

        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            print(f"  ❌ Job match analysis failed: {e}")
            self.test_results.append(
                {"test": "Job Match Analysis", "status": "FAIL", "error": str(e)}
            )

    async def test_resume_optimization_suggestions(self):
        """Test resume optimization suggestions."""
        print("\n🧪 Testing Resume Optimization...")

        sample_resume_section = """
        Work Experience:
        Software Developer at TechCorp (2021-2024)
        - Wrote Python code
        - Fixed bugs
        - Worked with team
        - Used databases
        """

        try:
            prompt = f"""
            Here's a work experience section from a resume:
            {sample_resume_section}

            Suggest 3 specific improvements to make it more impactful and professional.
            Focus on action verbs and quantifiable achievements.
            """

            response = await llm_service.generate_response(
                messages=[prompt], provider="gemini", model=self.model_name
            )

            print("  ✅ Resume optimization suggestions generated")
            print(f"     Suggestions: {response[:200]}...")

            self.test_results.append({"test": "Resume Optimization", "status": "PASS"})

        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            print(f"  ❌ Resume optimization failed: {e}")
            self.test_results.append(
                {"test": "Resume Optimization", "status": "FAIL", "error": str(e)}
            )

    def print_test_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("🧪 GEMINI RESUME TESTS SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        partial = sum(1 for r in self.test_results if r["status"] == "PARTIAL")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Partial: {partial}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed + partial) / total * 100:.1f}%")

        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(
                        f"  ❌ {result['test']}: {result.get('error', 'Unknown error')}"
                    )

        print("\n" + "=" * 60)

    async def run_all_tests(self):
        """Run all resume-related tests."""
        print("🚀 Starting Gemini Resume Integration Tests...")
        print(f"Using model: {self.model_name}")

        # Check if Gemini is available
        if "gemini" not in llm_service.get_available_providers():
            print(
                "❌ Gemini not available. Please set GOOGLE_API_KEY environment variable."
            )
            return False

        # Run all test suites
        await self.test_professional_summary_generation()
        await self.test_skill_recommendation()
        await self.test_job_match_analysis()
        await self.test_resume_optimization_suggestions()

        # Print summary
        self.print_test_summary()

        return True


async def main():
    """Main test runner."""
    tester = GeminiResumeTests()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
