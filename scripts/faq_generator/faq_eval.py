import os
import logging
import argparse
from dotenv import load_dotenv
from deepeval import evaluate
from deepeval import login_with_confident_api_key
from deepeval.test_case import LLMTestCase
from deepeval.metrics import HallucinationMetric
import csv
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_faq_content(input_text, generated_content, context):
    """
    Evaluate FAQ content using DeepEval metrics.
    
    Args:
        input_text (str): The original input/prompt
        generated_content (str): The LLM-generated FAQ content
        context (str): The context/reference material to check against
    
    Returns:
        list: List of test cases for evaluation
    """
    # Convert context to a list of strings if it's not already
    context_list = [context] if isinstance(context, str) else context
    
    test_case = LLMTestCase(
        input=input_text,
        actual_output=generated_content,
        context=context_list
    )
    return [test_case]

def write_results_to_csv(results, filename):
    """
    Write evaluation results to a CSV file.
    
    Args:
        results: DeepEval evaluation results
        filename (str): Name of the CSV file to write to
    """
    headers = [
        'input',
        'actual_output',
        'metric_name',
        'score',
        'reason',
        'evaluation_cost',
    ]

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        
        for test_result in results.test_results:
            for metric_data in test_result.metrics_data:
                writer.writerow([
                    test_result.input,
                    test_result.actual_output,
                    metric_data.name,
                    metric_data.score,
                    metric_data.reason,
                    metric_data.evaluation_cost,
                ])

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Evaluate FAQ content using DeepEval metrics')
    parser.add_argument('--input', required=True, help='The input prompt text')
    parser.add_argument('--content', required=True, help='The generated FAQ content')
    parser.add_argument('--context', required=True, help='The reference context material')
    args = parser.parse_args()

    load_dotenv()
    deepeval_key = os.getenv("DEEPEVAL_API_KEY")
    
    if not deepeval_key:
        logger.error("DEEPEVAL_API_KEY not found in environment variables")
        return

    # Create test cases
    test_cases = evaluate_faq_content(args.input, args.content, args.context)

    # Initialize metrics
    hallucination_metric = HallucinationMetric(
        threshold=0.5,
        include_reason=True
    )

    # Login to DeepEval
    login_with_confident_api_key(deepeval_key)

    # Run evaluation
    if test_cases:
        result = evaluate(test_cases=test_cases, metrics=[hallucination_metric])
        
        # Create results directory if it doesn't exist
        os.makedirs('deepeval_results/faq_eval', exist_ok=True)
        
        # Write results to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'deepeval_results/faq_eval/eval_results_{timestamp}.csv'
        write_results_to_csv(result, filename)
        logger.info(f"Evaluation results written to {filename}")
    else:
        logger.warning("No test cases to evaluate.")

if __name__ == "__main__":
    main()
