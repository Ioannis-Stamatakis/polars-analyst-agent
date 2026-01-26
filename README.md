# Data Analysis Code Generator with smolagents

An AI-powered data analysis agent that loads CSV files with Polars, inspects actual data, and generates tailored analysis code that it executes and validates.

## Why This Uses smolagents (Not Just an LLM)

This project demonstrates the power of **agentic AI** vs simple LLM prompting:

- 🔍 **Grounded in Reality**: Agent inspects actual CSV data before generating code
- 🔄 **Execution Feedback Loop**: Generates code → Executes → Reads errors → Debugs → Regenerates
- 🛠️ **Tool Orchestration**: Intelligently sequences: Load → Inspect → Profile → Generate → Execute
- 🎯 **Context-Aware**: Adapts code to discovered data characteristics (dtypes, nulls, distributions)
- 🔁 **Intelligent Recovery**: Reads tracebacks, understands issues, makes targeted fixes

**LLM alone**: Generates code blindly based on generic assumptions
**Agent with smolagents**: Inspects YOUR data, generates tailored code, validates it works

## Features

### Core Capabilities
- 📊 Intelligent CSV loading with auto-detection (encoding, separators)
- 🔬 Comprehensive data inspection (schema, nulls, statistics)
- 📈 Deep profiling (distributions, correlations, outliers)
- 🤖 Context-aware code generation (adapts to actual data)
- ✅ Execution validation with error recovery
- 🎨 Smart visualization selection by data type

### Advanced Features
- Natural language queries ("Show distribution of ages")
- Multi-file comparison
- Anomaly detection
- Code explanation for educational value
- Export options (code files, reports, visualizations)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd data-analysis-agent

# Install dependencies
pip install -r requirements.txt

# Set up your Gemini API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Quick Start

### Option 1: Command Line

```bash
# Analyze a CSV file
python -m src.agent_controller examples/sample_datasets/sales_data.csv

# With custom task
python -m src.agent_controller examples/sample_datasets/customer_data.csv \
  --task "Show me the correlation between age and income"

# Interactive mode
python -m src.agent_controller --interactive
```

### Option 2: Python API

```python
from src.agent_controller import DataAnalysisAgent

# Initialize agent
agent = DataAnalysisAgent(
    model_name="gemini/gemini-2.0-flash-exp",
    api_key="your-api-key"  # Or set GEMINI_API_KEY env var
)

# Run analysis
result = agent.analyze(
    csv_path="data/sales.csv",
    task="Perform comprehensive exploratory analysis"
)
```

### Option 3: Run Examples

```bash
# Run all examples
python examples/example_usage.py

# Run specific example
python examples/example_usage.py --example 1  # Sales analysis
python examples/example_usage.py --example 2  # Customer analysis
python examples/example_usage.py --example 3  # Custom query
python examples/example_usage.py --example 4  # Interactive mode
```

## How It Works

### Agent Workflow

```
1. LOAD DATA (PolarsDataLoaderTool)
   ├─> Robust CSV loading with auto-detection
   ├─> Error handling for encoding/separator issues
   └─> Returns shape, columns, preview

2. INSPECT DATA (DataInspectorTool)
   ├─> Analyzes schema (dtypes, nulls, unique counts)
   ├─> Computes basic statistics
   └─> Identifies data quality issues

3. PROFILE DATA (DataProfilerTool)
   ├─> Deep profiling (distributions, correlations)
   ├─> Outlier detection
   ├─> Cardinality analysis
   └─> Returns visualization recommendations

4. GENERATE CODE (Agent Reasoning)
   ├─> Creates Polars code based on ACTUAL data
   ├─> Handles nulls discovered during inspection
   ├─> Selects appropriate visualizations
   └─> Includes insights extraction

5. EXECUTE & VALIDATE (PythonInterpreterTool)
   ├─> Runs code in safe sandbox
   ├─> If error: reads traceback → debugs → regenerates
   └─> Iterates until working code produced

6. PRESENT RESULTS
   ├─> Formats findings
   ├─> Shows visualizations
   └─> Explains insights
```

### Example: Agent in Action

```python
# User provides CSV path
agent.analyze("sales_data.csv", task="Analyze sales trends")

# Agent's thought process (automatic):
# 1. "Let me load this CSV first"
#    → Calls: polars_data_loader("sales_data.csv")
#    → Discovers: 25 rows, columns [date, product, region, sales_amount, units_sold]

# 2. "Now let me inspect the structure"
#    → Calls: data_inspector("sales_data.csv")
#    → Discovers: 2 null values in sales_amount, sales_amount is numeric,
#                 product and region are categorical

# 3. "Let me profile the data deeply"
#    → Calls: data_profiler("sales_data.csv")
#    → Discovers: Strong correlation between units_sold and sales_amount,
#                 3 products, 4 regions, no major outliers

# 4. "Based on what I found, I'll generate tailored code"
#    → Generates Polars code that:
#      - Handles the 2 null values in sales_amount
#      - Creates time series plot (found date column)
#      - Creates bar chart by product (found categorical)
#      - Computes sales by region
#      - Shows correlation plot

# 5. "Let me execute this code"
#    → Calls: python_interpreter(generated_code)
#    → If error: "Hmm, got an error. Let me fix it..."
#    → Re-generates and re-executes until success

# 6. "Here are your results with visualizations!"
```

