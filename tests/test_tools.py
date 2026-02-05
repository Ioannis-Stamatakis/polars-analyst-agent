"""
Unit tests for all tools and memory compaction.
No API calls — runs fast, verifies exact output the agent sees.
"""
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.data_loader import PolarsDataLoaderTool
from src.tools.data_inspector import DataInspectorTool
from src.tools.data_profiler import DataProfilerTool
from src.tools.data_validator import DataValidatorTool
from src.memory.compact_memory import truncate_text, compact_memory_callback


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SALES_PATH = "examples/sample_datasets/sales_data.csv"
CUSTOMER_PATH = "examples/sample_datasets/customer_data.csv"
EMPLOYEE_PATH = "examples/sample_datasets/employee_data.csv"


@pytest.fixture
def sales_csv():
    return SALES_PATH


@pytest.fixture
def customer_csv():
    return CUSTOMER_PATH


@pytest.fixture
def employee_csv():
    return EMPLOYEE_PATH


@pytest.fixture
def empty_csv(tmp_path):
    """CSV with headers only, no rows."""
    p = tmp_path / "empty.csv"
    p.write_text("a,b,c\n")
    return str(p)


@pytest.fixture
def semicolon_csv(tmp_path):
    """CSV using semicolon separator."""
    p = tmp_path / "semi.csv"
    p.write_text("x;y;z\n1;2;3\n4;5;6\n")
    return str(p)


@pytest.fixture
def all_nulls_csv(tmp_path):
    """CSV where one column is entirely null."""
    p = tmp_path / "nulls.csv"
    p.write_text("id,val\n1,\n2,\n3,\n")
    return str(p)


# ---------------------------------------------------------------------------
# PolarsDataLoaderTool
# ---------------------------------------------------------------------------

class TestDataLoader:
    def test_loads_sales(self, sales_csv):
        result = PolarsDataLoaderTool().forward(sales_csv)
        assert "25 rows" in result
        assert "6 columns" in result
        # Must include actual column names so agent can reference them
        for col in ["date", "product", "region", "sales_amount", "units_sold", "customer_type"]:
            assert col in result

    def test_loads_customer(self, customer_csv):
        result = PolarsDataLoaderTool().forward(customer_csv)
        assert "25 rows" in result
        assert "7 columns" in result

    def test_loads_employee(self, employee_csv):
        result = PolarsDataLoaderTool().forward(employee_csv)
        assert "25 rows" in result
        assert "7 columns" in result

    def test_missing_file_returns_error(self):
        result = PolarsDataLoaderTool().forward("/no/such/file.csv")
        assert "ERROR" in result
        assert "not found" in result.lower()

    def test_empty_csv(self, empty_csv):
        result = PolarsDataLoaderTool().forward(empty_csv)
        # Should not crash; 0 rows is valid
        assert "0 rows" in result

    def test_semicolon_csv(self, semicolon_csv):
        # BUG: pl.read_csv doesn't raise on semicolon files — it loads as 1 column.
        # Fallback never triggers. Documenting current (broken) behavior.
        result = PolarsDataLoaderTool().forward(semicolon_csv)
        assert "ERROR" not in result
        # Currently loads as single string column "x;y;z" instead of 3 columns
        assert "1 columns" in result

    def test_output_contains_null_counts(self, sales_csv):
        result = PolarsDataLoaderTool().forward(sales_csv)
        # sales_data has 2 nulls in sales_amount — null counts list must appear
        assert "Nulls:" in result


# ---------------------------------------------------------------------------
# DataInspectorTool
# ---------------------------------------------------------------------------

class TestDataInspector:
    def test_sales_schema(self, sales_csv):
        result = DataInspectorTool().forward(sales_csv)
        assert "25 rows" in result
        assert "6 columns" in result
        # Every column must be named
        for col in ["date", "product", "region", "sales_amount", "units_sold", "customer_type"]:
            assert col in result

    def test_customer_numeric_classification(self, customer_csv):
        result = DataInspectorTool().forward(customer_csv)
        # These are Int64/Float64 — must be labeled NUMERIC
        for col in ["age", "income", "purchase_frequency", "satisfaction_score"]:
            assert col in result
        assert "NUMERIC" in result

    def test_customer_categorical_classification(self, customer_csv):
        result = DataInspectorTool().forward(customer_csv)
        # gender and membership_level are low-cardinality strings
        assert "CATEGORICAL" in result
        assert "gender" in result
        assert "membership_level" in result

    def test_detects_nulls_sales(self, sales_csv):
        result = DataInspectorTool().forward(sales_csv)
        # 2 nulls in sales_amount
        assert "sales_amount" in result
        assert "nulls=" in result  # each line has nulls=N

    def test_detects_nulls_customer(self, customer_csv):
        result = DataInspectorTool().forward(customer_csv)
        # income: 1 null, purchase_frequency: 1 null
        assert "income" in result
        assert "purchase_frequency" in result

    def test_employee_no_nulls(self, employee_csv):
        result = DataInspectorTool().forward(employee_csv)
        # employee_data has zero nulls
        assert "No nulls" in result

    def test_missing_file(self):
        result = DataInspectorTool().forward("/no/such/file.csv")
        assert "ERROR" in result

    def test_empty_csv(self, empty_csv):
        result = DataInspectorTool().forward(empty_csv)
        assert "0 rows" in result


