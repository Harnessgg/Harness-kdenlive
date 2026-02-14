import json
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from harness_kdenlive.core.xml_engine import KdenliveProject


class TransactionManager:
    def __init__(self, project: KdenliveProject, enable_auto_backup: bool = True):
        self.project = project
        self.enable_auto_backup = enable_auto_backup
        self._transaction_stack: List[str] = []
        self._history_dir = project.project_path.parent / ".kdenlive_history"
        self._backup_dir = project.project_path.parent / ".kdenlive_backups"
        self._history_dir.mkdir(exist_ok=True)
        self._backup_dir.mkdir(exist_ok=True)
        self._metadata_file = self._history_dir / "snapshots.json"
        self._snapshots: List[Dict[str, Any]] = self._load_snapshot_metadata()

    def _load_snapshot_metadata(self) -> List[Dict[str, Any]]:
        if not self._metadata_file.exists():
            return []
        return json.loads(self._metadata_file.read_text(encoding="utf-8"))

    def _save_snapshot_metadata(self) -> None:
        self._metadata_file.write_text(json.dumps(self._snapshots, indent=2), encoding="utf-8")

    def begin_transaction(self) -> None:
        self._transaction_stack.append(self.project.to_string())

    def commit(self) -> None:
        if not self._transaction_stack:
            raise RuntimeError("No active transaction")
        self._transaction_stack.clear()

    def rollback(self) -> None:
        if not self._transaction_stack:
            raise RuntimeError("No active transaction")
        xml = self._transaction_stack[0]
        self.project.load_from_string(xml)
        self._transaction_stack.clear()

    @contextmanager
    def transaction(self, description: str = "Transaction", create_snapshot: bool = False):
        self.begin_transaction()
        try:
            yield self
            self.commit()
            if create_snapshot:
                self.create_snapshot(description)
        except Exception:
            self.rollback()
            raise

    def create_backup(self, label: Optional[str] = None) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = self.project.project_path.stem
        name = f"{stem}_{label}_{timestamp}.kdenlive" if label else f"{stem}_backup_{timestamp}.kdenlive"
        destination = self._backup_dir / name
        shutil.copy2(self.project.project_path, destination)
        return destination

    def create_snapshot(self, description: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        timestamp = datetime.now()
        snapshot_id = f"snapshot_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        snapshot_file = self._history_dir / f"{snapshot_id}.kdenlive"
        snapshot_file.write_text(self.project.to_string(), encoding="utf-8")
        self._snapshots.append(
            {
                "id": snapshot_id,
                "timestamp": timestamp.isoformat(),
                "description": description,
                "metadata": metadata or {},
                "file": str(snapshot_file),
            }
        )
        self._save_snapshot_metadata()
        return snapshot_id

    def load_snapshot(self, snapshot_id: str) -> KdenliveProject:
        snap = next((s for s in self._snapshots if s["id"] == snapshot_id), None)
        if snap is None:
            raise ValueError(f"Snapshot '{snapshot_id}' not found")
        return KdenliveProject(snap["file"])

    def rollback_to_snapshot(self, snapshot_id: str) -> None:
        if self.enable_auto_backup:
            self.create_backup(label=f"before_rollback_{snapshot_id}")
        snapshot_project = self.load_snapshot(snapshot_id)
        self.project.tree = snapshot_project.tree
        self.project.root = snapshot_project.root

    def get_history(self) -> List[Dict[str, Any]]:
        return sorted(self._snapshots, key=lambda s: s["timestamp"], reverse=True)
