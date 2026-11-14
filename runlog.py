"""
The request log. Capstone (unit 9).

Every request to serve.py's /ask route writes one JSON object per line to
logs/requests.jsonl, whether it succeeded, was rejected, or crashed. One line
per request makes the file easy to read back:

    import runlog
    for record in runlog.read_records():
        print(record["status"], record["total_ms"])

Set AI201_RUN_LOG to write somewhere else, for example a separate file for
one test run.
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

import config

LOG_PATH = Path(os.getenv("AI201_RUN_LOG", str(config.ROOT / "logs" / "requests.jsonl")))

# The agent runs one request at a time, but rejected requests (400s) are
# answered outside that lock, so two writes can still overlap. A lock keeps
# each line whole.
_write_lock = threading.Lock()


def now_iso() -> str:
    """UTC timestamp with milliseconds, e.g. 2026-11-14T21:03:11.402+00:00."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def write_record(record: dict) -> None:
    """Append one record as a single JSON line."""
    line = json.dumps(record, ensure_ascii=False, default=str)
    with _write_lock:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def read_records(path: Path | None = None) -> list[dict]:
    """Every record in the log, oldest first. Lines that don't parse are skipped."""
    path = path or LOG_PATH
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records
