import argparse
import types
import unittest
from unittest import mock

from qasserbench.generation.clients import OpenAICompatibleClient
from scripts.run_generation import build_generation_client


class _FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str, finish_reason: str = "stop") -> None:
        self.message = _FakeMessage(content)
        self.finish_reason = finish_reason


class _FakeCompletions:
    def __init__(self, recorder: dict[str, object]) -> None:
        self._recorder = recorder

    def create(self, **kwargs):
        self._recorder.update(kwargs)
        return types.SimpleNamespace(
            id="resp_123",
            model=kwargs["model"],
            choices=[_FakeChoice("```python\nassert True\n```")],
            usage=_FakeUsage(prompt_tokens=12, completion_tokens=5),
        )


class _FakeOpenAI:
    def __init__(self, recorder: dict[str, object]) -> None:
        self.chat = types.SimpleNamespace(completions=_FakeCompletions(recorder))


class OpenAICompatibleClientTests(unittest.TestCase):
    def test_build_generation_client_reads_openai_compatible_settings_from_env(self) -> None:
        args = argparse.Namespace(
            client="openai-compatible",
            model=None,
            model_id="unused-static-model",
            response_text="unused",
            api_base_url=None,
            api_key_env="QAB_API_KEY",
            temperature=0.3,
            max_output_tokens=400,
        )

        with mock.patch.dict(
            "os.environ",
            {
                "QAB_MODEL": "env-model",
                "QAB_API_KEY": "env-secret",
                "QAB_API_BASE_URL": "https://example.invalid/v1",
            },
            clear=False,
        ):
            with mock.patch("scripts.run_generation.OpenAICompatibleClient") as client_cls:
                build_generation_client(args)

        client_cls.assert_called_once_with(
            model_name="env-model",
            api_key="env-secret",
            api_base_url="https://example.invalid/v1",
            temperature=0.3,
            max_output_tokens=400,
        )

    def test_calls_chat_completions_with_rendered_prompt(self) -> None:
        init_calls: list[dict[str, object]] = []
        request_calls: dict[str, object] = {}

        def fake_openai_factory(*, api_key: str, base_url: str | None = None):
            init_calls.append({"api_key": api_key, "base_url": base_url})
            return _FakeOpenAI(request_calls)

        fake_module = types.SimpleNamespace(OpenAI=fake_openai_factory)

        with mock.patch(
            "qasserbench.generation.clients._load_openai_sdk",
            return_value=fake_module,
        ):
            client = OpenAICompatibleClient(
                model_name="test-model",
                api_key="secret",
                api_base_url="https://example.invalid/v1",
                temperature=0.2,
                max_output_tokens=256,
            )
            response = client.generate(
                prompt_text="rendered prompt text",
                task_id="QAB01",
                trial_index=2,
            )

        self.assertEqual(init_calls, [{"api_key": "secret", "base_url": "https://example.invalid/v1"}])
        self.assertEqual(request_calls["model"], "test-model")
        self.assertEqual(request_calls["messages"], [{"role": "user", "content": "rendered prompt text"}])
        self.assertEqual(request_calls["temperature"], 0.2)
        self.assertEqual(request_calls["max_tokens"], 256)
        self.assertEqual(response.text, "```python\nassert True\n```")
        self.assertEqual(response.payload["finish_reason"], "stop")
        self.assertEqual(response.payload["provider_type"], "openai-compatible")
        self.assertEqual(response.payload["task_id"], "QAB01")
        self.assertEqual(response.payload["trial_index"], 2)
        self.assertEqual(response.payload["temperature"], 0.2)
        self.assertEqual(response.payload["max_output_tokens"], 256)
        self.assertEqual(response.payload["prompt_tokens"], 12)
        self.assertEqual(response.payload["completion_tokens"], 5)
        self.assertEqual(response.payload["total_tokens"], 17)

    def test_raises_helpful_error_when_openai_sdk_is_missing(self) -> None:
        with mock.patch(
            "qasserbench.generation.clients._load_openai_sdk",
            side_effect=ModuleNotFoundError("No module named 'openai'"),
        ):
            with self.assertRaisesRegex(RuntimeError, "openai package is required"):
                OpenAICompatibleClient(
                    model_name="test-model",
                    api_key="secret",
                )


if __name__ == "__main__":
    unittest.main()
