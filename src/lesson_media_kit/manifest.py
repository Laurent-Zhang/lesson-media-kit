"""Deterministic build manifest generation."""

import hashlib
import json
from dataclasses import asdict, dataclass

from lesson_media_kit import __version__


@dataclass(frozen=True)
class BuildManifest:
    schema_version: int
    tool_version: str
    lesson_sha256: str
    provider: str
    provider_metadata: dict[str, str]
    status: str
    files: dict[str, str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def create_manifest(
    *,
    lesson_bytes: bytes,
    provider: str,
    provider_metadata: dict[str, str],
    files: dict[str, bytes],
) -> BuildManifest:
    safe_metadata = {
        key: value
        for key, value in provider_metadata.items()
        if key in {"mode", "model", "endpoint_host", "version"}
    }
    return BuildManifest(
        schema_version=1,
        tool_version=__version__,
        lesson_sha256=digest(lesson_bytes),
        provider=provider,
        provider_metadata=safe_metadata,
        status="complete",
        files={path: digest(data) for path, data in sorted(files.items())},
    )
