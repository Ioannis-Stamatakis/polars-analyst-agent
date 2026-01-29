"""
DataValidatorTool: Validates CSV quality and provides actionable recommendations.
"""
import polars as pl
from smolagents import Tool


class DataValidatorTool(Tool):
    name = "data_validator"
    description = """
    Validates CSV data quality and provides code-ready recommendations.

    Args:
        csv_path: Path to the CSV file to validate

    Returns:
        Data quality report with specific code recommendations for handling issues
    """

    inputs = {
        "csv_path": {
            "type": "string",
            "description": "Path to the CSV file to validate"
        }
    }
    output_type = "string"

    def forward(self, csv_path: str) -> str:
        """Validate data and return actionable recommendations."""
        try:
            df = pl.read_csv(csv_path, ignore_errors=True)
            n_rows, n_cols = df.shape

            output = ["QUALITY REPORT", ""]

            # Check for nulls
            null_cols = []
            for col in df.columns:
                null_count = df[col].null_count()
                if null_count > 0:
                    pct = (null_count / n_rows) * 100
                    null_cols.append((col, null_count, pct))

            if null_cols:
                output.append("Nulls detected:")
                for col, count, pct in null_cols:
                    output.append(f"  {col}: {count} ({pct:.1f}%)")

                output.append("\nFix options:")
                output.append("  df.drop_nulls() OR")
                for col, _, _ in null_cols[:3]:  # Limit to first 3
                    dtype = str(df[col].dtype)
                    if 'Int' in dtype or 'Float' in dtype:
                        output.append(f"  pl.col('{col}').fill_null(0)")
                    else:
                        output.append(f"  pl.col('{col}').fill_null('Unknown')")
                output.append("")
            else:
                output.append("No nulls - clean dataset")
                output.append("")

            # Check data types
            output.append("Column types:")
            numeric_cols = []
            categorical_cols = []

            for col in df.columns:
                dtype = str(df[col].dtype)
                unique = df[col].n_unique()

                if 'Int' in dtype or 'Float' in dtype:
                    numeric_cols.append(col)
                    output.append(f"  {col}: {dtype} (NUMERIC)")
                else:
                    if unique < 20:
                        categorical_cols.append(col)
                        output.append(f"  {col}: {dtype} (CATEGORICAL)")
                    else:
                        output.append(f"  {col}: {dtype} (TEXT)")

            return "\n".join(output)

        except Exception as e:
            return f"ERROR: Validation failed: {str(e)}"
