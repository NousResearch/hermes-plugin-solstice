"""Test bootstrap: import Hermes from a hermes-agent checkout and load THIS repo's plugin.

The checkout is chosen in this order:

1. ``HERMES_AGENT_REPO`` when set;
2. the current directory when it is a hermes-agent checkout (``scripts/run_tests.sh`` clears the
   environment, so the README recipe relies on this);
3. ``~/.hermes/hermes-agent`` (the installed agent).

Hermes releases up to 0.22.x still bundle a copy of this plugin. Every test therefore installs this
repo into its temporary ``$HERMES_HOME`` (``solstice_home``) so the profile under test is this repo's,
registered the way ``hermes plugins install`` would leave it, and asserts that it won.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def _hermes_agent_repo() -> Path:
    explicit = os.environ.get("HERMES_AGENT_REPO")
    if explicit:
        return Path(explicit).expanduser()
    cwd = Path.cwd()
    if (cwd / "providers" / "__init__.py").is_file() and (cwd / "hermes_cli").is_dir():
        return cwd
    return Path.home() / ".hermes" / "hermes-agent"


_hermes_agent = str(_hermes_agent_repo())
if _hermes_agent not in sys.path:
    sys.path.insert(0, _hermes_agent)

@pytest.fixture
def solstice_home(tmp_path, monkeypatch):
    """A fresh ``$HERMES_HOME`` with this repo installed at ``plugins/solstice`` (as a symlink)."""
    home = tmp_path / "hermes"
    (home / "plugins").mkdir(parents=True)
    (home / "plugins" / "solstice").symlink_to(PLUGIN_ROOT, target_is_directory=True)
    monkeypatch.setenv("HERMES_HOME", str(home))
    return home
