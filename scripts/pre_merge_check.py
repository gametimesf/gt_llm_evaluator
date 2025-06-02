#!/usr/bin/env python3
"""
Pre-merge check script for chatbot evaluation. Reads simulated conversations, evaluates them, and exits with pass/fail for CI.
"""
import os
import sys
from dotenv import load_dotenv
from evaluator_service.test_case_builder import TestCaseBuilder
from evaluator_service.evaluator import ConversationEvaluator

def main():
    load_dotenv()
    deepeval_key = os.getenv("DEEPEVAL_API_KEY")
    csv_path = "mock_data/simulated_conversations.csv"
    if not os.path.exists(csv_path):
        print(f"Simulated conversations CSV not found at {csv_path}")
        sys.exit(1)

    test_cases = TestCaseBuilder.parse_simulated_conversations_csv(csv_path)
    if not test_cases:
        print("No test cases found in simulated conversations CSV.")
        sys.exit(1)

    evaluator = ConversationEvaluator(deepeval_api_key=deepeval_key)
    results = evaluator.evaluate(test_cases)

    all_passed = True
    for test_result in results.test_results:
        if not test_result.success:
            all_passed = False
            break
    if all_passed:
        print("All simulated conversation tests passed.")
        sys.exit(0)
    else:
        print("Some simulated conversation tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 