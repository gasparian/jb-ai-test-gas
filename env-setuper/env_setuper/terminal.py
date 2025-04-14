import atexit
import os
import select
import subprocess
from copy import deepcopy

from pydantic import BaseModel


def NoCallback(*args, **kwrags):
  return None


class ShellOutput(BaseModel):
  stdout: str
  stderr: str
  returncode: int | None


class TerminalSubProcess:
  def __init__(
    self,
    workspace: str,
    restricted: bool = True,
    select_timeout_sec: float = 1,
    exit_timeout_sec: float = 5,
  ):
    self.workspace = workspace
    self._select_timeout_sec = select_timeout_sec
    self._exit_timeout_sec = exit_timeout_sec
    shell_command = ["/bin/bash"]
    if restricted:
      shell_command.append("--restricted")
    env = os.environ.copy()
    self.env = deepcopy(env)
    env["PWD"] = workspace
    self._process = subprocess.Popen(
      shell_command,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      cwd=workspace,
      env=env,
      text=True,
      universal_newlines=True,
      bufsize=1,
    )
    atexit.register(lambda: self._process.terminate())

  def exec(self, command: str) -> ShellOutput:
    # NOTE: (@gas) small sanity check, to avoid crushing source
    if command.startswith(("souce", ".")):
      full_command = f"{command}; stdbuf -oL -eL echo SENTINEL $?\n"
    else:
      full_command = f"stdbuf -oL -eL {command}; echo .; stdbuf -oL -eL echo SENTINEL $?\n"
    if self._process.stdin is None:
      raise Exception("Failed to exec the command: process stdin not accesable")
    self._process.stdin.write(full_command)
    self._process.stdin.flush()
    stdout, stderr = "", ""
    returncode = None
    while True:
      readable, _, _ = select.select([self._process.stdout, self._process.stderr], [], [], self._select_timeout_sec)
      for pipe in readable:
        line = pipe.readline()
        if not line:  # EOF
          return ShellOutput(stdout=stdout, stderr=stderr, returncode=returncode)
        if line.startswith("SENTINEL"):
          parts = line.strip().split()
          if len(parts) == 2 and parts[0] == "SENTINEL":
            returncode = int(parts[1])
            return ShellOutput(stdout=stdout, stderr=stderr, returncode=returncode)
        if pipe == self._process.stdout:
          stdout += line
        else:
          stderr += line

  def exit(self):
    try:
      self._process.stdin.write("exit\n")
      self._process.stdin.flush()
      self._process.wait(self._exit_timeout_sec)
    except subprocess.TimeoutExpired:
      pass


def parse_printenv(result: str) -> dict[str, str]:
  env_dict = {}
  for line in result.strip().split("\n"):
    if not line:
      continue
    if "=" in line:
      key, value = line.split("=", 1)
      env_dict[key.strip()] = value.strip()
  return env_dict


def env_dict_to_txt(env_dict: dict[str, str]) -> str:
  lines = [f"{key}={value}" for key, value in env_dict.items()]
  return "\n".join(lines)


def get_dicts_diff(src: dict, dst: dict) -> dict:
  keys_in_dst_only = set(dst.keys()) - set(src.keys())
  return {k: v for k, v in dst.items() if k in keys_in_dst_only}
