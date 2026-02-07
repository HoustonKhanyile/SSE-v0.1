from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import uuid4


_STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "tracking_store.json"
_LOCK = Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_store() -> List[Dict[str, Any]]:
    if not _STORE_PATH.exists():
        return []
    raw = _STORE_PATH.read_text(encoding="ascii")
    if not raw.strip():
        return []
    return json.loads(raw)


def _write_store(items: List[Dict[str, Any]]) -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(items, indent=2), encoding="ascii")


def create_tracking_item(
    situation: str,
    prediction: Dict[str, Any],
    started_at: Optional[str] = None,
    expected_at: Optional[str] = None,
) -> Dict[str, Any]:
    item = {
        "id": str(uuid4()),
        "situation": situation,
        "prediction": prediction,
        "started_at": started_at or _utc_now(),
        "expected_at": expected_at,
        "actual_at": None,
        "vote": None,
        "actual_outcome": None,
        "status": "tracking",
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }

    with _LOCK:
        items = _load_store()
        items.append(item)
        _write_store(items)

    return item


def ensure_dummy_tracking_item() -> None:
    with _LOCK:
        items = _load_store()
        if items:
            return

        dummy = {
            "id": "dummy-tracking-item-001",
            "situation": "An employee expects a promotion decision by month-end after repeated high performance.",
            "prediction": {
                "mode": "B",
                "horizon": "days",
                "predicted_outcome": {
                    "id": "quiet_job_search",
                    "label": "The employee quietly searches for another job while maintaining performance.",
                    "confidence": 0.68,
                    "rationale": ["career preservation", "avoid open conflict"],
                },
                "explanation": "The employee quietly searches for another job while maintaining performance. This outcome is most likely given the constraints and priors in the situation.",
            },
            "started_at": "2026-02-01T09:00:00+00:00",
            "expected_at": "2026-02-28T17:00:00+00:00",
            "actual_at": None,
            "vote": None,
            "actual_outcome": None,
            "status": "tracking",
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
        }
        items.append(dummy)
        _write_store(items)


def list_tracking_items() -> List[Dict[str, Any]]:
    with _LOCK:
        items = _load_store()
    return sorted(items, key=lambda i: i["created_at"], reverse=True)


def get_tracking_item(item_id: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        items = _load_store()
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def vote_tracking_item(
    item_id: str,
    vote: str,
    actual_outcome: Optional[str] = None,
    actual_at: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    with _LOCK:
        items = _load_store()
        for item in items:
            if item["id"] != item_id:
                continue

            item["vote"] = vote
            item["actual_outcome"] = actual_outcome if vote == "inaccurate" else None
            item["actual_at"] = actual_at or _utc_now()
            item["status"] = "resolved"
            item["updated_at"] = _utc_now()
            _write_store(items)
            return item

    return None
