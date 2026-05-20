"""Shared ingest utilities: snapshot management, SHA256, provenance metadata."""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path


def snapshot_dir(base: Path, source: str, snapshot_date: str | None = None) -> Path:
    today = snapshot_date or date.today().isoformat()
    d = base / "data" / "raw" / source / today
    d.mkdir(parents=True, exist_ok=True)
    return d


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_meta(directory: Path, source: str, files: list[dict]) -> None:
    meta = {
        "source": source,
        "snapshot_date": directory.name,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "0.1.0",
        "files": files,
    }
    (directory / "meta.json").write_text(json.dumps(meta, indent=2))
