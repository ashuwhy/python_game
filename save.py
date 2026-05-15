"""Persistent save for coins, upgrades, and best level (SQLite)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_DEFAULT: dict[str, Any] = {"coins": 0, "upgrades": {}, "best_level": 1}


def db_path() -> Path:
    return Path(__file__).resolve().parent / ".minimario_save.db"


def _legacy_json_path() -> Path:
    return Path(__file__).resolve().parent / ".minimario_save.json"


def _copy_default() -> dict[str, Any]:
    return {
        "coins": int(_DEFAULT["coins"]),
        "upgrades": dict(_DEFAULT["upgrades"]),
        "best_level": int(_DEFAULT["best_level"]),
    }


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            coins INTEGER NOT NULL DEFAULT 0,
            best_level INTEGER NOT NULL DEFAULT 1
        );
        INSERT OR IGNORE INTO game_state (id, coins, best_level) VALUES (1, 0, 1);
        CREATE TABLE IF NOT EXISTS upgrades (
            upgrade_id TEXT PRIMARY KEY,
            level INTEGER NOT NULL DEFAULT 0
        );
        """
    )


def _parse_json_save(raw: dict[str, Any]) -> dict[str, Any]:
    out = _copy_default()
    if isinstance(raw.get("coins"), int) and raw["coins"] >= 0:
        out["coins"] = raw["coins"]
    if isinstance(raw.get("upgrades"), dict):
        cleaned: dict[str, int] = {}
        for k, v in raw["upgrades"].items():
            try:
                lvl = int(v)
            except (TypeError, ValueError):
                continue
            if lvl >= 0:
                cleaned[str(k)] = lvl
        out["upgrades"] = cleaned
    if isinstance(raw.get("best_level"), int) and raw["best_level"] >= 1:
        out["best_level"] = raw["best_level"]
    return out


def _migrate_json_if_needed() -> None:
    jp = _legacy_json_path()
    dp = db_path()
    if not jp.is_file():
        return
    try:
        with open(jp, encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            return
        data = _parse_json_save(raw)
    except (OSError, json.JSONDecodeError):
        jp.unlink(missing_ok=True)
        return
    if dp.is_file():
        jp.unlink(missing_ok=True)
        return
    with sqlite3.connect(dp) as conn:
        _init_schema(conn)
        conn.execute(
            "UPDATE game_state SET coins = ?, best_level = ? WHERE id = 1",
            (data["coins"], data["best_level"]),
        )
        conn.executemany(
            "INSERT INTO upgrades (upgrade_id, level) VALUES (?, ?)",
            [(k, v) for k, v in data["upgrades"].items() if v > 0],
        )
        conn.commit()
    jp.unlink(missing_ok=True)


def load_state() -> dict[str, Any]:
    _migrate_json_if_needed()
    dp = db_path()
    if not dp.is_file():
        return _copy_default()
    out = _copy_default()
    try:
        with sqlite3.connect(dp) as conn:
            conn.row_factory = sqlite3.Row
            _init_schema(conn)
            row = conn.execute(
                "SELECT coins, best_level FROM game_state WHERE id = 1"
            ).fetchone()
            if row:
                out["coins"] = int(max(0, row["coins"]))
                out["best_level"] = int(max(1, row["best_level"]))
            up_rows = conn.execute(
                "SELECT upgrade_id, level FROM upgrades"
            ).fetchall()
            for r in up_rows:
                lvl = int(max(0, r["level"]))
                if lvl > 0:
                    out["upgrades"][str(r["upgrade_id"])] = lvl
    except sqlite3.Error:
        return _copy_default()
    return out


def save_state(state: dict[str, Any]) -> None:
    coins = int(max(0, state.get("coins", 0)))
    best_level = int(max(1, state.get("best_level", 1)))
    upgrades = {
        str(k): int(max(0, v))
        for k, v in dict(state.get("upgrades") or {}).items()
        if int(max(0, v)) > 0
    }
    dp = db_path()
    try:
        with sqlite3.connect(dp) as conn:
            _init_schema(conn)
            conn.execute(
                "UPDATE game_state SET coins = ?, best_level = ? WHERE id = 1",
                (coins, best_level),
            )
            conn.execute("DELETE FROM upgrades")
            if upgrades:
                conn.executemany(
                    "INSERT INTO upgrades (upgrade_id, level) VALUES (?, ?)",
                    list(upgrades.items()),
                )
            conn.commit()
    except sqlite3.Error:
        pass


def wipe_save_file() -> None:
    """Remove DB and any SQLite WAL/SHM sidecars."""
    d = db_path()
    for suffix in ("", "-wal", "-shm"):
        p = d if suffix == "" else Path(str(d) + suffix)
        try:
            p.unlink(missing_ok=True)
        except OSError:
            pass
    _legacy_json_path().unlink(missing_ok=True)
