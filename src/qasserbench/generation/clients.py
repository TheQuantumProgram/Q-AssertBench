"""Client abstractions for repeated generation trials."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class GenerationResponse:
    """Structured raw model response."""

    text: str
    payload: dict[str, Any] = field(default_factory=dict)


class ModelClient(Protocol):
    """Minimal interface required by the generation driver."""

    @property
    def model_id(self) -> str:
        ...

    def generate(self, *, prompt_text: str, task_id: str, trial_index: int) -> GenerationResponse:
        ...


def _load_openai_sdk():
    return importlib.import_module("openai")


def _extract_message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
                    continue
            text = getattr(item, "text", None)
            if isinstance(text, str):
                parts.append(text)
        return "\n".join(part for part in parts if part)
    return ""


@dataclass(frozen=True)
class StaticResponseClient:
    """Local client that returns the same response for every request."""

    model_name: str
    response_text: str

    @property
    def model_id(self) -> str:
        return self.model_name

    def generate(self, *, prompt_text: str, task_id: str, trial_index: int) -> GenerationResponse:
        return GenerationResponse(
            text=self.response_text,
            payload={
                "provider_type": "static",
                "task_id": task_id,
                "trial_index": trial_index,
                "prompt_length": len(prompt_text),
                "temperature": None,
                "max_output_tokens": None,
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
            },
        )


@dataclass(frozen=True)
class OpenAICompatibleClient:
    """Model client backed by an OpenAI SDK compatible chat-completions endpoint."""

    model_name: str
    api_key: str
    api_base_url: str | None = None
    temperature: float = 0.0
    max_output_tokens: int = 512
    _client: Any = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        try:
            sdk = _load_openai_sdk()
        except ModuleNotFoundError as exc:  # pragma: no cover - exercised via patching in tests
            raise RuntimeError(
                "The openai package is required for OpenAI-compatible generation. "
                "Install it in project_code/.venv first."
            ) from exc

        object.__setattr__(
            self,
            "_client",
            sdk.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base_url,
            ),
        )

    @property
    def model_id(self) -> str:
        return self.model_name

    def generate(self, *, prompt_text: str, task_id: str, trial_index: int) -> GenerationResponse:
        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=self.temperature,
            max_tokens=self.max_output_tokens,
        )
        choices = getattr(response, "choices", None) or []
        choice = choices[0] if choices else None
        message = getattr(choice, "message", None)
        content = getattr(message, "content", "")
        text = _extract_message_text(content)
        usage = getattr(response, "usage", None)

        return GenerationResponse(
            text=text,
            payload={
                "provider_type": "openai-compatible",
                "task_id": task_id,
                "trial_index": trial_index,
                "api_base_url": self.api_base_url,
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
                "response_id": getattr(response, "id", None),
                "response_model": getattr(response, "model", None),
                "finish_reason": getattr(choice, "finish_reason", None),
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            },
        )
