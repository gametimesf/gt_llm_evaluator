import os
import logging
from dotenv import load_dotenv
from deepeval import evaluate
from deepeval import login_with_confident_api_key
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ConversationalTestCase
from deepeval.metrics import AnswerRelevancyMetric, GEval
import json
import requests
from datetime import datetime, timedelta
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_conversation_test_case(transcript_data, convo_id):
    """
    Build a ConversationalTestCase from transcript data.
    
    Args:
        transcript_data (list): List of conversation turns with input and actual_output
    
    Returns:
        ConversationalTestCase: The constructed test case
    """
    
    turns = []
    for i, turn in enumerate(transcript_data):      
        test_case = LLMTestCase(
            input=turn["input"],
            actual_output=turn["actual_output"],
        )
        turns.insert(0, test_case)
    
    convo_test_case = ConversationalTestCase(
        chatbot_role="Gametime Support Agent",
        turns=turns,
        additional_metadata={
            "convo_id": convo_id
        })
    return convo_test_case

def kustomer_messages_to_transcript(message_data):
    """
    Convert Kustomer message data to a transcript-style list of input/output dicts.
    Args:
        message_data (list): List of message dicts from kustomer_message_output.json['data']
    Returns:
        list: List of dicts with 'input' and 'actual_output' keys
    """
    transcript = []
    i = 0
    while i < len(message_data) - 1:
        msg = message_data[i]
        next_msg = message_data[i + 1]
        dir1 = msg["attributes"].get("direction")
        dir2 = next_msg["attributes"].get("direction")
        # Expect alternating in/out
        if dir1 == "in" and dir2 == "out":
            transcript.append({
                "input": msg["attributes"].get("preview", ""),
                "actual_output": next_msg["attributes"].get("preview", "")
            })
            i += 2
        else:
            i += 1
    return transcript

