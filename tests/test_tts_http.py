import os
import unittest
from unittest.mock import patch

import httpx

from lesson_media_kit.tts.base import ProviderConfigurationError, ProviderError, TTSRequest
from lesson_media_kit.tts.http_provider import HttpProvider, HttpProviderConfig


class HttpProviderTest(unittest.TestCase):
    def test_rejects_non_https_endpoint(self) -> None:
        with self.assertRaisesRegex(ProviderConfigurationError, "HTTPS"):
            HttpProviderConfig(endpoint="http://tts.example/v1", api_key_env="TEST_TTS_KEY")

    def test_error_redacts_api_key_and_provider_body(self) -> None:
        secret = "top-secret-token"

        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.headers["Authorization"], f"Bearer {secret}")
            return httpx.Response(401, text=f"bad token {secret}")

        transport = httpx.MockTransport(handler)
        config = HttpProviderConfig(
            endpoint="https://tts.example/v1",
            api_key_env="TEST_TTS_KEY",
            allowed_hosts=("tts.example",),
        )
        with patch.dict(os.environ, {"TEST_TTS_KEY": secret}, clear=False):
            provider = HttpProvider(config, transport=transport)
            with self.assertRaises(ProviderError) as caught:
                provider.synthesize(TTSRequest("s1", "Hello", "en"))
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn("bad token", str(caught.exception))

    def test_rejects_unapproved_response_type(self) -> None:
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, headers={"content-type": "text/html"}, text="no")
        )
        config = HttpProviderConfig(endpoint="https://tts.example/v1", api_key_env="TEST_TTS_KEY")
        with patch.dict(os.environ, {"TEST_TTS_KEY": "secret"}, clear=False):
            provider = HttpProvider(config, transport=transport)
            with self.assertRaisesRegex(ProviderError, "content type"):
                provider.synthesize(TTSRequest("s1", "Hello", "en"))
