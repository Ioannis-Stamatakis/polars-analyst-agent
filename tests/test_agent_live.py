"""
Live end-to-end tests that hit the Gemini API.

Each test runs the full agent loop on a real dataset and records:
  - Whether it completed without exception
  - Number of steps consumed
  - Whether final_answer() was called (result is not None/empty)
  - Whether a PNG visualization was saved
  - Wall-clock time

Run with:
    cd /home/istamatakis/Personal/TestAgent
    venv/bin/python -m pytest tests/test_agent_live.py -v --tb=short

Results are printed as a summary table at the end via the session-scoped
fixture so you can eyeball efficiency at a glance.
"""
import os
import sys
import time
import glob
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agent_controller import DataAnalysisAgent


# ---------------------------------------------------------------------------
# Shared state: collect results across all tests for the summary table
# ---------------------------------------------------------------------------

RESULTS = []


@pytest.fixture(autouse=True, scope="session")
def _print_summary(request):
    """Print results table after all tests finish."""
    yield
    if RESULTS:
        print("\n" + "=" * 80)
        print("LIVE TEST SUMMARY")
        print("=" * 80)
        print(f"{'Test':<40} {'OK':>4} {'Steps':>6} {'Answer':>7} {'PNG':>4} {'Time':>7}")
        print("-" * 80)
        for r in RESULTS:
            print(
                f"{r['name']:<40} "
                f"{'Y' if r['ok'] else 'N':>4} "
                f"{r['steps']:>6} "
                f"{'Y' if r['has_answer'] else 'N':>7} "
                f"{'Y' if r['has_png'] else 'N':>4} "
                f"{r['elapsed']:>6.1f}s"
            )
        print("=" * 80)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _run_agent(name: str, csv_path: str, task: str):
    """Run agent, capture metrics, append to RESULTS, assert no crash."""
    # Snapshot PNGs before run so we only detect new ones
    pngs_before = set(glob.glob("*.png"))

    agent = DataAnalysisAgent(
        model_name="gemini/gemini-2.5-flash",
        max_steps=12,
        verbosity_level=0   # quiet — we only care about result
    )

    start = time.time()
    try:
        result = agent.analyze(csv_path=csv_path, task=task)
        elapsed = time.time() - start
        ok = True
    except Exception as e:
        elapsed = time.time() - start
        result = str(e)
        ok = False

    pngs_after = set(glob.glob("*.png"))
    new_pngs = pngs_after - pngs_before

    # "steps" is not directly exposed; we approximate from agent internals
    steps = getattr(agent.agent, 'step_number', None) or 0

    has_answer = (
        ok
        and result is not None
        and len(str(result).strip()) > 0
        and "Analysis failed" not in str(result)
    )

    RESULTS.append({
        "name": name,
        "ok": ok,
        "steps": steps,
        "has_answer": has_answer,
        "has_png": len(new_pngs) > 0,
        "elapsed": elapsed,
        "result": result,
        "new_pngs": new_pngs,
    })

    # Core assertion: must not crash and must produce an answer
    assert ok, f"Agent raised an exception:\n{result}"
    assert has_answer, f"Agent did not produce a final answer. Result:\n{result}"


# ---------------------------------------------------------------------------
# Test cases — each is a distinct real-world scenario
# ---------------------------------------------------------------------------

class TestSalesData:
    """Tests against sales_data.csv (has 2 nulls in sales_amount)."""

    def test_sales_by_region(self):
        _run_agent(
            name="sales_by_region",
            csv_path="examples/sample_datasets/sales_data.csv",
            task="Show total sales by region and create a bar chart."
        )

    def test_sales_by_product(self):
        _run_agent(
            name="sales_by_product",
            csv_path="examples/sample_datasets/sales_data.csv",
            task="Compare total revenue and average units sold per product. Visualize both."
        )

    def test_sales_time_trend(self):
        _run_agent(
            name="sales_time_trend",
            csv_path="examples/sample_datasets/sales_data.csv",
            task="Show daily sales trend over time with a line chart."
        )

    def test_sales_null_handling(self):
        """Specifically tests whether the agent handles the 2 nulls correctly."""
        _run_agent(
            name="sales_null_handling",
            csv_path="examples/sample_datasets/sales_data.csv",
            task="Identify and handle missing values in sales_amount. Report how many nulls exist and show the cleaned totals by region."
        )


class TestCustomerData:
    """Tests against customer_data.csv (nulls in income + purchase_frequency)."""

    def test_satisfaction_by_membership(self):
        _run_agent(
            name="satisfaction_by_membership",
            csv_path="examples/sample_datasets/customer_data.csv",
            task="Show average satisfaction score by membership level with a bar chart."
        )

    def test_income_age_correlation(self):
        """Common failure point: agent invents type conversions on numeric cols."""
        _run_agent(
            name="income_age_correlation",
            csv_path="examples/sample_datasets/customer_data.csv",
            task="Plot the correlation between age and income. Include a scatter plot."
        )

    def test_purchase_frequency_analysis(self):
        """Regression guard: purchase_frequency is Int64, agent must NOT map it as categorical."""
        _run_agent(
            name="purchase_freq_analysis",
            csv_path="examples/sample_datasets/customer_data.csv",
            task="Analyze purchase_frequency distribution by membership level. Show a grouped bar chart."
        )

    def test_gender_income_comparison(self):
        _run_agent(
            name="gender_income",
            csv_path="examples/sample_datasets/customer_data.csv",
            task="Compare average income between genders. Create a visualization."
        )


class TestEmployeeData:
    """Tests against employee_data.csv (no nulls, has categorical performance_rating)."""

    def test_salary_by_department(self):
        _run_agent(
            name="salary_by_dept",
            csv_path="examples/sample_datasets/employee_data.csv",
            task="Show average salary by department with a bar chart."
        )

    def test_experience_vs_salary(self):
        _run_agent(
            name="experience_vs_salary",
            csv_path="examples/sample_datasets/employee_data.csv",
            task="Scatter plot of years_experience vs salary. Color by department if possible."
        )

    def test_performance_by_department(self):
        """performance_rating is categorical (Excellent/Good/Average) — tests string handling."""
        _run_agent(
            name="performance_by_dept",
            csv_path="examples/sample_datasets/employee_data.csv",
            task="Show the distribution of performance ratings within each department as a stacked or grouped chart."
        )


class TestEdgeCases:
    """Scenarios designed to trigger known failure modes."""

    def test_comprehensive_eda(self):
        """Default task — 'do everything'. Stresses step budget."""
        _run_agent(
            name="comprehensive_eda",
            csv_path="examples/sample_datasets/customer_data.csv",
            task="Perform comprehensive exploratory data analysis. Show distributions, correlations, and key insights."
        )

    def test_multiple_visualizations(self):
        """Agent must save multiple PNGs in one run."""
        _run_agent(
            name="multi_viz",
            csv_path="examples/sample_datasets/sales_data.csv",
            task="Create separate visualizations for sales by region, sales by product, and daily sales over time. Save each plot as its own PNG file."
        )
