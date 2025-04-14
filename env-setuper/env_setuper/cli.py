import datetime
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from env_setuper.workflows import EnvironmentSetupWorkflow

app = typer.Typer()
console = Console()


def create_visualization(step: int, total: int, name: str, message: str, start_time: float, *args, **kwargs):
  progress_percent = (step / total) * 100
  elapsed = time.perf_counter() - start_time
  elapsed_td = datetime.timedelta(seconds=elapsed)
  total_seconds = int(elapsed_td.total_seconds())
  milliseconds = int(elapsed_td.microseconds / 1000)
  elapsed_str = (
    f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}.{milliseconds:03d}"
  )
  status_text = Text(
    f"Step {step}/{total}: {name}\n\n{message}\n\nProgress: {progress_percent:.1f}%\nElapsed time: {elapsed_str}",
    style="bold cyan",
  )
  start_index = status_text.plain.find(message)
  end_index = start_index + len(message)
  status_text.stylize("yellow", start_index, end_index)
  return Panel(status_text, title="live log", border_style="green")


@app.command()
def setup_workflow(
  workspace: str = typer.Argument(..., help="Path to the folder to list contents"),
  restricted_shell: bool = typer.Option(
    True, "--restricted-shell/--no-restricted-shell", help="Enable or disable restricted shell"
  ),
  max_agent_iter: int = typer.Option(30, "--max-agent-iter", help="Maximum agent iterations"),
  max_agent_fails: int | None = typer.Option(None, "--max-agent-fails", help="Maximum agent failures"),
  max_tokens_per_msg: int = typer.Option(8192, "--max-tokens-per-msg", help="Maximum tokens per message"),
  shell_select_timeout_sec: float = typer.Option(
    1, "--shell-select-timeout-sec", help="Shell wait timeout to capture the output"
  ),
  openai_api_key: str | None = typer.Option(None, "--openai-api-key", help="OpenAI API key"),
):
  workspace_abs = str(Path(workspace).absolute())
  workflow = EnvironmentSetupWorkflow(
    workspace=workspace_abs,
    restricted_shell=restricted_shell,
    max_agent_iter=max_agent_iter,
    max_agent_fails=max_agent_fails or max_agent_iter,
    max_tokens_per_msg=max_tokens_per_msg,
    shell_select_timeout_sec=shell_select_timeout_sec,
  )
  steps = workflow.n_steps

  start_time = time.perf_counter()
  with Live(console=console, refresh_per_second=5) as live:
    console.print(f"\nSetting up project at `{workspace}`\n", style="bold green")

    def visualize(step: int, name: str, message: str = "", *args, **kwargs) -> None:
      visualization = create_visualization(step, steps, name, message, start_time)
      live.update(visualization)

    results = workflow.run(log_callback=visualize)

  if results:
    final_result = results[-1]
    final_message = final_result.get("message")
    if final_message:
      is_complete = final_result.get("task_complete")
      if is_complete:
        console.print("\n--- Summary [Success] ---\n", style="bold green", justify="center")
      else:
        console.print("\n--- Summary [Warning] ---\n", style="yellow", justify="center")
      console.print(Markdown(final_message))
      console.print("\n///", style="bold green", justify="center")
  else:
    console.print("\n--- [Error] Smth went wrong ---\n", style="red", justify="center")


if __name__ == "__main__":
  app()
