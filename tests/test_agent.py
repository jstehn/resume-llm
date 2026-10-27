import json
from pathlib import Path
from typing import Any

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from pydantic import Field

from resume_llm import cli
from resume_llm.agents.agent import TailoringError, tailor_resume
from resume_llm.utils.jsonresume_validator import validate_resume

RESUME_PATH = Path("dummy_data", "resumes", "sample-jsonresume.json")
JOB_PATH = Path("dummy_data", "jobs", "sample-job.txt")


class RecordingChatModel(FakeListChatModel):
    """Fake chat model that also records the last message of each prompt."""

    prompts: list[str] = Field(default_factory=list)

    def _call(self, messages, stop=None, run_manager=None, **kwargs):
        self.prompts.append(str(messages[-1].content))
        return super()._call(messages, stop, run_manager, **kwargs)


@pytest.fixture(name="resume")
def resume_fixture() -> dict[str, Any]:
    return json.loads(RESUME_PATH.read_text(encoding="utf-8"))


@pytest.fixture(name="job")
def job_fixture() -> str:
    return JOB_PATH.read_text(encoding="utf-8")


def test_returns_valid_resume(resume, job):
    llm = RecordingChatModel(responses=[json.dumps(resume)])
    assert tailor_resume(llm, resume, job) == resume
    assert len(llm.prompts) == 1
    assert "Hooli" in llm.prompts[0]


def test_accepts_markdown_fenced_json(resume, job):
    llm = RecordingChatModel(responses=[f"```json\n{json.dumps(resume)}\n```"])
    assert tailor_resume(llm, resume, job) == resume


def test_retries_after_invalid_json(resume, job):
    llm = RecordingChatModel(responses=["not json", json.dumps(resume)])
    assert tailor_resume(llm, resume, job) == resume
    assert len(llm.prompts) == 2
    assert "invalid JSON" in llm.prompts[1]


def test_retries_after_schema_violation(resume, job):
    invalid = {**resume, "work": [{"name": "Pied Piper", "startDate": "01-2013"}]}
    llm = RecordingChatModel(responses=[json.dumps(invalid), json.dumps(resume)])
    assert tailor_resume(llm, resume, job) == resume
    assert "work/0/startDate" in llm.prompts[1]


def test_gives_up_after_max_attempts(resume, job):
    llm = RecordingChatModel(responses=["not json", "[]", "still not json"])
    with pytest.raises(TailoringError, match="after 2 attempt"):
        tailor_resume(llm, resume, job, max_attempts=2)
    assert len(llm.prompts) == 2


def test_cli_writes_output(monkeypatch, tmp_path, resume):
    llm = RecordingChatModel(responses=[json.dumps(resume)])
    monkeypatch.setattr(cli, "get_llm", lambda *args, **kwargs: llm)
    output = tmp_path / "tailored.json"
    code = cli.main(["tailor", str(RESUME_PATH), str(JOB_PATH), "-o", str(output)])
    assert code == 0
    assert json.loads(output.read_text(encoding="utf-8")) == resume


def test_cli_reports_failure(monkeypatch, capsys):
    llm = RecordingChatModel(responses=["not json", "not json"])
    monkeypatch.setattr(cli, "get_llm", lambda *args, **kwargs: llm)
    code = cli.main(["tailor", str(RESUME_PATH), str(JOB_PATH)])
    assert code == 1
    assert "No valid resume" in capsys.readouterr().err


@pytest.mark.live
def test_live_ollama(resume, job):
    from resume_llm.llms import get_llm

    llm = get_llm("ollama", reasoning=False)
    tailored = tailor_resume(llm, resume, job)
    assert validate_resume(tailored)
    assert tailored["basics"]["name"] == resume["basics"]["name"]
