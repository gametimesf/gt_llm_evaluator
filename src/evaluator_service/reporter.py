import csv
import os
from typing import List
from .drive_client import GoogleDriveClient
class EvaluationReporter:
    """
    Handles reporting of evaluation results, including CSV generation and (future) Google Drive upload.
    """

    @staticmethod
    def write_conversations_to_csv(conversations: List, filename: str):
        """
        Write conversations to a CSV file with formatting.
        Args:
            conversations (list): List of conversation test cases.
            filename (str): Name of the CSV file to write to.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
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

    @staticmethod
    def write_evaluation_results_to_csv(results: object, filename: str):
        """
        Write evaluation results to a CSV file.
        Args:
            results (object): Evaluation results object.
            filename (str): Name of the CSV file to write to.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
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
            for test_result in results.test_results:
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
                    if i % 2 == 1:
                        writer.writerow([])

    @staticmethod
    def upload_to_google_drive(filepath: str, folder_id: str) -> str:
        """
        Upload a file to Google Drive.
        Args:
            filepath (str): Path to the file to upload.
            folder_id (str): ID of the Google Drive folder to upload to.
        Returns:
            str: ID of the uploaded file in Google Drive
        """
        credentials = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
        if not credentials:
            raise ValueError("GOOGLE_DRIVE_CREDENTIALS environment variable not set")
            
        drive_client = GoogleDriveClient(credentials)
        return drive_client.upload_file(filepath, folder_id)