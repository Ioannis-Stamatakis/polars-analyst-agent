"""
Result formatting utilities.
"""
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from typing import Dict, Any


class ResultFormatter:
    """Formats agent results for CLI output."""

    def __init__(self):
        self.console = Console()

    def format_agent_result(self, result: Any) -> None:
        """Format and display agent execution result."""
        self.console.print("\n")
        self.console.print(Panel(
            "[bold green]Analysis Complete[/bold green]",
            border_style="green"
        ))

        if isinstance(result, str):
            self.console.print(result)
        elif isinstance(result, dict):
            self._format_dict_result(result)
        else:
            self.console.print(str(result))

    def _format_dict_result(self, result: Dict[str, Any]) -> None:
        """Format dictionary results."""
        for key, value in result.items():
            if key == "code" and isinstance(value, str):
                self.console.print("\n[bold cyan]Generated Code:[/bold cyan]")
                syntax = Syntax(value, "python", theme="monokai", line_numbers=True)
                self.console.print(syntax)
            elif key == "visualizations" and isinstance(value, list):
                self.console.print("\n[bold cyan]Visualizations:[/bold cyan]")
                for viz in value:
                    self.console.print(f"  📊 {viz}")
            elif key == "insights" and isinstance(value, list):
                self.console.print("\n[bold cyan]Insights:[/bold cyan]")
                for insight in value:
                    self.console.print(f"  • {insight}")
            else:
                self.console.print(f"\n[bold]{key}:[/bold] {value}")

    def print_step(self, step_name: str, description: str = "") -> None:
        """Print a workflow step."""
        self.console.print(f"\n[bold blue]→ {step_name}[/bold blue]")
        if description:
            self.console.print(f"  {description}")

    def print_error(self, error_msg: str) -> None:
        """Print an error message."""
        self.console.print(Panel(
            f"[bold red]Error:[/bold red] {error_msg}",
            border_style="red"
        ))

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[green]✓[/green] {message}")
