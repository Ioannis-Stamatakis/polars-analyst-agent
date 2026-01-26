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

            output_lines = [
                "DATA PROFILING REPORT",
                "=" * 50,
                ""
            ]

            # Identify column types
            numeric_cols = []
            categorical_cols = []
            potential_date_cols = []

            for col in df.columns:
                dtype = str(df[col].dtype)
                n_unique = df[col].n_unique()
                n_rows = len(df)

                if 'int' in dtype.lower() or 'float' in dtype.lower():
                    numeric_cols.append(col)
                elif n_unique < min(50, n_rows * 0.05):  # Low cardinality
                    categorical_cols.append(col)
                elif 'date' in col.lower() or 'time' in col.lower():
                    potential_date_cols.append(col)

            output_lines.append("COLUMN TYPE CLASSIFICATION:")
            output_lines.append(f"  Numeric: {len(numeric_cols)} columns - {numeric_cols}")
            output_lines.append(f"  Categorical: {len(categorical_cols)} columns - {categorical_cols}")
            output_lines.append(f"  Potential dates: {len(potential_date_cols)} columns - {potential_date_cols}")
            output_lines.append("")

            # Numeric analysis
            if numeric_cols:
                output_lines.append("NUMERIC COLUMN ANALYSIS:")
                output_lines.append("")

                for col in numeric_cols[:5]:  # Limit to first 5
                    try:
                        values = df[col].drop_nulls()
                        if len(values) > 0:
                            q1 = values.quantile(0.25)
                            q3 = values.quantile(0.75)
                            iqr = q3 - q1

                            # Detect outliers
                            lower_bound = q1 - 1.5 * iqr
                            upper_bound = q3 + 1.5 * iqr
                            outliers = ((values < lower_bound) | (values > upper_bound)).sum()

                            output_lines.append(f"  {col}:")
                            output_lines.append(f"    Range: [{values.min()}, {values.max()}]")
                            output_lines.append(f"    IQR: {iqr:.2f}")
                            output_lines.append(f"    Outliers: {outliers} ({(outliers/len(values)*100):.1f}%)")
                    except:
                        pass

                output_lines.append("")

            # Correlation analysis
            if len(numeric_cols) >= 2:
                output_lines.append("CORRELATION ANALYSIS:")

                try:
                    # Select numeric columns and compute correlation
                    numeric_df = df.select(numeric_cols[:10])  # Limit to first 10

                    # Calculate correlations manually
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
                        output_lines.append("  Strong correlations (|r| > 0.5):")
                        for col1, col2, corr in sorted(correlations, key=lambda x: abs(x[2]), reverse=True):
                            output_lines.append(f"    {col1} <-> {col2}: {corr:.3f}")
                    else:
                        output_lines.append("  No strong correlations found (|r| > 0.5)")
                except Exception as e:
                    output_lines.append(f"  Could not compute correlations: {str(e)}")

                output_lines.append("")

            # Categorical analysis
            if categorical_cols:
                output_lines.append("CATEGORICAL COLUMN ANALYSIS:")
                output_lines.append("")

                for col in categorical_cols[:5]:  # Limit to first 5
                    value_counts = df[col].value_counts().sort("count", descending=True)
                    top_values = value_counts.head(5)

                    output_lines.append(f"  {col}:")
                    output_lines.append(f"    Unique values: {df[col].n_unique()}")
                    output_lines.append(f"    Top values:")
                    for row in top_values.iter_rows():
                        output_lines.append(f"      {row[0]}: {row[1]} occurrences")
                    output_lines.append("")

            # Visualization recommendations
            output_lines.append("RECOMMENDED VISUALIZATIONS:")
            output_lines.append("")

            if numeric_cols:
                output_lines.append("📊 Numeric columns:")
                output_lines.append(f"   - Histograms/distributions: {', '.join(numeric_cols[:3])}")
                output_lines.append(f"   - Box plots (outlier detection): {', '.join(numeric_cols[:3])}")

            if len(numeric_cols) >= 2:
                output_lines.append(f"   - Scatter plots: {numeric_cols[0]} vs {numeric_cols[1]}")
                output_lines.append(f"   - Correlation heatmap for all numeric columns")

            if categorical_cols:
                output_lines.append("📊 Categorical columns:")
                output_lines.append(f"   - Bar charts: {', '.join(categorical_cols[:3])}")
                output_lines.append(f"   - Count plots with percentages")

            if categorical_cols and numeric_cols:
                output_lines.append("📊 Combined analysis:")
                output_lines.append(f"   - Group by {categorical_cols[0]}, aggregate {numeric_cols[0]}")
                output_lines.append(f"   - Box plots: {numeric_cols[0]} across {categorical_cols[0]} categories")

            if potential_date_cols:
                output_lines.append("📊 Time series:")
                output_lines.append(f"   - Temporal trends for date columns")

            return "\n".join(output_lines)

        except Exception as e:
            return f"ERROR: Failed to profile data: {str(e)}"
