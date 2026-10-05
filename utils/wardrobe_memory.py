"""Validate and persist the wardrobe used by the FitFindr CLI."""

import json
from pathlib import Path

import config


_CATEGORIES = {"tops", "bottoms", "outerwear", "shoes", "accessories"}
_REQUIRED_FIELDS = {"id", "name", "category", "colors", "style_tags"}


def _path(memory_path: str | Path | None) -> Path:
    return Path(memory_path) if memory_path is not None else config.WARDROBE_MEMORY_PATH


def _read_wardrobe(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Wardrobe file not found: {path}") from exc
    except OSError as exc:
        raise ValueError(f"Could not read {path}: {exc.strerror}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc.msg}") from exc

    if not isinstance(value, dict) or not isinstance(value.get("items"), list):
        raise ValueError(f"{path} must contain a JSON object with an 'items' list.")

    seen_ids = set()
    for index, item in enumerate(value["items"], start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Wardrobe item {index} must be a JSON object.")

        missing = sorted(_REQUIRED_FIELDS - item.keys())
        if missing:
            raise ValueError(
                f"Wardrobe item {index} is missing: {', '.join(missing)}."
            )

        item_id = item["id"]
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"Wardrobe item {index} needs a non-empty string id.")
        if item_id in seen_ids:
            raise ValueError(f"Wardrobe item id {item_id!r} appears more than once.")
        seen_ids.add(item_id)

        if not isinstance(item["name"], str) or not item["name"].strip():
            raise ValueError(f"Wardrobe item {index} needs a non-empty string name.")
        category = item["category"]
        if not isinstance(category, str) or category not in _CATEGORIES:
            choices = ", ".join(sorted(_CATEGORIES))
            raise ValueError(
                f"Wardrobe item {index} has category {category!r}; "
                f"use one of: {choices}."
            )
        for field in ("colors", "style_tags"):
            values = item[field]
            if not isinstance(values, list) or not all(
                isinstance(value, str) for value in values
            ):
                raise ValueError(
                    f"Wardrobe item {index} field {field!r} must be a list of strings."
                )
        if item.get("notes") is not None and not isinstance(item["notes"], str):
            raise ValueError(
                f"Wardrobe item {index} field 'notes' must be a string or null."
            )

    return value


def remember_wardrobe(
    source_path: str | Path,
    memory_path: str | Path | None = None,
) -> dict:
    """Validate a wardrobe file, copy it to local memory, and return its data."""
    wardrobe = _read_wardrobe(Path(source_path))
    destination = _path(memory_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(wardrobe, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return wardrobe


def load_remembered_wardrobe(
    memory_path: str | Path | None = None,
) -> dict | None:
    """Return the remembered wardrobe, or None when no memory exists."""
    path = _path(memory_path)
    if not path.exists():
        return None
    try:
        return _read_wardrobe(path)
    except ValueError as exc:
        raise ValueError(
            f"The remembered wardrobe is unreadable. {str(exc).rstrip('.')}. "
            "Run 'python app.py wardrobe forget' to reset it, or "
            "'python app.py wardrobe remember PATH' to replace it."
        ) from exc


def forget_remembered_wardrobe(
    memory_path: str | Path | None = None,
) -> bool:
    """Delete local wardrobe memory and report whether a file was removed."""
    path = _path(memory_path)
    try:
        path.unlink()
    except FileNotFoundError:
        return False
    return True
