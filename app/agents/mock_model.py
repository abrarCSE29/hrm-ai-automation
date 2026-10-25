"""Deterministic mock model for CI (no LLM calls)."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from agno.models.base import Model
from agno.models.response import ModelResponse


@dataclass
class MockModel(Model):
    id: str = "mock-model"
    name: str = "MockModel"
    provider: str = "mock"
    responses: list[ModelResponse] = field(default_factory=list)
    _index: int = 0

    def __post_init__(self):
        super().__post_init__()
        if not self.responses:
            self.responses = [ModelResponse(content="OK")]

    def _next(self) -> ModelResponse:
        if self._index < len(self.responses):
            r = self.responses[self._index]
            self._index += 1
            return r
        return self.responses[-1]

    def invoke(self, *args, **kwargs) -> ModelResponse:
        return self._next()

    async def ainvoke(self, *args, **kwargs) -> ModelResponse:
        return self._next()

    def invoke_stream(self, *args, **kwargs) -> Iterator[ModelResponse]:
        yield self._next()

    async def ainvoke_stream(self, *args, **kwargs):
        yield self._next()

    def _parse_provider_response(self, response: Any, **kwargs) -> ModelResponse:
        return response if isinstance(response, ModelResponse) else ModelResponse(content=str(response))

    def _parse_provider_response_delta(self, response: Any) -> ModelResponse:
        return ModelResponse(content=str(response))
