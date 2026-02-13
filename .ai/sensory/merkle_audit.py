from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuditSnapshot:
    merkle_root: str
    file_hashes: dict[str, str]


class MerkleProjectAuditor:
    """Builds project Merkle root and detects bit-level file changes."""

    def __init__(self, root: Path, ignore_dirs: Iterable[str] | None = None) -> None:
        self.root = root.resolve()
        self.ignore_dirs = set(
            ignore_dirs
            or {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".hypothesis", ".ruff_cache"}
        )

    def snapshot(self) -> AuditSnapshot:
        file_hashes: dict[str, str] = {}
        for file_path in self._iter_files():
            rel = file_path.relative_to(self.root).as_posix()
            try:
                file_hashes[rel] = self._sha256_file(file_path)
            except PermissionError:
                LOGGER.debug("Skipping unreadable file: %s", file_path)
            except OSError:
                LOGGER.debug("Skipping file with OS error: %s", file_path, exc_info=True)
        return AuditSnapshot(merkle_root=self._build_merkle_root(file_hashes), file_hashes=file_hashes)

    def detect_changes(self, previous: AuditSnapshot | None) -> tuple[AuditSnapshot, list[str]]:
        current = self.snapshot()
        if previous is None:
            return current, sorted(current.file_hashes.keys())
        changed: list[str] = []
        all_paths = set(previous.file_hashes) | set(current.file_hashes)
        for path in sorted(all_paths):
            if previous.file_hashes.get(path) != current.file_hashes.get(path):
                changed.append(path)
        return current, changed

    def _iter_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(self.root).parts
            if any(part in self.ignore_dirs for part in rel_parts):
                continue
            yield path

    @staticmethod
    def _sha256_file(file_path: Path) -> str:
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            while True:
                block = handle.read(1024 * 1024)
                if not block:
                    break
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _build_merkle_root(file_hashes: dict[str, str]) -> str:
        if not file_hashes:
            return hashlib.sha256(b"").hexdigest()
        leaves = [hashlib.sha256(f"{k}:{v}".encode("utf-8")).digest() for k, v in sorted(file_hashes.items())]
        level = leaves
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])
            next_level: list[bytes] = []
            for idx in range(0, len(level), 2):
                next_level.append(hashlib.sha256(level[idx] + level[idx + 1]).digest())
            level = next_level
        return level[0].hex()
