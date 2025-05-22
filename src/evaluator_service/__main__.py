import os
from dotenv import load_dotenv
from datetime import datetime

from evaluator_service.kustomer_client import KustomerClient
from evaluator_service.test_case_builder import TestCaseBuilder
from evaluator_service.evaluator import ConversationEvaluator
from evaluator_service.reporter import EvaluationReporter

def main():
    load_dotenv()

    deepeval_key = os.getenv("DEEPEVAL_API_KEY")
    kustomer_key = os.getenv("KUSTOMER_API_KEY")
    assigned_user_id = os.getenv("KUSTOMER_ASSIGNED_USER_ID")  
    queue_id = os.getenv("KUSTOMER_QUEUE_ID")

    print(f"Kustomer API Key {kustomer_key}")
    print(f"Assigned User ID: {assigned_user_id}")
    print(f"Queue ID: {queue_id}")

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

if __name__ == "__main__":
    main()