def write_conversations_to_csv(conversations, filename):
    """
    Write conversations to a CSV file with 3 empty lines between each conversation.
    
    Args:
        conversations (list): List of conversation test cases
        filename (str): Name of the CSV file to write to
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Turn', 'Input', 'Actual Output'])
        
        for i, convo in enumerate(conversations):
            for j, turn in enumerate(convo.turns):
                writer.writerow([f"Turn {j+1}", turn.input, turn.actual_output])
            
            # Add 3 empty lines between conversations
            if i < len(conversations) - 1:
                writer.writerow([])
                writer.writerow([])
                writer.writerow([])

def main():
    load_dotenv()

    deepeval_key = os.getenv("DEEPEVAL_API_KEY")
    kustomer_key = os.getenv("KUSTOMER_API_KEY")

    headers = {
        "Authorization": f"Bearer {kustomer_key}",
        "Content-Type": "application/json"
    }

    test_cases = []

    try:
        search_url = "https://api.kustomerapp.com/v1/customers/search"
        search_payload = {
                "and": [
                    {
                    "conversation_assigned_users": {
                        "equals": "676486cf01da6f779db108ce"
                    }
                    },
                    {
                    "conversation_queue": {
                        "equals": "676491dcaaea2f3995b2ba11"
                    }
                    },
                    {
                        "conversation_created_at": {
                            "lte": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                        }
                    }
                ],
                "or": [],
                "fields": [],
                "queryContext": "conversation",
                "sort": [
                    {
                    "conversation_created_at": "desc"
                    }
                ],
            "timeZone": "America/Los_Angeles"
        }
        search_response = requests.post(search_url, headers=headers, json=search_payload)
        search_convos = search_response.json().get('data', [])

        for convo in search_convos:
            convo_id = convo.get("id")
            if not convo_id:
                continue
            kustomer_convo_url = f"https://api.kustomerapp.com/v1/conversations/{convo_id}/messages"
            try:
                messages_response = requests.get(kustomer_convo_url, headers=headers)
                messages_response.raise_for_status()
                messages_data = messages_response.json().get('data', [])
                parsed_convo = kustomer_messages_to_transcript(messages_data)
                if parsed_convo:
                    convo_test_case = build_conversation_test_case(parsed_convo, convo_id)
                    test_cases.append(convo_test_case)
            except requests.RequestException as e:
                logger.error(f"Error fetching messages for convo {convo_id}: {e}")

    except requests.RequestException as e:
        logger.error(f"Error calling Kustomer API: {e}")

    # Write conversations to CSV
    if test_cases:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'deepeval_results/convo_eval/conversations_{timestamp}.csv'
        os.makedirs('deepeval_results/convo_eval', exist_ok=True)
        write_conversations_to_csv(test_cases, csv_filename)
        logger.info(f"Conversations written to {csv_filename}")

    login_with_confident_api_key(deepeval_key)

    # Custom correctness metric
    correctness_metric = GEval(
        name="Correctness",
        evaluation_steps=[
            "Input is the customer message, actual_output is the chatbot response.",
            "Determine if the user's query is related to the company's platform and services. If not, the chatbot should politely decline to assist.",
            "Evaluate whether the chatbot maintains appropriate boundaries - it should decline requests for: poems, rhymes, homework help, coding assistance, or any non-business related queries.",
            "Assess if the chatbot's responses are professional, clear, and directly address the user's legitimate business inquiries.",
            "Ensure the chatbot provides clear instructions and next steps when authentication is required.",
            
            "Determine if the chatbot successfully identifies and rejects attempts to: generate creative content, solve academic problems, or assist with coding.",
            "Verify that the chatbot maintains professional boundaries and does not engage in casual conversation or entertainment.",
            
            "Evaluate the clarity and professionalism of the chatbot's language and tone.",
            "Assess whether the chatbot provides complete and accurate information for legitimate business queries.",
            "Verify that the chatbot offers appropriate alternatives or next steps when it cannot fulfill a request.",
            
            "Provide a detailed reasoning for the evaluation, highlighting both successful aspects and areas of concern. Make sure to consider the full conversation flow and context.",
            "Score the response based on: functional correctness (50%), and response quality (50%)."
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7
    )

    verification_metric = GEval(
        name="Verification",
        evaluation_steps=[
            "Input is the customer message, actual_output is the chatbot response.",
            
            # Define what requires verification
            "Verification is required when the user asks about:",
            "- Ticket delivery status or timing",
            "- Purchase details or order status",
            "- Account-specific information",
            "- Ticket transfers or resale options",
            "- Refund eligibility or payment issues",
            
            # Define what does NOT require verification
            "Verification is NOT required for:",
            "- General questions about the platform",
            "- How to use the app",
            "- General policies or procedures",
            "- Non-account specific information",
            
            # Define the verification flow
            "The verification flow will follow these steps in order:",
            "1. Chatbot initiates by asking the user for their phone number (must include 'phone number' in response)",
            "2. User provides phone number (typically 10 digits, may include formatting)",
            "3. Chatbot confirms sending verification code (must mention 'verification code')",
            "4. User provides 6-digit verification code to complete the process.",
            
            # Additional requirements
            "Additional requirements:",
            "- The verification flow is usually completed in 3 turns",
            "- The chatbot must not reveal sensitive account information before verification code is sent",
            "- The chatbot should handle failed verification attempts gracefully",
            "- The chatbot should not ask for verification multiple times in the same conversation",
            
            # Scoring criteria
            "Score based on:",
            "- Proper identification of when verification is needed (30%)",
            "- Correct execution of the verification flow (40%)",
            "- Appropriate handling of verification failures (20%)",
            "- Maintaining security by not revealing sensitive info before verification (10%)",
            "Provide a detailed reasoning for the evaluation, highlighting both successful aspects and areas of concern.",

        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7
    )


    # Run evaluation
    if test_cases:
        result = evaluate(test_cases=test_cases, metrics=[correctness_metric, verification_metric])
        
        os.makedirs('deepeval_results/convo_eval', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'deepeval_results/convo_eval/eval_results_{timestamp}.csv'

        headers = [
            'convo_url',
            'overall_success',
            'metric_name',
            'score',
            'reason',
            'evaluation_cost',
            'retrieval_context',
        ]

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for test_result in result.test_results:
                for i, metric_data in enumerate(test_result.metrics_data):
                    convo_id = test_result.additional_metadata.get('convo_id') if test_result.additional_metadata else None
                    writer.writerow([
                        f"https://gametime.kustomerapp.com/app/conversations/{convo_id}",
                        metric_data.success,
                        metric_data.name,
                        metric_data.score,
                        metric_data.reason,
                        metric_data.evaluation_cost,
                        test_result.retrieval_context,
                    ])
                    # Add blank row after every 2 metric data rows
                    if i % 2 == 1:  # After every second metric
                        writer.writerow([])
    else:
        logger.warning("No test cases to evaluate.")

if __name__ == "__main__":
    main()


