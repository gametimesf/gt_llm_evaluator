# LLM Evaluator Service

A modular service for static LLM evaluation of LLM outputs.

## Requirements

- Python 3.12 or higher
- Dependencies are managed through `pyproject.toml`

## Setup

1. Install UV (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and activate a virtual environment using UV:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies using UV:

```bash
uv pip install -e .
```

## Available Scripts

### Chatbot Evaluation Scripts

Located in `scripts/chatbot/`:

- `simulate_convo.py` - Creates simulated conversations for testing and evaluation purposes
  - Usage: `uv run scripts/chatbot/simulate_convo.py`

- `pre_merge_check.py` - Runs validation checks before merging code changes
  - Usage: `uv run scripts/chatbot/pre_merge_check.py`

- `nightly_report.py` - Generates daily evaluation reports
  - Usage: `uv run scripts/chatbot/nightly_report.py`

### Main Evaluation Script

`convo_eval.py`

- Core evaluation script for analyzing conversations
- Usage: `uv run convo_eval.py`

### FAQ Generator Scripts

Located in `scripts/faq_generator/`:

- `faq_eval.py` - Evaluates FAQ content using DeepEval metrics
  - Usage: `uv run scripts/faq_generator/faq_eval.py --input "Your prompt" --content "Generated FAQ content" --context "Reference material"`
  - Required arguments:
    - `--input`: The input prompt text used to generate the FAQ
    - `--content`: The generated FAQ content to evaluate
    - `--context`: The reference material or ground truth to check against
  - Output: Generates a CSV file in `deepeval_results/faq_eval/` with evaluation metrics including:
    - Hallucination score
    - Evaluation reasoning
    - Cost metrics
  - Requirements:
    - DEEPEVAL_API_KEY environment variable must be set
    - Python 3.12 or higher
    - DeepEval package installed

## Project Structure

- `src/` - Source code directory
- `scripts/` - Utility scripts for various tasks
  - `chatbot/` - Chatbot evaluation and testing scripts
  - `faq_generator/` - FAQ generation scripts
- `mock_data/` - Sample data for testing
- `deepeval_results/` - Output directory for evaluation results

## Dependencies

Main dependencies include:

- deepeval (>=2.7.6)
- deepteam (>=0.0.9)
- Google API Client Libraries
- python-dotenv

## Environment Variables

The project uses environment variables for configuration. Create a `.env` file in the root directory with necessary credentials and settings.

## Contributing

1. Follow the existing code structure and style
2. Update documentation as needed

