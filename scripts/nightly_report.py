#!/usr/bin/env python3
"""
Nightly report script for chatbot evaluation. Fetches real conversations, evaluates, and writes results to CSV/Drive.
"""
import os
from dotenv import load_dotenv
from datetime import datetime
from evaluator_service.kustomer_client import KustomerClient
from evaluator_service.test_case_builder import TestCaseBuilder
from evaluator_service.evaluator import ConversationEvaluator
from evaluator_service.reporter import EvaluationReporter

def main():
    load_dotenv()

    # Add Google Drive folder ID to environment variables
    drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not drive_folder_id:
        print("Warning: GOOGLE_DRIVE_FOLDER_ID not set. Google Drive upload will be skipped.")

    deepeval_key = os.getenv("DEEPEVAL_API_KEY")
    kustomer_key = os.getenv("KUSTOMER_API_KEY")
    assigned_user_id = os.getenv("KUSTOMER_ASSIGNED_USER_ID")  
    queue_id = os.getenv("KUSTOMER_QUEUE_ID")

    kustomer = KustomerClient(api_key=kustomer_key, assigned_user_id=assigned_user_id, queue_id=queue_id)
    conversations_data = kustomer.fetch_yesterdays_conversations()

    test_cases = []
    for convo in conversations_data:
        convo_id = convo.get("id")
        if not convo_id:
            continue
        messages = kustomer.fetch_single_conversation(convo_id)
        transcript = TestCaseBuilder.kustomer_messages_to_transcript(messages)
        if transcript:
            test_case = TestCaseBuilder.build_conversation_test_case(transcript, convo_id)
            test_cases.append(test_case)

    if not test_cases:
        print("No test cases found. Exiting.")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    convo_csv = f'deepeval_results/convo_eval/conversations_{timestamp}.csv'
    EvaluationReporter.write_conversations_to_csv(test_cases, convo_csv)
    print(f"Wrote conversations to {convo_csv}")

    evaluator = ConversationEvaluator(deepeval_api_key=deepeval_key)
    results = evaluator.evaluate(test_cases)

    eval_csv = f'deepeval_results/convo_eval/eval_results_{timestamp}.csv'
    EvaluationReporter.write_evaluation_results_to_csv(results, eval_csv)
    print(f"Wrote evaluation results to {eval_csv}")

    # Test Google Drive upload if folder ID is provided
    if drive_folder_id:
        try:
            print("Attempting to upload files to Google Drive...")
            convo_file_id = EvaluationReporter.upload_to_google_drive(convo_csv, drive_folder_id)
            print(f"Successfully uploaded conversations file. File ID: {convo_file_id}")
            
            eval_file_id = EvaluationReporter.upload_to_google_drive(eval_csv, drive_folder_id)
            print(f"Successfully uploaded evaluation results file. File ID: {eval_file_id}")
        except Exception as e:
            print(f"Failed to upload files to Google Drive: {str(e)}")
    else:
        print("Skipping Google Drive upload as GOOGLE_DRIVE_FOLDER_ID is not set.")

if __name__ == "__main__":
    main() 