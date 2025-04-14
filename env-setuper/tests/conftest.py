import pytest

from env_setuper.terminal import TerminalSubProcess


@pytest.fixture
def terminal(tmp_path):
  workspace = tmp_path / "workspace"
  workspace.mkdir()
  terminal = TerminalSubProcess(str(workspace), select_timeout_sec=1)
  yield terminal
  terminal.exit()
