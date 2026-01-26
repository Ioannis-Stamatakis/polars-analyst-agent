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
        """Inspect dataframe and return detailed analysis."""
        try:
            df = pl.read_csv(csv_path, ignore_errors=True)
            n_rows, n_cols = df.shape

            output_lines = [
                f"Data shape: {n_rows} rows, {n_cols} columns",
                "\nColumn Analysis:"
            ]

            # Categorize columns
            numeric_cols = []
            categorical_cols = []
            columns_with_nulls = []

            # Analyze each column
            for col in df.columns:
                dtype = str(df[col].dtype)
                nulls = df[col].null_count()
                unique = df[col].n_unique()

                # Classify column type
                if 'Int' in dtype or 'Float' in dtype:
                    numeric_cols.append(col)
                    col_type = "NUMERIC"
                else:
                    if unique < 20:  # Low cardinality = likely categorical
                        categorical_cols.append(col)
                        col_type = "CATEGORICAL"
                    else:
                        col_type = "TEXT"

                # Track nulls
                if nulls > 0:
                    columns_with_nulls.append((col, nulls))

                output_lines.append(
                    f"  {col}: {dtype} ({col_type}), nulls={nulls}/{n_rows}, unique={unique}"
                )

            # Add summary
            output_lines.append("\nSummary:")
            output_lines.append(f"  Numeric columns: {len(numeric_cols)} → {numeric_cols}")
            output_lines.append(f"  Categorical columns: {len(categorical_cols)} → {categorical_cols}")

            if columns_with_nulls:
                output_lines.append(f"\n⚠️  Columns with nulls:")
                for col, count in columns_with_nulls:
                    pct = (count / n_rows) * 100
                    output_lines.append(f"    {col}: {count} nulls ({pct:.1f}%)")
                output_lines.append("\n💡 Recommendation: Use drop_nulls() or fill_null(0) to handle nulls")
            else:
                output_lines.append("\n✅ No null values found - clean dataset!")

            return "\n".join(output_lines)

        except Exception as e:
            return f"ERROR: Failed to inspect data: {str(e)}"
