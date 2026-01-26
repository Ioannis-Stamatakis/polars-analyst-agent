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

            output = ["DATA QUALITY REPORT", "=" * 50, ""]

            # Check for nulls
            null_cols = []
            for col in df.columns:
                null_count = df[col].null_count()
                if null_count > 0:
                    pct = (null_count / n_rows) * 100
                    null_cols.append((col, null_count, pct))

            if null_cols:
                output.append("⚠️  NULL VALUES DETECTED:")
                for col, count, pct in null_cols:
                    output.append(f"   {col}: {count} nulls ({pct:.1f}%)")

                output.append("\n✅ RECOMMENDED CODE:")
                output.append("   # Option 1: Drop rows with nulls")
                output.append("   df = df.drop_nulls()")
                output.append("")
                output.append("   # Option 2: Fill nulls with value")
                for col, _, _ in null_cols:
                    dtype = str(df[col].dtype)
                    if 'Int' in dtype or 'Float' in dtype:
                        output.append(f"   df = df.with_columns(pl.col('{col}').fill_null(0))")
                    else:
                        output.append(f"   df = df.with_columns(pl.col('{col}').fill_null('Unknown'))")
                output.append("")
            else:
                output.append("✅ No null values - clean dataset!")
                output.append("")

            # Check data types
            output.append("COLUMN TYPES:")
            numeric_cols = []
            categorical_cols = []

            for col in df.columns:
                dtype = str(df[col].dtype)
                unique = df[col].n_unique()

                if 'Int' in dtype or 'Float' in dtype:
                    numeric_cols.append(col)
                    output.append(f"   {col}: {dtype} (NUMERIC)")
                else:
                    if unique < 20:
                        categorical_cols.append(col)
                        output.append(f"   {col}: {dtype} (CATEGORICAL, {unique} categories)")
                    else:
                        output.append(f"   {col}: {dtype} (TEXT)")

            output.append("")
            output.append("SUGGESTED ANALYSIS:")

            if numeric_cols:
                output.append(f"   Numeric columns: {numeric_cols}")
                output.append("   → Use: df.describe() or df.select(pl.col(numeric_cols).mean())")

            if categorical_cols:
                output.append(f"   Categorical columns: {categorical_cols}")
                output.append(f"   → Use: df.group_by('{categorical_cols[0]}').agg(pl.count())")

            if numeric_cols and categorical_cols:
                output.append(f"\n   Combined analysis:")
                output.append(f"   → df.group_by('{categorical_cols[0]}').agg(pl.mean('{numeric_cols[0]}'))")

            return "\n".join(output)

        except Exception as e:
            return f"ERROR: Validation failed: {str(e)}"
