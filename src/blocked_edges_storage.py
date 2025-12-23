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


def _read_entries_unlocked() -> List[Tuple[str, str]]:
    """
    Đọc file lưu trạng thái chặn theo NODE.

    Định dạng mới (ưu tiên):
        node reason

    Định dạng cũ (vẫn hỗ trợ, để tương thích):
        u v reason   -> được map thành hai node (u, reason) và (v, reason)
    """
    entries: List[Tuple[str, str]] = []
    if not STORAGE_FILE.exists():
        return entries
    with STORAGE_FILE.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            parts = raw_line.strip().split()
            if not parts:
                continue
            # Định dạng mới: node reason
            if len(parts) == 2:
                node, reason = parts
                entries.append((node, reason))
            # Định dạng cũ: u v reason -> convert sang hai node
            elif len(parts) == 3:
                u, v, reason = parts
                entries.append((u, reason))
                entries.append((v, reason))
    return entries


def _write_entries_unlocked(entries: Sequence[Tuple[str, str]]) -> None:
    with STORAGE_FILE.open("w", encoding="utf-8") as handle:
        for node, reason in entries:
            handle.write(f"{node} {reason}\n")


def load_entries() -> List[Tuple[str, str]]:
    """Trả về danh sách (node, reason) đã bị đánh dấu."""
    with _LOCK:
        _ensure_storage_file()
        return list(_read_entries_unlocked())


def load_penalties() -> Dict[str, float]:
    """
    Trả về map từ node_id -> penalty.

    Flood node: coi như không đi được (penalty = inf).
    Traffic node: áp dụng hệ số phạt cố định.
    """
    penalty: Dict[str, float] = {}
    for node, reason in load_entries():
        if reason == "flood":
            value = float("inf")
        elif reason == "traffic":
            value = TRAFFIC_PENALTY
        else:
            value = 1.0
        penalty[node] = value
    return penalty


def append_path(edges: Iterable[Tuple[str, str]], reason: str) -> None:
    """
    Lưu các tình huống theo NODE dựa trên danh sách cạnh.

    Mỗi cạnh (u, v) sẽ đánh dấu cả hai node u, v với reason tương ứng.

    The file is rewritten only when new data is actually appended to minimise I/O.
    """
    # Chuyển từ danh sách cạnh sang tập node
    nodes = {str(u) for u, v in edges} | {str(v) for u, v in edges}
    if not nodes:
        return

    with _LOCK:
        _ensure_storage_file()
        existing = set(_read_entries_unlocked())
        new_entries = {(node, reason) for node in nodes}
        if new_entries.issubset(existing):
            return
        updated = existing.union(new_entries)
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

