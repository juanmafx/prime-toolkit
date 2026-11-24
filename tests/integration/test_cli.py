import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from prime_maker import __version__
from prime_maker.cli.app import main

SOURCE = str(Path(__file__).resolve().parents[2] / "src")


def run_json(capsys, *arguments):
    code = main(["--json", *arguments])
    return code, json.loads(capsys.readouterr().out)


def test_check_prime(capsys):
    code, payload = run_json(capsys, "check", "97")
    assert code == 0
    assert payload == {"classification": "proven_prime", "number": "97"}


def test_check_composite_exits_one(capsys):
    code, payload = run_json(capsys, "check", "91")
    assert code == 1
    assert payload["classification"] == "not_prime"


def test_check_negative_number(capsys):
    code, payload = run_json(capsys, "check", "-5")
    assert code == 1
    assert payload["classification"] == "not_prime"


def test_check_large_probable_prime_with_seed(capsys):
    code, payload = run_json(capsys, "check", str(2**127 - 1), "--seed", "3")
    assert code == 0
    assert payload["classification"] == "probable_prime"


def test_list_text(capsys):
    assert main(["list", "--high", "12"]) == 0
    assert capsys.readouterr().out.split() == ["2", "3", "5", "7", "11"]


def test_list_json(capsys):
    code, payload = run_json(capsys, "list", "--low", "10", "--high", "20")
    assert code == 0
    assert payload == [11, 13, 17, 19]


def test_list_json_empty(capsys):
    code, payload = run_json(capsys, "list", "--low", "24", "--high", "29")
    assert code == 0
    assert payload == []


def test_count(capsys):
    code, payload = run_json(capsys, "count", "99")
    assert code == 0
    assert payload["prime_count"] == 25


def test_analyze(capsys):
    code, payload = run_json(capsys, "analyze", "--high", "100")
    assert code == 0
    assert payload["twin_prime_pairs"] == 8
    assert payload["residue_counts"] == {"1": 5, "3": 7, "7": 6, "9": 5}


def test_text_output_for_key_value_commands(capsys):
    assert main(["count", "10"]) == 0
    assert "prime_count: 4" in capsys.readouterr().out


def test_random_is_reproducible(capsys):
    _, first = run_json(capsys, "random", "--bits", "128", "--seed", "42")
    _, second = run_json(capsys, "random", "--bits", "128", "--seed", "42")
    assert first == second
    assert int(first["prime"]).bit_length() == 128


@pytest.mark.parametrize(
    "arguments",
    [
        ["count", "-1"],
        ["list", "--low", "-1", "--high", "5"],
        ["random", "--bits", "1"],
        ["check", "7", "--rounds", "0"],
        ["analyze", "--high", "10", "--modulus", "1"],
        ["check", str(1 << 4096)],
    ],
)
def test_invalid_values_exit_two_without_traceback(capsys, arguments):
    assert main(arguments) == 2
    assert capsys.readouterr().err.startswith("error: ")


@pytest.mark.parametrize("seed", ["-1", str(2**63)])
def test_invalid_seed_is_a_usage_error(capsys, seed):
    with pytest.raises(SystemExit) as raised:
        main(["random", "--bits", "8", f"--seed={seed}"])
    assert raised.value.code == 2
    capsys.readouterr()


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as raised:
        main(["--version"])
    assert raised.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_db_records_run(tmp_path, capsys):
    database = tmp_path / "runs.sqlite"
    assert main(["--db", str(database), "random", "--bits", "16", "--seed", "5"]) == 0
    capsys.readouterr()
    connection = sqlite3.connect(database)
    rows = connection.execute("SELECT command, seed, package_version FROM runs").fetchall()
    connection.close()
    assert rows == [("random", 5, __version__)]


def test_unwritable_db_path_reports_error(tmp_path, capsys):
    assert main(["--db", str(tmp_path / "missing" / "x.sqlite"), "count", "10"]) == 2
    assert capsys.readouterr().err.startswith("error: ")


def test_module_entry_point_survives_closed_pipe():
    environment = {**os.environ, "PYTHONPATH": SOURCE}
    process = subprocess.Popen(
        [sys.executable, "-m", "prime_maker", "list", "--high", "50000000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    assert process.stdout.readline() == b"2\n"
    process.stdout.close()
    stderr = process.stderr.read()
    process.stderr.close()
    assert process.wait(timeout=60) == 0
    assert b"Traceback" not in stderr
