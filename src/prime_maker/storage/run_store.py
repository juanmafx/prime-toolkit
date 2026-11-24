import json
import os
import sqlite3
import stat
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from types import TracebackType
from typing import Any, Self


@dataclass(frozen=True, slots=True)
class RunRecord:
    command: str
    parameters: dict[str, Any]
    result: dict[str, Any]
    seed: int | None
    package_version: str
    started_at: str
    duration_ms: float


def _open_regular_file(path: Path) -> int:
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags, 0o600)
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise ValueError("database path must be a regular file")
    return descriptor


def _connect(path: Path, descriptor: int) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    try:
        if not os.path.samestat(os.fstat(descriptor), os.lstat(path)):
            raise ValueError("database path changed while opening")
        connection.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE, True)
        connection.execute("PRAGMA trusted_schema = OFF")
        schema = files("prime_maker.storage").joinpath("schema.sql").read_text(encoding="utf-8")
        connection.executescript(schema)
    except BaseException:
        connection.close()
        raise
    return connection


class RunStore:
    def __init__(self, path: Path) -> None:
        descriptor = _open_regular_file(path)
        try:
            self._connection = _connect(path, descriptor)
        finally:
            os.close(descriptor)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def record(self, run: RunRecord) -> int:
        with self._connection:
            cursor = self._connection.execute(
                "INSERT INTO runs (command, parameters_json, result_json, seed, "
                "package_version, started_at, duration_ms) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    run.command,
                    json.dumps(run.parameters, sort_keys=True),
                    json.dumps(run.result, sort_keys=True),
                    run.seed,
                    run.package_version,
                    run.started_at,
                    run.duration_ms,
                ),
            )
        row_id = cursor.lastrowid
        if row_id is None:
            raise sqlite3.DatabaseError("insert did not return a row id")
        return row_id

    def fetch(self, run_id: int) -> RunRecord | None:
        row = self._connection.execute(
            "SELECT command, parameters_json, result_json, seed, package_version, "
            "started_at, duration_ms FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return RunRecord(
            command=row[0],
            parameters=json.loads(row[1]),
            result=json.loads(row[2]),
            seed=row[3],
            package_version=row[4],
            started_at=row[5],
            duration_ms=row[6],
        )
