"""
Agent Controller: Main orchestration of the data analysis agent.
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from smolagents import CodeAgent, LiteLLMModel, PythonInterpreterTool, tool

from src.tools.data_loader import PolarsDataLoaderTool
from src.tools.data_inspector import DataInspectorTool
from src.tools.data_profiler import DataProfilerTool
from src.prompts.system_prompts import DATA_ANALYSIS_TASK_TEMPLATE
from src.formatters.result_formatter import ResultFormatter
from src.execution.authorized_imports import AUTHORIZED_IMPORTS


class DataAnalysisAgent:
    """
    AI-powered data analysis agent using smolagents and Gemini.

    Orchestrates the workflow:
    1. Load CSV with Polars
    2. Inspect data structure
    3. Profile data characteristics
    4. Generate tailored analysis code
    5. Execute and validate code
    6. Present results
    """

    def __init__(
        self,
        model_name: str = "gemini/gemini-2.0-flash-exp",
        api_key: Optional[str] = None,
        max_steps: int = 8,
        verbosity_level: int = 1
    ):
        """
        Initialize the data analysis agent.

        Args:
            model_name: LiteLLM model identifier (default: Gemini 2.0 Flash)
            api_key: Gemini API key (reads from GEMINI_API_KEY env var if not provided)
            max_steps: Maximum agentic steps before stopping
            verbosity_level: 0=silent, 1=normal, 2=verbose
        """
        # Load environment variables
        load_dotenv()

        # Set API key
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        elif not os.getenv("GEMINI_API_KEY"):
            raise ValueError(
                "GEMINI_API_KEY not found. Either pass api_key parameter or set GEMINI_API_KEY environment variable."
            )

        # Initialize LiteLLM model
        self.model = LiteLLMModel(
            model_id=model_name,
            api_key=os.getenv("GEMINI_API_KEY")
        )

        # Initialize tools (without PythonInterpreterTool - CodeAgent creates it)
        self.tools = [
            PolarsDataLoaderTool(),
            DataInspectorTool(),
            DataProfilerTool(),
        ]

        # Initialize agent with authorized imports
        self.agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            max_steps=max_steps,
            verbosity_level=verbosity_level,
            additional_authorized_imports=AUTHORIZED_IMPORTS
        )

        # Initialize formatter
        self.formatter = ResultFormatter()

    def analyze(
        self,
        csv_path: str,
        task: str = "Perform comprehensive exploratory data analysis"
    ) -> str:
        """
        Run data analysis on a CSV file.

        Args:
            csv_path: Path to the CSV file to analyze
            task: Description of the analysis task

        Returns:
            Analysis results as a string
        """
        # Validate file exists
        if not os.path.exists(csv_path):
            error_msg = f"File not found: {csv_path}"
            self.formatter.print_error(error_msg)
            return error_msg

        # Format the task
        full_task = DATA_ANALYSIS_TASK_TEMPLATE.format(
            csv_path=csv_path,
            task_description=task
        )

        # Print start message
        self.formatter.print_step(
            "Starting Analysis",
            f"File: {csv_path}\nTask: {task}"
        )

        try:
            # Run the agent
            result = self.agent.run(full_task)

            # Format and display result
            self.formatter.format_agent_result(result)

            return result

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.formatter.print_error(error_msg)
            return error_msg

    def analyze_interactive(self):
        """
        Interactive CLI mode for analyzing multiple files.
        """
        self.formatter.console.print(
            Panel(
                "[bold cyan]Data Analysis Agent[/bold cyan]\n"
                "Powered by smolagents + Gemini\n\n"
                "Commands:\n"
                "  analyze <path> - Analyze a CSV file\n"
                "  quit - Exit",
                border_style="cyan"
            )
        )

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    self.formatter.console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.startswith("analyze "):
                    csv_path = user_input[8:].strip()
                    if csv_path.startswith('"') and csv_path.endswith('"'):
                        csv_path = csv_path[1:-1]
                    elif csv_path.startswith("'") and csv_path.endswith("'"):
                        csv_path = csv_path[1:-1]

                    self.analyze(csv_path)
                else:
                    self.formatter.console.print(
                        "[yellow]Unknown command. Try 'analyze <path>' or 'quit'[/yellow]"
                    )

            except KeyboardInterrupt:
                self.formatter.console.print("\n[yellow]Interrupted. Use 'quit' to exit.[/yellow]")
            except Exception as e:
                self.formatter.print_error(str(e))


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-powered data analysis agent using smolagents and Gemini"
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        help="Path to CSV file to analyze"
    )
    parser.add_argument(
        "--task",
        default="Perform comprehensive exploratory data analysis",
        help="Analysis task description"
    )
    parser.add_argument(
        "--model",
        default="gemini/gemini-2.0-flash-exp",
        help="LiteLLM model identifier"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
        help="Maximum agentic steps"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )

    args = parser.parse_args()

    # Initialize agent
    agent = DataAnalysisAgent(
        model_name=args.model,
        max_steps=args.max_steps,
        verbosity_level=2 if args.verbose else 1
    )

    # Run analysis
    if args.interactive or not args.csv_path:
        agent.analyze_interactive()
    else:
        agent.analyze(args.csv_path, args.task)


if __name__ == "__main__":
    main()
