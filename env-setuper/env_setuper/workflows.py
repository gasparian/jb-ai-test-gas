import json
import time
from copy import deepcopy
from typing import Any, Callable

import tiktoken
from openai import OpenAI

from env_setuper.assistants import EnvironmentAssistant
from env_setuper.prompts import SETUP_PROMPT
from env_setuper.terminal import (
  NoCallback,
  TerminalSubProcess,
)
from env_setuper.tools import build_terminal_tool


class EnvironmentSetupWorkflow:
  def __init__(
    self,
    workspace: str,
    restricted_shell: bool = True,
    openai_api_key: str | None = None,
    max_agent_iter: int = 100,
    max_agent_fails: int = 10,
    max_tokens_per_msg: int = 8192,
    shell_select_timeout_sec: float = 5,
  ) -> None:
    self._client = OpenAI(api_key=openai_api_key)
    self._terminal_process = TerminalSubProcess(
      workspace=workspace,
      restricted=restricted_shell,
      select_timeout_sec=shell_select_timeout_sec,
    )
    self._env_orig_main = deepcopy(self._terminal_process.env)
    self._terminal_tool = build_terminal_tool(self._terminal_process)
    self._environment_assistant = EnvironmentAssistant(client=self._client, tools=[self._terminal_tool])
    self._max_agent_iter = max_agent_iter
    self._max_agent_fails = max_agent_fails
    self._max_tokens_per_msg = max_tokens_per_msg
    self._stages = [
      (SETUP_PROMPT.format(tool_name=self._terminal_tool.name), "Setting up the environment"),
    ]
    self.n_steps = len(self._stages)
    self._tt_encoding = tiktoken.encoding_for_model(self._environment_assistant.model)

  def _truncate_to_token_limit(self, text, cut_head=True):
    tokens = self._tt_encoding.encode(text)
    if len(tokens) > self._max_tokens_per_msg:
      if cut_head:
        tokens = tokens[-self._max_tokens_per_msg :]
      else:
        tokens = tokens[: self._max_tokens_per_msg]
      text = self._tt_encoding.decode(tokens)
    return text

  def _trim_env_tool_answers(self, msgs: list[dict]) -> list[dict]:
    result = []
    for msg in msgs:
      if msg["role"] == "tool" and msg.get("content"):
        content: str = msg["content"]
        content_parsed = json.loads(content)
        if "stdout" in content_parsed:
          content_parsed["stdout"] = self._truncate_to_token_limit(content_parsed["stdout"])
        if "stderr" in content_parsed:
          content_parsed["stderr"] = self._truncate_to_token_limit(content_parsed["stderr"], cut_head=True)
        content = json.dumps(content_parsed)
        msg["content"] = content
      result.append(msg)
    return result

  def _run_agent_loop(
    self,
    messages: list[dict],
    log_callback: Callable = NoCallback,
    log_args: list[Any] = [],
  ) -> tuple[list[dict], dict]:
    messages_cc = deepcopy(messages)
    content = dict()
    i, fails = 0, 0
    while i < self._max_agent_iter:
      new_msgs = self._environment_assistant.call(messages_cc, log_callback, log_args)
      new_msgs = self._trim_env_tool_answers(new_msgs)
      last_message = new_msgs[-1]
      if last_message["role"] == "assistant" and not last_message.get("tool_calls"):
        content = json.loads(last_message["content"])
        task_complete = content.get("task_complete")
        task_observed_not_complete = task_complete is not None and not task_complete
        if task_complete or (task_observed_not_complete and fails >= self._max_agent_fails):
          break
        elif task_observed_not_complete:
          fails += 1
      messages_cc.extend(new_msgs)
      i += 1
    return messages_cc, content

  def _run_stage(
    self,
    step: int,
    prompt: str,
    name: str,
    messages: list[dict] = [],
    log_callback: Callable = NoCallback,
  ) -> tuple[list[dict], dict]:
    start_time = time.perf_counter()
    log_callback(step, name)
    messages_ = [
      {
        "role": "system",
        "content": prompt,
      }
    ]
    if step == 1:
      # NOTE: (@gas) jsut to help assistant with the first step
      ws_files_list_output = self._terminal_process.exec("ls -la")
      # NOTE: (@gas) jsut a small hint for the model in a very beginning
      messages_.append(
        {
          "role": "assistant",
          "content": (
            "Here an stdout with list of files in a workspace, " "produced by ls -la:\n" + ws_files_list_output.stdout
          ),
        }
      )
    messages_ += messages
    messages_, result = self._run_agent_loop(messages_, log_callback=log_callback, log_args=[step, name])
    elapsed_time = time.perf_counter() - start_time
    log_callback(step, name, result.get("message"), elapsed_time)
    return messages_, result

  def run(self, log_callback: Callable = NoCallback) -> list[dict]:
    messages: list[dict] = []
    results: list[dict] = []
    for i, stage in enumerate(self._stages):
      prompt, name = stage
      messages, result = self._run_stage(
        step=i + 1,
        prompt=prompt,
        name=name,
        messages=messages,
        log_callback=log_callback,
      )
      # NOTE: (@gas) exclude the first system message
      #       in case of multi-stage workflow
      messages = messages[1:]
      results.append(result)

    log_callback(self.n_steps, name, " > finished <")
    self._terminal_process.exit()
    return results
