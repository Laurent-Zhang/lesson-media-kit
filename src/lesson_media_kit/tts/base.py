"""Provider-neutral TTS request and result types."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class TTSRequest:
    segment_id: str
    text: str
    language: str


@dataclass(frozen=True)
class TTSResult:
    audio: bytes
    media_type: str
    duration_ms: int
    provider_metadata: dict[str, str] = field(default_factory=dict)


class TTSProvider(Protocol):
    provider_id: str

    def synthesize(self, request: TTSRequest) -> TTSResult: ...


class ProviderError(RuntimeError):
    """Safe provider failure suitable for user-facing output."""


class ProviderConfigurationError(ProviderError):
    """A provider cannot run with the supplied trusted configuration."""