## Project Structure

```
data-analysis-agent/
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
│
├── src/
│   ├── agent_controller.py          # Main orchestration & CLI
│   ├── tools/
│   │   ├── data_loader.py          # PolarsDataLoaderTool
│   │   ├── data_inspector.py       # DataInspectorTool
│   │   └── data_profiler.py        # DataProfilerTool
│   ├── execution/
│   │   └── authorized_imports.py   # Safe execution config
│   ├── formatters/
│   │   └── result_formatter.py     # Rich formatting
│   └── prompts/
│       └── system_prompts.py       # Agent instructions
│
├── examples/
│   ├── sample_datasets/
│   │   ├── sales_data.csv          # Example sales data
│   │   └── customer_data.csv       # Example customer data
│   └── example_usage.py            # Demo scripts
│
├── tests/
│   └── test_integration.py         # Integration tests
│
└── outputs/                         # Generated analyses
    ├── code/                        # Saved code files
    ├── visualizations/              # Saved plots
    └── reports/                     # Markdown reports
```

## Dependencies

- **smolagents**: Agent framework with tool orchestration
- **litellm**: Unified LLM interface (supports Gemini, OpenAI, etc.)
- **polars**: Fast DataFrame library for data manipulation
- **numpy**: Numerical computing
- **matplotlib/seaborn**: Visualization libraries
- **rich**: Beautiful CLI formatting
- **python-dotenv**: Environment variable management

## Configuration

### Environment Variables

Create a `.env` file:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

### Agent Parameters

```python
agent = DataAnalysisAgent(
    model_name="gemini/gemini-2.0-flash-exp",  # LiteLLM model ID
    api_key="...",                              # API key (optional if in env)
    max_steps=20,                               # Max agentic iterations
    verbosity_level=1                           # 0=silent, 1=normal, 2=verbose
)
```

## Why This Showcases smolagents

### 1. Tool Orchestration
The agent follows a logical workflow: Load → Inspect → Profile → Generate → Execute. This demonstrates multi-step reasoning and planning that requires an agent framework.

### 2. Execution Feedback Loop
Unlike a simple LLM that generates code blindly:
- **LLM**: Generates code → User runs it → May fail
- **Agent**: Generates → Executes → Reads errors → Debugs → Regenerates → Validates

### 3. Grounded in Actual Data
The agent MUST inspect real CSV files to know:
- What dtypes exist (numeric, categorical, dates)
- Which columns have nulls
- What visualizations are appropriate
- Whether correlations exist

This requires tool usage - an LLM alone can't access files.

### 4. Dynamic Decision Making
The agent adapts based on discoveries:
- Timestamps → time series analysis
- High cardinality categorical → different viz strategy
- Many nulls → include imputation
- Correlations → add correlation matrix

### 5. Intelligent Error Recovery
When code fails, the agent:
- Reads the traceback
- Understands the specific issue (not just "try again")
- Makes targeted fixes
- Re-executes to validate

## Verification

To verify the agent is working correctly:

```bash
# Run tests
python -m pytest tests/

# Or manually verify:
python examples/example_usage.py --example 1
```

**Check that the agent:**
1. ✅ Calls tools in correct sequence (never generates code before inspecting)
2. ✅ Successfully recovers from execution errors
3. ✅ Generates different code for different data types
4. ✅ Uses Polars (not pandas) in all generated code
5. ✅ Produces working, executable analysis code

## Example Output

```
→ Starting Analysis
  File: examples/sample_datasets/sales_data.csv
  Task: Perform comprehensive exploratory data analysis

[Agent loads data...]
CSV LOADED SUCCESSFULLY
Shape: 25 rows × 6 columns

[Agent inspects data...]
Found 2 null values in sales_amount column
Identified 3 numeric columns, 3 categorical columns

[Agent profiles data...]
Strong correlation between units_sold and sales_amount (r=0.87)
Recommending: time series plot, bar charts, correlation heatmap

[Agent generates code...]
Generated Polars analysis code with:
- Null handling for sales_amount
- Sales trends over time
- Revenue by product and region
- Correlation analysis

[Agent executes code...]
✓ Code executed successfully

Analysis Complete
═════════════════
Generated 3 visualizations:
  📊 outputs/visualizations/sales_trends.png
  📊 outputs/visualizations/revenue_by_product.png
  📊 outputs/visualizations/correlation_heatmap.png

Key Insights:
  • Widget C generates highest revenue ($23,580)
  • North region leads in sales volume
  • Strong positive correlation between units and revenue
```

## Contributing

Contributions welcome! Areas for improvement:
- Additional tool implementations (SQL databases, APIs)
- More sophisticated error recovery strategies
- Multi-file comparative analysis
- Real-time data streaming support
- Export to various formats (PDF reports, interactive dashboards)

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- [smolagents](https://github.com/huggingface/smolagents) - Hugging Face's agent framework
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM interface
- [Polars](https://pola.rs) - Lightning-fast DataFrame library
- [Gemini](https://ai.google.dev) - Google's generative AI model