# ---------------------------------------------------------------------------
# DataProfilerTool
# ---------------------------------------------------------------------------

class TestDataProfiler:
    def test_sales_profiling(self, sales_csv):
        result = DataProfilerTool().forward(sales_csv)
        assert "PROFILING REPORT" in result
        # sales_amount and units_sold are numeric — ranges must appear
        assert "sales_amount" in result or "units_sold" in result

    def test_customer_correlations(self, customer_csv):
        result = DataProfilerTool().forward(customer_csv)
        # age vs income likely correlates > 0.5 in this dataset
        assert "Correlations" in result

    def test_customer_categorical_top_values(self, customer_csv):
        result = DataProfilerTool().forward(customer_csv)
        # gender and membership_level are low-cardinality strings
        assert "Categorical" in result

    def test_employee_profiling(self, employee_csv):
        result = DataProfilerTool().forward(employee_csv)
        assert "PROFILING REPORT" in result
        assert "salary" in result

    def test_missing_file(self):
        result = DataProfilerTool().forward("/no/such/file.csv")
        assert "ERROR" in result

    def test_single_numeric_col_no_crash(self, tmp_path):
        """Only one numeric col — correlation block should not crash."""
        p = tmp_path / "single.csv"
        p.write_text("name,score\nAlice,90\nBob,80\n")
        result = DataProfilerTool().forward(str(p))
        assert "ERROR" not in result


# ---------------------------------------------------------------------------
# DataValidatorTool
# ---------------------------------------------------------------------------

class TestDataValidator:
    def test_sales_nulls_reported(self, sales_csv):
        result = DataValidatorTool().forward(sales_csv)
        assert "QUALITY REPORT" in result
        assert "sales_amount" in result
        assert "Nulls detected" in result

    def test_employee_clean(self, employee_csv):
        result = DataValidatorTool().forward(employee_csv)
        assert "No nulls" in result

    def test_customer_null_cols(self, customer_csv):
        result = DataValidatorTool().forward(customer_csv)
        assert "income" in result
        assert "purchase_frequency" in result

    def test_fix_options_present(self, sales_csv):
        result = DataValidatorTool().forward(sales_csv)
        # Should suggest drop_nulls or fill_null
        assert "drop_nulls" in result or "fill_null" in result

    def test_column_type_labels(self, customer_csv):
        result = DataValidatorTool().forward(customer_csv)
        assert "NUMERIC" in result
        assert "CATEGORICAL" in result

    def test_all_nulls_column(self, all_nulls_csv):
        result = DataValidatorTool().forward(all_nulls_csv)
        assert "val" in result
        # 3 nulls out of 3 rows = 100%
        assert "100.0%" in result

    def test_missing_file(self):
        result = DataValidatorTool().forward("/no/such/file.csv")
        assert "ERROR" in result


# ---------------------------------------------------------------------------
# Memory compaction
# ---------------------------------------------------------------------------

class TestTruncateText:
    def test_short_text_unchanged(self):
        assert truncate_text("hello", 100) == "hello"

    def test_exact_limit_unchanged(self):
        text = "x" * 100
        assert truncate_text(text, 100) == text

    def test_long_text_truncated(self):
        text = "a" * 1000
        result = truncate_text(text, 200)
        assert len(result) == 200
        assert result.endswith("... [truncated]")

    def test_custom_suffix(self):
        result = truncate_text("a" * 50, 20, suffix="[cut]")
        assert result.endswith("[cut]")
        assert len(result) == 20


class _FakeStep:
    """Minimal stand-in for smolagents ActionStep."""
    def __init__(self, observations, error=None):
        self.observations = observations
        self.error = error


class TestCompactMemoryCallback:
    def test_truncates_long_observation(self):
        step = _FakeStep(observations="x" * 2000)
        compact_memory_callback(step)
        assert len(step.observations) == 800
        assert step.observations.endswith("... [truncated]")

    def test_short_observation_unchanged(self):
        step = _FakeStep(observations="short")
        compact_memory_callback(step)
        assert step.observations == "short"

    def test_error_gets_higher_limit(self):
        step = _FakeStep(observations="e" * 2000, error="boom")
        compact_memory_callback(step)
        assert len(step.observations) == 1200

    def test_no_observations_attr_no_crash(self):
        class NoObs:
            pass
        # Should not raise
        compact_memory_callback(NoObs())

    def test_empty_observations_no_crash(self):
        step = _FakeStep(observations="")
        compact_memory_callback(step)  # no raise

    def test_kwargs_accepted(self):
        """Regression: callback must accept **kwargs (smolagents passes agent=)."""
        step = _FakeStep(observations="hi")
        compact_memory_callback(step, agent="fake_agent_object")
        assert step.observations == "hi"
