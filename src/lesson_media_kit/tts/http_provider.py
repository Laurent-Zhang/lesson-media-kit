"""Bounded HTTPS text-to-speech provider."""

import os
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from lesson_media_kit.tts.base import (
    ProviderConfigurationError,
    ProviderError,
    TTSRequest,
    TTSResult,
)


@dataclass(frozen=True)
class HttpProviderConfig:
    endpoint: str
    api_key_env: str
    allowed_hosts: tuple[str, ...] = ()
    allowed_media_types: tuple[str, ...] = ("audio/mpeg", "audio/wav")
    maximum_response_bytes: int = 10 * 1024 * 1024

    def __post_init__(self) -> None:
        parsed = urlparse(self.endpoint)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ProviderConfigurationError("TTS endpoint must use HTTPS")
        if parsed.username or parsed.password:
            raise ProviderConfigurationError("TTS endpoint must not contain credentials")
        if self.allowed_hosts and parsed.hostname not in self.allowed_hosts:
            raise ProviderConfigurationError("TTS endpoint host is not allowlisted")
        if not self.api_key_env or not self.api_key_env.replace("_", "").isalnum():
            raise ProviderConfigurationError("invalid credential environment variable name")


class HttpProvider:
    provider_id = "http"

    def __init__(
        self,
        config: HttpProviderConfig,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.config = config
        self._transport = transport

    def synthesize(self, request: TTSRequest) -> TTSResult:
        key = os.environ.get(self.config.api_key_env)
        if not key:
            raise ProviderConfigurationError(
                f"missing credential environment variable: {self.config.api_key_env}"
            )
        try:
            with (
                httpx.Client(
                    follow_redirects=False,
                    timeout=httpx.Timeout(30.0, connect=5.0),
                    transport=self._transport,
                ) as client,
                client.stream(
                    "POST",
                    self.config.endpoint,
                    headers={"Authorization": f"Bearer {key}"},
                    json={"text": request.text, "language": request.language},
                ) as response,
            ):
                if 300 <= response.status_code < 400:
                    raise ProviderError("TTS provider redirect was rejected")
                if not 200 <= response.status_code < 300:
                    raise ProviderError(f"TTS provider returned HTTP {response.status_code}")
                media_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
                if media_type not in self.config.allowed_media_types:
                    raise ProviderError("TTS provider returned an unsupported content type")
                chunks: list[bytes] = []
                size = 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > self.config.maximum_response_bytes:
                        raise ProviderError("TTS provider response exceeded the size limit")
                    chunks.append(chunk)
        except ProviderError:
            raise
        except (httpx.TimeoutException, httpx.TransportError):
            raise ProviderError("TTS provider network request failed") from None
        return TTSResult(
            audio=b"".join(chunks),
            media_type=media_type,
            duration_ms=0,
            provider_metadata={"endpoint_host": urlparse(self.config.endpoint).hostname or ""},
        )
