import json
from typing import Any, Callable

from openai import OpenAI
from pydantic import BaseModel

from env_setuper.terminal import NoCallback
from env_setuper.tools import Tool


class EnvironmentResponse(BaseModel):
  task_complete: bool
  environment_details: dict | None = None
  message: str | None = None


class EnvironmentAssistant:
  def __init__(self, client: OpenAI, tools: list[Tool] = [], model: str = "gpt-4o") -> None:
    self._client = client
    self._tools = [t.to_openai_format() for t in tools]
    self._tools_dict: dict[str, Tool] = {t.name: t for t in tools}
    self.model = model

  def _log_preprocess(self, msgs: list[dict]) -> str:
    result = []
    for msg in msgs:
      tool_calls = msg.get("tool_calls")
      if tool_calls:
        for tool_call in tool_calls:
          func_args = json.loads(tool_call["function"]["arguments"])
          if func_args and func_args.get("command"):
            result.append(f"[{tool_call["id"]}]\n$: {func_args.get('command')}")
      elif msg.get("content"):
        result.append(f"[{msg.get("tool_call_id")}]\n{msg.get("content")}")
    return "\n\n".join(result)

  def _log_msgs(self, msgs: list[dict], log_callback: Callable = NoCallback, log_args: list[Any] = []) -> None:
    msgs_to_log = self._log_preprocess(msgs)
    log_args_ = log_args + [msgs_to_log]
    log_callback(*log_args_)

  def call(self, messages: list[dict], log_callback: Callable = NoCallback, log_args: list[Any] = []) -> list[dict]:
    completion = self._client.chat.completions.create(  # type: ignore
      model=self.model,
      messages=messages,
      tools=self._tools,
      response_format={
        "type": "json_schema",
        "json_schema": {
          "name": "environment_response",
          "schema": EnvironmentResponse.model_json_schema(),
        },
      },
    )

    response_message = completion.choices[0].message
    response_content = {}
    if response_message.content:
      response_content = json.loads(response_message.content)

    if response_content.get("task_complete"):
      msgs = [
        {
          "role": "assistant",
          "content": response_message.content,
        }
      ]
      self._log_msgs(msgs, log_callback, log_args)
      return msgs

    result_msgs = [response_message.model_dump(exclude_none=True)]
    self._log_msgs(result_msgs, log_callback, log_args)
    tool_calls = response_message.tool_calls
    if tool_calls:
      for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool = self._tools_dict.get(tool_name)
        if tool is not None:
          args = json.loads(tool_call.function.arguments)
          result: BaseModel = tool.execute(**args)
          result_msg = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result.model_dump_json(exclude_none=True),
          }
          result_msgs.append(result_msg)
          self._log_msgs(result_msgs, log_callback, log_args)
    return result_msgs
