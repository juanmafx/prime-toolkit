import os
import sqlite3
import stat
from pathlib import Path

import pytest

from prime_maker.storage.run_store import RunRecord, RunStore


def sample(command="check", parameters=None):
    return RunRecord(
        command=command,
        parameters=parameters or {"number": "7"},
        result={"classification": "proven_prime"},
        seed=11,
        package_version="2.0.0",
        started_at="2026-01-01T00:00:00+00:00",
        duration_ms=1.5,
    )


def test_round_trip(tmp_path):
    with RunStore(tmp_path / "runs.sqlite") as store:
        run_id = store.record(sample())
        assert store.fetch(run_id) == sample()


def test_missing_row_returns_none(tmp_path):
    with RunStore(tmp_path / "runs.sqlite") as store:
        assert store.fetch(404) is None


def test_file_is_owner_only(tmp_path):
    path = tmp_path / "runs.sqlite"
    RunStore(path).close()
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_refuses_symbolic_link(tmp_path):
    target = tmp_path / "target"
    target.write_text("")
    link = tmp_path / "link.sqlite"
    link.symlink_to(target)
    with pytest.raises(OSError):
        RunStore(link)


def test_refuses_named_pipe(tmp_path):
    pipe = tmp_path / "runs.fifo"
    os.mkfifo(pipe)
    with pytest.raises(ValueError, match="regular file"):
        RunStore(pipe)


def test_refuses_path_swapped_for_symbolic_link(tmp_path, monkeypatch):
    path = tmp_path / "runs.sqlite"
    target = tmp_path / "target.sqlite"
    target.write_bytes(b"")
    original_connect = sqlite3.connect

    def swap_then_connect(database):
        path.unlink()
        path.symlink_to(target)
        return original_connect(database)

    monkeypatch.setattr("prime_maker.storage.run_store.sqlite3.connect", swap_then_connect)
    with pytest.raises(ValueError, match="changed"):
        RunStore(path)
    assert target.read_bytes() == b""


def test_existing_file_mode_is_not_changed(tmp_path):
    path = tmp_path / "runs.sqlite"
    RunStore(path).close()
    path.chmod(0o640)
    RunStore(path).close()
    assert stat.S_IMODE(path.stat().st_mode) == 0o640


def test_connection_does_not_trust_database_schema(tmp_path):
    with RunStore(tmp_path / "runs.sqlite") as store:
        connection = store._connection
        assert connection.execute("PRAGMA trusted_schema").fetchone() == (0,)
        assert connection.getconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE) is True


def test_values_are_bound_not_interpolated(tmp_path):
    payload = "'); DROP TABLE runs; --"
    with RunStore(tmp_path / "runs.sqlite") as store:
        run_id = store.record(sample(parameters={"number": payload}))
        assert store.fetch(run_id).parameters["number"] == payload


def test_schema_rejects_unknown_command(tmp_path):
    with RunStore(tmp_path / "runs.sqlite") as store, pytest.raises(sqlite3.IntegrityError):
        store.record(sample(command="drop"))


def test_packaged_schema_matches_canonical_schema():
    root = Path(__file__).resolve().parents[3]
    canonical = (root / "db" / "schema.sql").read_text(encoding="utf-8")
    packaged = (root / "src/prime_maker/storage/schema.sql").read_text(encoding="utf-8")
    assert packaged == canonical
