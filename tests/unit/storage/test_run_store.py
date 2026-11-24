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
