import unittest

from lesson_media_kit.tts.base import TTSRequest
from lesson_media_kit.tts.dummy import DummyProvider


class DummyProviderTest(unittest.TestCase):
    def test_is_deterministic_and_returns_wav(self) -> None:
        provider = DummyProvider()
        request = TTSRequest(segment_id="s1", text="你好", language="zh-CN")
        first = provider.synthesize(request)
        second = provider.synthesize(request)
        self.assertEqual(first.audio, second.audio)
        self.assertTrue(first.audio.startswith(b"RIFF"))
        self.assertEqual(first.media_type, "audio/wav")
