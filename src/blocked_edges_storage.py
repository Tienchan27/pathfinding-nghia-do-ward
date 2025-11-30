from __future__ import annotations

import os
from pathlib import Path
from threading import Lock
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
STORAGE_FILE = DATA_DIR / "blocked_edges.txt"
TRAFFIC_PENALTY = 5.0

_LOCK = Lock()


def _ensure_storage_file() -> None:
    """Guarantee that the storage file exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STORAGE_FILE.exists():
        STORAGE_FILE.touch()


def _read_entries_unlocked() -> List[Tuple[str, str, str]]:
    entries: List[Tuple[str, str, str]] = []
    if not STORAGE_FILE.exists():
        return entries
    with STORAGE_FILE.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            parts = raw_line.strip().split()
            if len(parts) != 3:
                continue
            entries.append((parts[0], parts[1], parts[2]))
    return entries


def _write_entries_unlocked(entries: Sequence[Tuple[str, str, str]]) -> None:
    with STORAGE_FILE.open("w", encoding="utf-8") as handle:
        for u, v, reason in entries:
            handle.write(f"{u} {v} {reason}\n")


def load_entries() -> List[Tuple[str, str, str]]:
    """Return all blocked edges as (source, target, reason)."""
    with _LOCK:
        _ensure_storage_file()
        return list(_read_entries_unlocked())


def load_penalties() -> Dict[Tuple[str, str], float]:
    """
    Return a mapping of directed edges to penalty multipliers.

    Flood edges are treated as impassable (infinite penalty) and traffic edges receive a fixed slowdown.
    """
    penalty: Dict[Tuple[str, str], float] = {}
    for source, target, reason in load_entries():
        if reason == "flood":
            value = float("inf")
        elif reason == "traffic":
            value = TRAFFIC_PENALTY
        else:
            value = 1.0
        penalty[(source, target)] = value
        penalty[(target, source)] = value
    return penalty


def append_path(edges: Iterable[Tuple[str, str]], reason: str) -> None:
    """
    Persist a set of directed edges with the provided reason.

    The file is rewritten only when new data is actually appended to minimise I/O.
    """
    normalized = {(str(u), str(v), reason) for u, v in edges}
    if not normalized:
        return

    with _LOCK:
        _ensure_storage_file()
        existing_set = set(_read_entries_unlocked())
        if normalized.issubset(existing_set):
            return
        updated = existing_set.union(normalized)
        _write_entries_unlocked(sorted(updated))


def reset_storage() -> None:
    """Clear the storage file."""
    with _LOCK:
        _ensure_storage_file()
        STORAGE_FILE.write_text("", encoding="utf-8")


def storage_path() -> Path:
    """Expose the absolute path for the current storage file."""
    _ensure_storage_file()
    return STORAGE_FILE

