"""Append-only, bounded JSONL audit log for safe agent observability."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"
_WRITE_LOCK = threading.Lock()
_SENSITIVE_KEYS = {"password", "password_hash", "token", "authorization", "api_key"}


def _safe_value(value: Any, max_length: int = 240) -> Any:
    if isinstance(value, dict):
        return {str(key): _safe_value(item) for key, item in value.items() if str(key).lower() not in _SENSITIVE_KEYS}
    if isinstance(value, (list, tuple)):
        return [_safe_value(item, 100) for item in value[:8]]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    text = str(value).replace("\n", " ")
    return text if len(text) <= max_length else text[: max_length - 1] + "…"


def audit_event(event: str, *, tool_name: str | None = None, args: Any = None, result: Any = None, stop_reason: str | None = None) -> None:
    """Append one non-sensitive, bounded event without replacing prior runs."""
    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "tool_name": tool_name,
        "args": _safe_value(args),
        "result": _safe_value(result),
        "stop_reason": stop_reason,
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _WRITE_LOCK, AUDIT_PATH.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(record, ensure_ascii=True, separators=(",", ":")) + "\n")
        audit_file.flush()
