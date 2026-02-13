from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PersistentMemory:
    """Persistent state backed by JSON plus append-only markdown journal."""

    root_dir: Path
    state_file: Path = field(init=False)
    journal_file: Path = field(init=False)
    _state: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.root_dir / "state.json"
        self.journal_file = self.root_dir / "journal.md"
        if not self.journal_file.exists():
            self.journal_file.write_text("# PROJECT EGO v2 Journal\n\n", encoding="utf-8")
        self.load()

    @property
    def state(self) -> dict[str, Any]:
        return dict(self._state)

    def load(self) -> dict[str, Any]:
        if not self.state_file.exists():
            self._state = {
                "created_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
                "cycle": 0,
                "last_merkle_root": "",
                "pending_replan": False,
                "mcp_config_path": str(Path.home() / ".gemini" / "antigravity" / "mcp_config.json"),
            }
            self.save(note="Memory initialized")
            return self.state
        try:
            raw = self.state_file.read_text(encoding="utf-8")
            loaded = json.loads(raw)
            if not isinstance(loaded, dict):
                raise ValueError("State JSON must be an object.")
            self._state = loaded
            return self.state
        except Exception as exc:
            LOGGER.exception("Failed to load state. Rebuilding clean state: %s", exc)
            backup_file = self.root_dir / f"state_corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                if self.state_file.exists():
                    backup_file.write_text(self.state_file.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                LOGGER.exception("Failed to create state backup.")
            self._state = {
                "created_at": _utc_now_iso(),
                "updated_at": _utc_now_iso(),
                "cycle": 0,
                "last_merkle_root": "",
                "pending_replan": True,
            }
            self.save(note="State recovered from corruption")
            return self.state

    def save(self, note: str | None = None) -> None:
        self._state["updated_at"] = _utc_now_iso()
        payload = json.dumps(self._state, indent=2, ensure_ascii=False, sort_keys=True)
        self.state_file.write_text(payload + "\n", encoding="utf-8")
        if note:
            self.append_journal(note)

    def update(self, values: dict[str, Any], note: str | None = None) -> dict[str, Any]:
        self._state.update(values)
        self.save(note=note)
        return self.state

    def append_journal(self, message: str, metadata: dict[str, Any] | None = None) -> None:
        timestamp = _utc_now_iso()
        lines = [f"## {timestamp}", "", message]
        if metadata:
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True))
            lines.append("```")
        lines.append("")
        with self.journal_file.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
