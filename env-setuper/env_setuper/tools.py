from typing import Any, Callable

from pydantic import BaseModel

from env_setuper.terminal import TerminalSubProcess


class Tool:
  def __init__(
    self, name: str, description: str, parameters: dict[str, Any], function: Callable, context: Any | None = None
  ) -> None:
    self.name = name
    self.description = description
    self.parameters = parameters
    self.function = function
    self.context = context

  def to_openai_format(self) -> dict[str, Any]:
    return {
      "type": "function",
      "function": {
        "name": self.name,
        "description": self.description,
        "parameters": self.parameters,
        "strict": True,
      },
    }

  def execute(self, **kwargs) -> BaseModel:
    if self.context is not None:
      return self.function(self.context, **kwargs)
    else:
      return self.function(**kwargs)


def build_terminal_tool(terminal_process: TerminalSubProcess) -> Tool:
  terminal_tool = Tool(
    name="execute_command_via_terminal_tool",
    description=(
      "Executes a shell command in a persistent, restricted shell. "
      "Commands should be generic and allow for language-agnostic steps like "
      "analyzing the repository, installing dependencies, or verifying the environment. "
      "This command must not modify the file system."
    ),
    parameters={
      "type": "object",
      "properties": {"command": {"type": "string", "description": "The shell command to execute."}},
      "required": ["command"],
      "additionalProperties": False,
    },
    function=lambda tp, command: tp.exec(command),
    context=terminal_process,
  )
  return terminal_tool
