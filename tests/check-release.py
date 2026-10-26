#!/usr/bin/env python3
"""Check release archives against the documentation links Universe validates."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import re
import runpy
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
release = runpy.run_path(str(ROOT / "scripts/release.py"))
with tempfile.TemporaryDirectory() as directory:
    package = Path(directory) / "package"
    with redirect_stdout(io.StringIO()):
        release["bundle"](str(package))
    # These are excluded from compiler imports, but must be committed in Universe.
    for path in ("docs/reference.md", "docs/html-semantics.md", "CONTRIBUTING.md"):
        assert (package / path).is_file(), f"missing linked documentation: {path}"
    assert not (package / "tests").exists()
    assert not (package / ".github").exists()
    for markdown in package.rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", markdown.read_text()):
            if re.match(r"[a-z]+:", link) or link.startswith("#"):
                continue
            target = link.split("#")[0]
            assert (markdown.parent / target).is_file(), f"{markdown.name}: missing {target}"

manifest = tomllib.loads((ROOT / "typst.toml").read_text())["package"]
assert "typst" not in manifest["description"].lower()
readme = (ROOT / "README.md").read_text()
assert '#import "lib.typ"' not in readme
assert f'@preview/{manifest["name"]}:{manifest["version"]}' in readme
print("PASS: release archive includes linked documentation; README and manifest follow package checks")
