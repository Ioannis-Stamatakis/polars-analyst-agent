"""
Integration tests for the Data Analysis Agent.
"""
import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.data_loader import PolarsDataLoaderTool
from src.tools.data_inspector import DataInspectorTool
from src.tools.data_profiler import DataProfilerTool


class TestTools:
    """Test individual tools."""

    @pytest.fixture
    def sales_csv_path(self):
        """Path to sample sales data."""
        return "examples/sample_datasets/sales_data.csv"

    @pytest.fixture
    def customer_csv_path(self):
        """Path to sample customer data."""
        return "examples/sample_datasets/customer_data.csv"

    def test_data_loader_success(self, sales_csv_path):
        """Test that data loader successfully loads a valid CSV."""
        tool = PolarsDataLoaderTool()
        result = tool.forward(sales_csv_path)

        assert "SUCCESS" in result
        assert "25 rows" in result
        assert "6 columns" in result
        assert "date" in result
        assert "product" in result

    def test_data_loader_missing_file(self):
        """Test that data loader handles missing files."""
        tool = PolarsDataLoaderTool()
        result = tool.forward("nonexistent_file.csv")

        assert "ERROR" in result
        assert "not found" in result.lower()

    def test_data_inspector(self, sales_csv_path):
        """Test that data inspector analyzes structure."""
        tool = DataInspectorTool()
        result = tool.forward(sales_csv_path)

        assert "DATA INSPECTION REPORT" in result
        assert "25" in result  # Row count
        assert "COLUMN DETAILS" in result
        assert "RECOMMENDATIONS" in result

    def test_data_profiler(self, customer_csv_path):
        """Test that data profiler provides deep analysis."""
        tool = DataProfilerTool()
        result = tool.forward(customer_csv_path)

        assert "DATA PROFILING REPORT" in result
        assert "COLUMN TYPE CLASSIFICATION" in result
        assert "RECOMMENDED VISUALIZATIONS" in result

    def test_inspector_detects_nulls(self, sales_csv_path):
        """Test that inspector detects null values."""
        tool = DataInspectorTool()
        result = tool.forward(sales_csv_path)

        # sales_data.csv has nulls in sales_amount
        assert "Nulls:" in result

    def test_profiler_identifies_numeric_cols(self, customer_csv_path):
        """Test that profiler identifies numeric columns."""
        tool = DataProfilerTool()
        result = tool.forward(customer_csv_path)

        # customer_data.csv has numeric columns like age, income
        assert "Numeric:" in result
        assert "age" in result.lower() or "income" in result.lower()

    def test_profiler_identifies_categorical_cols(self, customer_csv_path):
        """Test that profiler identifies categorical columns."""
        tool = DataProfilerTool()
        result = tool.forward(customer_csv_path)

        # customer_data.csv has categorical columns like gender, membership_level
        assert "Categorical:" in result


class TestAgentWorkflow:
    """Test the full agent workflow."""

    def test_tool_sequence(self, sales_csv_path):
        """Test that tools can be called in sequence."""
        # This simulates what the agent does

        # Step 1: Load
        loader = PolarsDataLoaderTool()
        load_result = loader.forward(sales_csv_path)
        assert "SUCCESS" in load_result

        # Step 2: Inspect
        inspector = DataInspectorTool()
        inspect_result = inspector.forward(sales_csv_path)
        assert "DATA INSPECTION REPORT" in inspect_result

        # Step 3: Profile
        profiler = DataProfilerTool()
        profile_result = profiler.forward(sales_csv_path)
        assert "DATA PROFILING REPORT" in profile_result

        # Verify all steps completed
        assert all([
            "SUCCESS" in load_result,
            "INSPECTION" in inspect_result,
            "PROFILING" in profile_result
        ])


def test_project_structure():
    """Test that all required files exist."""
    required_files = [
        "src/agent_controller.py",
        "src/tools/data_loader.py",
        "src/tools/data_inspector.py",
        "src/tools/data_profiler.py",
        "src/prompts/system_prompts.py",
        "src/formatters/result_formatter.py",
        "src/execution/authorized_imports.py",
        "examples/example_usage.py",
        "examples/sample_datasets/sales_data.csv",
        "examples/sample_datasets/customer_data.csv",
        "requirements.txt",
        "README.md",
    ]

    for file_path in required_files:
        assert os.path.exists(file_path), f"Missing required file: {file_path}"


def test_dependencies_installable():
    """Test that requirements.txt is valid."""
    assert os.path.exists("requirements.txt")

    with open("requirements.txt") as f:
        content = f.read()
        assert "smolagents" in content
        assert "litellm" in content
        assert "polars" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
