from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any


CURRENT_DIR = Path(__file__).resolve().parent
AI_ROOT = CURRENT_DIR.parent
SENSORY_DIR = AI_ROOT / "sensory"
if str(SENSORY_DIR) not in sys.path:
    sys.path.insert(0, str(SENSORY_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from memory import PersistentMemory  # type: ignore  # noqa: E402
from merkle_audit import AuditSnapshot, MerkleProjectAuditor  # type: ignore  # noqa: E402
from neuro_client import NeuroMCPClient  # type: ignore  # noqa: E402


def setup_logging() -> None:
    log_dir = AI_ROOT / "data"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "ego.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


class OODALoop:
    def __init__(self, project_root: Path, sleep_sec: float = 4.0) -> None:
        self.project_root = project_root
        self.sleep_sec = sleep_sec
        self.logger = logging.getLogger(self.__class__.__name__)
        self.memory = PersistentMemory(AI_ROOT / "data")
        self.auditor = MerkleProjectAuditor(project_root)
        self.neuro_client = self._build_neuro_client()

    def _build_neuro_client(self) -> NeuroMCPClient | None:
        cfg = self.memory.state.get("mcp_config_path")
        try:
            return NeuroMCPClient(config_path=str(cfg) if cfg else None)
        except Exception as exc:
            self.logger.warning("NeuroMCP unavailable: %s", exc)
            self.memory.append_journal("NeuroMCP unavailable", {"error": str(exc)})
            return None

    def run_forever(self) -> None:
        self.logger.info("PROJECT EGO v2 started. OODA loop active.")
        max_cycles = int(os.getenv("PROJECT_EGO_MAX_CYCLES", "0") or "0")
        runtime_cycles = 0
        while True:
            try:
                self._cycle()
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user. Stopping.")
                break
            except Exception as exc:
                self.logger.exception("Unhandled cycle exception: %s", exc)
                self.memory.append_journal("Cycle exception", {"error": str(exc)})
            runtime_cycles += 1
            if max_cycles and runtime_cycles >= max_cycles:
                self.logger.info("Max cycles reached (%s). Stopping.", max_cycles)
                break
            time.sleep(self.sleep_sec)

    def _load_previous_snapshot(self) -> AuditSnapshot | None:
        last = self.memory.state.get("last_snapshot")
        if not isinstance(last, dict):
            return None
        hashes = last.get("file_hashes")
        root = last.get("merkle_root")
        if isinstance(root, str) and isinstance(hashes, dict):
            cast_hashes = {str(k): str(v) for k, v in hashes.items()}
            return AuditSnapshot(merkle_root=root, file_hashes=cast_hashes)
        return None

    def _cycle(self) -> None:
        state = self.memory.state
        cycle_number = int(state.get("cycle", 0)) + 1

        # Observe
        previous = self._load_previous_snapshot()
        snapshot, changed = self.auditor.detect_changes(previous)
        observe_data: dict[str, Any] = {
            "cycle": cycle_number,
            "changed_files": changed[:200],
            "merkle_root": snapshot.merkle_root,
            "change_count": len(changed),
        }

        # Orient
        replan_needed = bool(changed) and cycle_number > 1
        orient_data: dict[str, Any] = {
            "pending_replan": replan_needed,
            "reason": "filesystem-drift-detected" if replan_needed else "stable",
        }

        # Decide
        decision = "re-evaluate-plan" if replan_needed else "continue-monitoring"
        decision_data: dict[str, Any] = {"decision": decision}

        # Act
        act_data: dict[str, Any] = {}
        if replan_needed:
            self.memory.append_journal("Detected atomic file changes. Plan re-evaluation triggered.", observe_data)
        if self.neuro_client is not None and cycle_number % 10 == 0:
            try:
                act_data["neurovision_ping"] = self.neuro_client.list_files(".")
            except Exception as exc:
                act_data["neurovision_error"] = str(exc)
                self.logger.warning("NeuroVision call failed: %s", exc)

        self.memory.update(
            {
                "cycle": cycle_number,
                "pending_replan": replan_needed,
                "last_merkle_root": snapshot.merkle_root,
                "last_snapshot": {"merkle_root": snapshot.merkle_root, "file_hashes": snapshot.file_hashes},
                "last_ooda": {
                    "observe": observe_data,
                    "orient": orient_data,
                    "decide": decision_data,
                    "act": act_data,
                },
            },
            note=f"OODA cycle {cycle_number}: {decision}",
        )
        self.logger.info("Cycle %s complete. changed=%s decision=%s", cycle_number, len(changed), decision)


def main() -> None:
    setup_logging()
    root = AI_ROOT.parent
    OODALoop(project_root=root).run_forever()


if __name__ == "__main__":
    main()
