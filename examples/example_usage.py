"""
Example usage of the Data Analysis Agent.

This script demonstrates how to use the agent to analyze CSV files.
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agent_controller import DataAnalysisAgent


def example_1_sales_analysis():
    """Example 1: Comprehensive sales data analysis."""
    print("=" * 60)
    print("EXAMPLE 1: Sales Data Analysis")
    print("=" * 60)

    # Initialize agent
    agent = DataAnalysisAgent(
        model_name="gemini/gemini-2.0-flash-exp",
        verbosity_level=1
    )

    # Run analysis
    csv_path = "examples/sample_datasets/sales_data.csv"
    result = agent.analyze(
        csv_path=csv_path,
        task="""
        Perform a comprehensive sales analysis:
        1. Show sales trends over time
        2. Compare performance across regions
        3. Analyze product performance
        4. Identify any patterns or anomalies
        5. Create relevant visualizations
        """
    )

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


def example_2_customer_analysis():
    """Example 2: Customer segmentation analysis."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Customer Data Analysis")
    print("=" * 60)

    agent = DataAnalysisAgent(
        model_name="gemini/gemini-2.0-flash-exp",
        verbosity_level=1
    )

    csv_path = "examples/sample_datasets/customer_data.csv"
    result = agent.analyze(
        csv_path=csv_path,
        task="""
        Analyze customer demographics and behavior:
        1. Show age and income distributions
        2. Analyze satisfaction scores by membership level
        3. Identify correlations between variables
        4. Compare purchase frequency patterns
        5. Create segmentation visualizations
        """
    )

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


def example_3_custom_query():
    """Example 3: Custom natural language query."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Custom Query")
    print("=" * 60)

    agent = DataAnalysisAgent(
        model_name="gemini/gemini-2.0-flash-exp",
        verbosity_level=1
    )

    csv_path = "examples/sample_datasets/sales_data.csv"
    result = agent.analyze(
        csv_path=csv_path,
        task="Show me which product generates the most revenue and create a visualization"
    )

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


def example_4_interactive_mode():
    """Example 4: Interactive mode for multiple analyses."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Interactive Mode")
    print("=" * 60)
    print("Starting interactive session...")
    print("Type 'analyze <path>' to analyze a file")
    print("Type 'quit' to exit")
    print("=" * 60)

    agent = DataAnalysisAgent(
        model_name="gemini/gemini-2.0-flash-exp",
        verbosity_level=1
    )

    agent.analyze_interactive()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run example analyses")
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4],
        help="Which example to run (1-4)"
    )

    args = parser.parse_args()

    if args.example == 1:
        example_1_sales_analysis()
    elif args.example == 2:
        example_2_customer_analysis()
    elif args.example == 3:
        example_3_custom_query()
    elif args.example == 4:
        example_4_interactive_mode()
    else:
        # Run all examples (except interactive)
        print("Running all examples...\n")
        example_1_sales_analysis()
        example_2_customer_analysis()
        example_3_custom_query()
        print("\n\nAll examples complete!")
        print("To try interactive mode, run: python examples/example_usage.py --example 4")
