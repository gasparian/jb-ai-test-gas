import time

from env_setuper.terminal import ShellOutput


def test_simple_command(terminal):
  """Test a simple command with immediate output."""
  output: ShellOutput = terminal.exec('echo "Hello"')
  assert output.stdout.strip() == "Hello\n."
  assert output.stderr == ""
  assert output.returncode == 0


def test_delayed_output(terminal):
  """Test a command with a delay before producing output."""
  start_time = time.time()
  output: ShellOutput = terminal.exec("sleep 3")
  output: ShellOutput = terminal.exec('echo "Hello after 3 seconds"')
  end_time = time.time()
  assert output.stdout.strip() == "Hello after 3 seconds\n."
  assert output.stderr == ""
  assert output.returncode == 0
  assert end_time - start_time >= 3, "Method did not wait for the command to complete"
