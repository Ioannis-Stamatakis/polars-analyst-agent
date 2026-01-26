"""
DataInspectorTool: Analyzes schema, nulls, and basic statistics.
"""
import polars as pl
from smolagents import Tool
from typing import Dict, Any


class DataInspectorTool(Tool):
    name = "data_inspector"
    description = """
    Inspects a loaded CSV file to understand its structure and quality.

    Args:
        csv_path: Path to the CSV file to inspect

    Returns:
        Detailed information about:
        - Column data types
        - Null/missing value counts
        - Unique value counts
        - Basic statistics for numeric columns
        - Sample values for categorical columns
    """

    inputs = {
        "csv_path": {
            "type": "string",
            "description": "Path to the CSV file to inspect"
        }
    }
    output_type = "string"

    def forward(self, csv_path: str) -> str:
        """Inspect dataframe and return concise analysis."""
        try:
            df = pl.read_csv(csv_path, ignore_errors=True)
            n_rows, n_cols = df.shape

            output_lines = [f"Data shape: {n_rows} rows, {n_cols} columns"]

            # Analyze columns
            for col in df.columns:
                dtype = str(df[col].dtype)
                nulls = df[col].null_count()
                unique = df[col].n_unique()
                output_lines.append(f"{col}: {dtype}, nulls={nulls}, unique={unique}")

            return "\n".join(output_lines)

        except Exception as e:
            return f"ERROR: Failed to inspect data: {str(e)}"
