from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List
from uuid import uuid4


_STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "queries_store.json"
_LOCK = Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_store() -> List[Dict[str, Any]]:
    if not _STORE_PATH.exists():
        return []
    raw = _STORE_PATH.read_text(encoding="utf-8")
    if not raw.strip():
        return []
    return json.loads(raw)


def _write_store(items: List[Dict[str, Any]]) -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")


def create_query_item(
    situation: str,
    query_mode: str,
    prediction: Dict[str, Any],
) -> Dict[str, Any]:
    now = _utc_now()
    item = {
        "id": str(uuid4()),
        "situation": situation.strip(),
        "query_mode": (query_mode or "general").strip().lower(),
        "prediction": prediction,
        "reflection": None,
        "created_at": now,
        "updated_at": now,
    }

    with _LOCK:
        items = _load_store()
        items.append(item)
        _write_store(items)

    return item


def list_query_items() -> List[Dict[str, Any]]:
    with _LOCK:
        items = _load_store()
    return sorted(items, key=lambda i: i["created_at"], reverse=True)


def get_query_item(item_id: str) -> Dict[str, Any] | None:
    with _LOCK:
        items = _load_store()
    for item in items:
        if item.get("id") == item_id:
            return item
    return None


def search_query_items(search_text: str) -> List[Dict[str, Any]]:
    q = (search_text or "").strip().lower()
    if not q:
        return list_query_items()

    items = list_query_items()
    results: List[Dict[str, Any]] = []
    for item in items:
        situation = str(item.get("situation") or "").lower()
        mode = str(item.get("query_mode") or "").lower()
        outcome = str(item.get("prediction", {}).get("predicted_outcome", {}).get("label") or "").lower()
        posture = " ".join(item.get("prediction", {}).get("daily_use", {}).get("recommended_posture", [])).lower()
        if q in situation or q in mode or q in outcome or q in posture:
            results.append(item)
    return results


def reflect_query_item(item_id: str, reflection: Dict[str, Any]) -> Dict[str, Any] | None:
    with _LOCK:
        items = _load_store()
        for item in items:
            if item.get("id") != item_id:
                continue
            item["reflection"] = reflection
            item["updated_at"] = _utc_now()
            _write_store(items)
            return item
    return None
