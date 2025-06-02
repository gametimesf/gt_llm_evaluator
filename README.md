# Chatbot Evaluator Service

A modular service for static LLM evaluation of customer conversations.

## Requirements

- Python 3.12 or higher
- Dependencies are managed through `pyproject.toml`

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install dependencies:

```bash
pip install -e .
```

## Available Scripts

### Conversation Simulation

`scripts/simulate_convo.py`

- Simulates conversations for testing and evaluation purposes
- Usage: `python scripts/simulate_convo.py`

### Pre-merge Checks

`scripts/pre_merge_check.py`

- Runs validation checks before merging code changes
- Usage: `python scripts/pre_merge_check.py`

### Nightly Report Generation

`scripts/nightly_report.py`

- Generates daily evaluation reports
- Usage: `python scripts/nightly_report.py`

### Main Evaluation Script

`convo_eval.py`

- Core evaluation script for analyzing conversations
- Usage: `python convo_eval.py`

## Project Structure

- `src/` - Source code directory
- `scripts/` - Utility scripts for various tasks
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

