import json
import tomllib
from pathlib import Path

import prime_maker

ROOT = Path(__file__).resolve().parents[2]


def test_versions_are_synchronized():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package = json.loads((ROOT / "javascript/package.json").read_text(encoding="utf-8"))
    assert project["project"]["version"] == prime_maker.__version__
    assert package["version"] == prime_maker.__version__
