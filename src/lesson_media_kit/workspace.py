"""Confined and ownership-aware generated output writes."""

import json
import os
import secrets
from pathlib import Path, PureWindowsPath


class UnsafeOutputPath(ValueError):
    """A generated path could escape the approved output directory."""


class UnownedOutputError(ValueError):
    """A write would replace a file not owned by this tool."""


class OutputWorkspace:
    _OWNERSHIP_FILE = ".lesson-media-owned.json"

    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=False)
        self.root.mkdir(parents=True, exist_ok=True)
        if self.root.is_symlink():
            raise UnsafeOutputPath("output root must not be a symbolic link")
        self._owned = self._load_owned()

    def _load_owned(self) -> set[str]:
        path = self.root / self._OWNERSHIP_FILE
        if not path.exists():
            return set()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise UnownedOutputError("invalid output ownership record") from None
        if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
            raise UnownedOutputError("invalid output ownership record")
        return set(data)

    @staticmethod
    def _normalize(relative_path: str) -> str:
        if not relative_path or "\x00" in relative_path:
            raise UnsafeOutputPath("generated path is empty or contains a null byte")
        windows = PureWindowsPath(relative_path)
        if windows.is_absolute() or windows.drive or windows.root:
            raise UnsafeOutputPath("generated path must be relative")
        normalized = relative_path.replace("\\", "/")
        parts = normalized.split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise UnsafeOutputPath("generated path contains an unsafe component")
        return "/".join(parts)

    def resolve_generated(self, relative_path: str) -> Path:
        normalized = self._normalize(relative_path)
        candidate = self.root.joinpath(*normalized.split("/"))
        current = self.root
        for part in normalized.split("/")[:-1]:
            current = current / part
            if current.exists() and current.is_symlink():
                raise UnsafeOutputPath("generated path crosses a symbolic link")
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(self.root)
        except ValueError:
            raise UnsafeOutputPath("generated path escapes output directory") from None
        return resolved

    def _save_owned(self) -> None:
        data = json.dumps(sorted(self._owned), ensure_ascii=False, indent=2) + "\n"
        self._atomic_replace(self.root / self._OWNERSHIP_FILE, data.encode("utf-8"))

    @staticmethod
    def _atomic_replace(destination: Path, data: bytes) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.parent / f".{destination.name}.{secrets.token_hex(8)}.tmp"
        try:
            temporary.write_bytes(data)
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()

    def write_bytes(self, relative_path: str, data: bytes, *, force: bool = False) -> Path:
        normalized = self._normalize(relative_path)
        destination = self.resolve_generated(normalized)
        if destination.exists():
            if normalized not in self._owned:
                raise UnownedOutputError(f"refusing to replace unowned output: {normalized}")
            if not force:
                raise FileExistsError(f"owned output exists; pass force to replace: {normalized}")
        self._atomic_replace(destination, data)
        self._owned.add(normalized)
        self._save_owned()
        return destination
