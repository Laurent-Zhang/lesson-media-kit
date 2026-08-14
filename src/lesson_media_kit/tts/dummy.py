"""Deterministic offline WAV provider for examples and tests."""

import io
import wave

from lesson_media_kit.tts.base import TTSRequest, TTSResult


class DummyProvider:
    provider_id = "dummy"

    def synthesize(self, request: TTSRequest) -> TTSResult:
        duration_ms = max(250, min(5_000, len(request.text.encode("utf-8")) * 40))
        sample_rate = 8_000
        frame_count = sample_rate * duration_ms // 1_000
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(sample_rate)
            output.writeframes(b"\x00\x00" * frame_count)
        return TTSResult(
            audio=buffer.getvalue(),
            media_type="audio/wav",
            duration_ms=duration_ms,
            provider_metadata={"mode": "deterministic-silence"},
        )
