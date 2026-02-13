from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Tuple

_STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "profiles_store.json"
_LOCK = Lock()
_MENTION_RE = re.compile(r"@([A-Za-z0-9_-]+)")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_tag(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", raw.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "profile"


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


def create_profile(
    name: str,
    profile_type: str,
    description: str,
    attributes: Dict[str, str] | None = None,
    tag: str | None = None,
) -> Dict[str, Any]:
    profile_tag = _normalize_tag(tag or name)
    now = _utc_now()
    profile = {
        "tag": profile_tag,
        "name": name.strip(),
        "profile_type": profile_type,
        "description": description.strip(),
        "attributes": attributes or {},
        "created_at": now,
        "updated_at": now,
    }

    with _LOCK:
        items = _load_store()
        items = [p for p in items if p.get("tag") != profile_tag]
        items.append(profile)
        _write_store(items)

    return profile


def update_profile(
    tag: str,
    name: str | None = None,
    profile_type: str | None = None,
    description: str | None = None,
    attributes: Dict[str, str] | None = None,
) -> Dict[str, Any] | None:
    wanted = _normalize_tag(tag)
    with _LOCK:
        items = _load_store()
        for item in items:
            if item.get("tag") != wanted:
                continue
            if name is not None:
                item["name"] = name.strip()
            if profile_type is not None:
                item["profile_type"] = profile_type
            if description is not None:
                item["description"] = description.strip()
            if attributes is not None:
                item["attributes"] = attributes
            item["updated_at"] = _utc_now()
            _write_store(items)
            return item
    return None


def list_profiles() -> List[Dict[str, Any]]:
    with _LOCK:
        items = _load_store()
    return sorted(items, key=lambda i: i["created_at"], reverse=True)


def get_profile(tag: str) -> Dict[str, Any] | None:
    wanted = _normalize_tag(tag)
    with _LOCK:
        items = _load_store()
    for item in items:
        if item.get("tag") == wanted:
            return item
    return None


def _profile_context(profile: Dict[str, Any]) -> str:
    attrs = profile.get("attributes") or {}
    if attrs:
        attr_text = "; ".join([f"{k}: {v}" for k, v in attrs.items()])
        return (
            f"{profile['name']} is a {profile['profile_type']} profile. "
            f"{profile['description']} Attributes: {attr_text}."
        )
    return f"{profile['name']} is a {profile['profile_type']} profile. {profile['description']}"


def resolve_profiles_in_text(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    mentions = _MENTION_RE.findall(text)
    if not mentions:
        return text, []

    used_profiles: List[Dict[str, Any]] = []
    resolved_text = text

    for raw_tag in mentions:
        tag = _normalize_tag(raw_tag)
        profile = get_profile(tag)
        if profile is None:
            continue
        used_profiles.append(profile)
        resolved_text = re.sub(rf"@{re.escape(raw_tag)}\b", profile["name"], resolved_text)

    if not used_profiles:
        return text, []

    contexts = " ".join([_profile_context(profile) for profile in used_profiles])
    enriched = f"{resolved_text} Profile context: {contexts}"
    return enriched, used_profiles
