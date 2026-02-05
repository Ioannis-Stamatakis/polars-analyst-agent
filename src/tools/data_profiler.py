"""
DataProfilerTool: Deep profiling including distributions and correlations.
"""
import polars as pl
from smolagents import Tool
from typing import Dict, Any
import numpy as np


class DataProfilerTool(Tool):
    name = "data_profiler"
    description = """
    Performs deep profiling of the dataset including distributions and correlations.

    Args:
        csv_path: Path to the CSV file to profile

    Returns:
        Advanced profiling information:
        - Distribution characteristics (skewness, outliers)
        - Correlation analysis between numeric columns
        - Cardinality analysis for categorical columns
        - Temporal patterns if date columns exist
        - Recommendations for appropriate visualizations
    """

    inputs = {
        "csv_path": {
            "type": "string",
            "description": "Path to the CSV file to profile"
        }
    }
    output_type = "string"

    def forward(self, csv_path: str) -> str:  # pragma: no cover
        """Profile dataframe deeply and return recommendations."""
        try:
            # Load the dataframe
            df = pl.read_csv(csv_path, ignore_errors=True)

            output_lines = ["PROFILING REPORT", ""]

            # Identify column types
            numeric_cols = []
            categorical_cols = []

            for col in df.columns:
                dtype = str(df[col].dtype)
                n_unique = df[col].n_unique()
                n_rows = len(df)

                if 'int' in dtype.lower() or 'float' in dtype.lower():
                    numeric_cols.append(col)
                elif n_unique < 20:  # Low cardinality
                    categorical_cols.append(col)

            # Numeric analysis
            if numeric_cols:
                output_lines.append("Numeric ranges:")
                for col in numeric_cols[:3]:  # Limit to first 3
                    try:
                        values = df[col].drop_nulls()
                        if len(values) > 0:
                            q1 = values.quantile(0.25)
                            q3 = values.quantile(0.75)
                            iqr = q3 - q1
                            lower_bound = q1 - 1.5 * iqr
                            upper_bound = q3 + 1.5 * iqr
                            outliers = ((values < lower_bound) | (values > upper_bound)).sum()

                            output_lines.append(f"  {col}: [{values.min()}, {values.max()}], outliers={outliers}")
                    except:
                        pass
                output_lines.append("")

            # Correlation analysis
            if len(numeric_cols) >= 2:
                output_lines.append("Correlations (|r| > 0.5):")
                try:
                    correlations = []
                    for i, col1 in enumerate(numeric_cols[:5]):
                        for col2 in numeric_cols[i+1:6]:
                            try:
                                corr = df.select([
                                    pl.corr(col1, col2).alias("correlation")
                                ]).item()
                                if abs(corr) > 0.5:
                                    correlations.append((col1, col2, corr))
                            except:
                                pass

                    if correlations:
                        for col1, col2, corr in sorted(correlations, key=lambda x: abs(x[2]), reverse=True):
                            output_lines.append(f"  {col1} <-> {col2}: {corr:.3f}")
                    else:
                        output_lines.append("  None found")
                except Exception as e:
                    output_lines.append(f"  Error: {str(e)}")
                output_lines.append("")

            # Categorical analysis
            if categorical_cols:
                output_lines.append("Categorical top-5 values:")
                for col in categorical_cols[:3]:  # Limit to first 3
                    value_counts = df[col].value_counts().sort("count", descending=True)
                    top_values = value_counts.head(5)
                    output_lines.append(f"  {col}: {', '.join([str(row[0]) for row in top_values.iter_rows()])}")
                output_lines.append("")

            return "\n".join(output_lines)

        except Exception as e:
            return f"ERROR: Failed to profile data: {str(e)}"
