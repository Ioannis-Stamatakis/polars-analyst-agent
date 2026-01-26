"""
PolarsDataLoaderTool: Robust CSV loading with error handling and auto-detection.
"""
import polars as pl
from smolagents import Tool
from typing import Dict, Any
import os


class PolarsDataLoaderTool(Tool):
    name = "polars_data_loader"
    description = """
    Loads a CSV file using Polars with robust error handling.

    Args:
        csv_path: Path to the CSV file to load

    Returns:
        A dictionary containing:
        - success: Boolean indicating if load was successful
        - data_summary: Preview and basic metadata (shape, columns)
        - error: Error message if failed
        - dataframe_variable: Name of the variable storing the dataframe
    """

    inputs = {
        "csv_path": {
            "type": "string",
            "description": "Path to the CSV file to load"
        }
    }
    output_type = "string"

    def forward(self, csv_path: str) -> str:
        """Load CSV with error handling and return summary."""
        try:
            # Validate path
            if not os.path.exists(csv_path):
                return f"ERROR: File not found at path: {csv_path}"

            # Try loading with default settings first
            try:
                df = pl.read_csv(csv_path)
            except Exception as e:
                # Try with different encodings and separators
                encodings = ['utf-8', 'latin-1', 'iso-8859-1']
                separators = [',', ';', '\t', '|']

                df = None
                for encoding in encodings:
                    for sep in separators:
                        try:
                            df = pl.read_csv(
                                csv_path,
                                encoding=encoding,
                                separator=sep,
                                ignore_errors=True
                            )
                            break
                        except:
                            continue
                    if df is not None:
                        break

                if df is None:
                    return f"ERROR: Could not load CSV with various encoding/separator combinations. Original error: {str(e)}"

            # Get basic info
            n_rows, n_cols = df.shape
            columns = list(df.columns)
            dtypes = [str(dtype) for dtype in df.dtypes]

            # Format as readable string with key info
            output = f"""CSV loaded: {csv_path}
Shape: {n_rows} rows, {n_cols} columns
Columns: {columns}
Types: {dtypes}
Nulls: {[df[col].null_count() for col in columns]}"""

            return output

        except Exception as e:
            return f"ERROR: Unexpected error loading CSV: {str(e)}"
