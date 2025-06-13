from deepeval import evaluate, login_with_confident_api_key
from deepeval.test_case.conversational_test_case import TurnParams
from deepeval.metrics import ConversationalGEval
from typing import List

class ConversationEvaluator:
    """
    Handles evaluation of conversation test cases using defined metrics and prompts.
    """

    def __init__(self, deepeval_api_key: str):
        """
        Initialize the evaluator with the required API key and set up metrics.
        """
        login_with_confident_api_key(deepeval_api_key)
        self.metrics = [
            ConversationalGEval(
                name="Correctness",
                evaluation_steps=[
                    "Turns will alternate between a customer message and achatbot response.",
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
                evaluation_params=[TurnParams.CONTENT],
                threshold=0.85
            ),
            ConversationalGEval(
                name="Verification",
                evaluation_steps=[
                    "Turns will alternate between a customer message and achatbot response.",
                    "Verification is required when the user asks about:",
                    "- Ticket delivery status or timing",
                    "- Purchase details or order status",
                    "- Account-specific information",
                    "- Ticket transfers or resale options",
                    "- Payment issues",
                    "Verification is NOT required for:",
                    "- General questions about the platform",
                    "- How to use the app",
                    "- General policies or procedures relating to Gametime's platform",
                    "- Non-account specific information",
                    "- User's that drop off of the conversation before asking quesitons requiring verification.",
                    "The verification flow will follow these steps in order:",
                    "1. Chatbot initiates by asking the user for their phone number (must include 'phone number' in response)",
                    "2. User provides phone number (typically 10 digits, may include formatting)",
                    "3. Chatbot confirms sending verification code (must mention 'verification code')",
                    "4. User provides 6-digit verification code to complete the process.",
                    "Additional requirements:",
                    "- The verification flow is usually completed in 3 turns",
                    "- The chatbot must not reveal sensitive account information before verification code is sent",
                    "- The chatbot should handle failed verification attempts gracefully",
                    "- The chatbot should not ask for verification multiple times in the same conversation",
                    "Score based on:",
                    "- Proper identification of when verification is needed (30%)",
                    "- Correct execution of the verification flow (40%)",
                    "- Appropriate handling of verification failures (20%)",
                    "- Maintaining security by not revealing sensitive info before verification (10%)",
                    "Provide a detailed reasoning for the evaluation, highlighting both successful aspects and areas of concern.",
                ],
                evaluation_params=[TurnParams.CONTENT],
                threshold=0.7
            )
        ]

    def evaluate(self, test_cases: List) -> object:
        """
        Run evaluation on a list of test cases using the configured metrics.
        Args:
            test_cases (list): List of ConversationalTestCase objects.
        Returns:
            Evaluation results object.
        """
        return evaluate(test_cases=test_cases, metrics=self.metrics) 