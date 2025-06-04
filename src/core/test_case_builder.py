from deepeval.test_case import LLMTestCase, ConversationalTestCase
from typing import List, Dict

class TestCaseBuilder:
    """
    Converts raw Kustomer conversation/message data into test cases suitable for evaluation.
    """

    @staticmethod
    def kustomer_messages_to_transcript(message_data: List[Dict]) -> List[Dict]:
        """
        Convert Kustomer message data to a transcript-style list of input/output dicts.
        Args:
            message_data (list): List of message dicts from Kustomer.
        Returns:
            list: List of dicts with 'input' and 'actual_output' keys.
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

    @staticmethod
    def build_conversation_test_case(transcript_data: List[Dict], convo_id: str) -> ConversationalTestCase:
        """
        Build a ConversationalTestCase from transcript data.
        Args:
            transcript_data (list): List of conversation turns with input and actual_output.
            convo_id (str): The conversation ID.
        Returns:
            ConversationalTestCase: The constructed test case.
        """
        turns = []
        for turn in transcript_data:
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

    @staticmethod
    def parse_simulated_conversations_csv(csv_path: str) -> list:
        """
        Parse a CSV of simulated conversations and return a list of ConversationalTestCase objects.
        Each conversation is separated by 3 empty lines (as in the reporting format).
        """
        import csv
        test_cases = []
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            transcript = []
            convo_id = 'simulated'
            for row in reader:
                if not any(row):  # empty row
                    if transcript:
                        test_case = TestCaseBuilder.build_conversation_test_case(transcript, convo_id)
                        test_cases.append(test_case)
                        transcript = []
                    continue
                if row[0].startswith('Turn'):
                    transcript.append({"input": row[1], "actual_output": row[2]})
            if transcript:
                test_case = TestCaseBuilder.build_conversation_test_case(transcript, convo_id)
                test_cases.append(test_case)
        return test_cases 