from __future__ import annotations

from contextlib import contextmanager

from app import agent as agent_module


class ManagedPrompt:
    version = 3

    def compile(self, **variables: str) -> str:
        return (
            f"Feature={variables['feature']}\n"
            f"Docs={variables['docs']}\n"
            f"Question={variables['message']}"
        )


class RecordingLangfuseClient:
    def __init__(self) -> None:
        self.prompt = ManagedPrompt()
        self.span_updates: list[dict] = []

    def get_prompt(self, name: str, **kwargs):
        return self.prompt

    def update_current_span(self, **kwargs) -> None:
        self.span_updates.append(kwargs)

    def update_current_generation(self, **kwargs) -> None:
        return None


def test_agent_records_prompt_version_with_v4_observation_api(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_PROMPT_NAME", "day13-chat")
    monkeypatch.setenv("LANGFUSE_PROMPT_LABEL", "production")
    client = RecordingLangfuseClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client)
    monkeypatch.setattr("app.mock_llm.get_langfuse_client", lambda: client)
    monkeypatch.setattr(agent_module, "tracing_enabled", lambda: True)

    propagated: list[dict] = []

    @contextmanager
    def record_attributes(**kwargs):
        propagated.append(kwargs)
        yield

    monkeypatch.setattr(agent_module, "propagate_attributes", record_attributes)

    agent = agent_module.LabAgent()
    run = getattr(agent_module.LabAgent.run, "__wrapped__", agent_module.LabAgent.run)
    run(
        agent,
        user_id="student-01",
        feature="qa-student@vinuni.edu.vn",
        session_id="session-0901234567",
        message="Explain traces",
        correlation_id="req-12345678",
    )

    span_update = client.span_updates[-1]
    assert span_update["metadata"] == {
        "doc_count": 1,
        "query_preview": "Explain traces",
        "prompt_name": "day13-chat",
        "prompt_label": "production",
        "prompt_version": "3",
        "prompt_source": "langfuse",
        "prompt_fetch_error": "",
    }
    assert span_update["version"] == "3"
    assert propagated[0]["metadata"]["correlation_id"] == "req-12345678"
    assert propagated[0]["session_id"] == "session-[REDACTED_PHONE_VN]"
    assert propagated[0]["metadata"]["feature"] == "[REDACTED_EMAIL]"
    assert "qa-student@vinuni.edu.vn" not in propagated[0]["tags"]
    assert propagated[-1]["prompt"] is client.prompt


def test_agent_uses_local_prompt_without_initializing_langfuse(monkeypatch) -> None:
    def unexpected_client():
        raise AssertionError("Langfuse client must not be initialized when tracing is off")

    monkeypatch.setattr(agent_module, "tracing_enabled", lambda: False)
    monkeypatch.setattr(agent_module, "get_langfuse_client", unexpected_client)
    monkeypatch.setattr(agent_module, "propagate_attributes", unexpected_client)
    monkeypatch.setattr("app.mock_llm.tracing_enabled", lambda: False)
    monkeypatch.setattr("app.mock_llm.get_langfuse_client", unexpected_client)

    agent = agent_module.LabAgent()
    run = getattr(agent_module.LabAgent.run, "__wrapped__", agent_module.LabAgent.run)
    result = run(
        agent,
        user_id="student-01",
        feature="qa",
        session_id="session-01",
        message="Explain traces",
        correlation_id="req-12345678",
    )

    assert result.answer.startswith("Starter answer.")
