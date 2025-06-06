import requests
import json
from typing import List, Dict
from datetime import datetime, timedelta
import os

class KustomerClient:
    """
    Handles API interactions with the Kustomer platform.
    Responsible for fetching historical and single conversations.
    """

    BASE_URL = "https://api.kustomerapp.com/v1"

    def __init__(self, api_key: str, assigned_user_id: str, queue_id: str):
        """
        Initialize the client with the required API key, assigned user ID, and queue ID.
        """
        api_key_env = os.getenv('KUSTOMER_API_KEY')
        print(f"KUSTOMER_API_KEY env: {'*' * (len(api_key_env) - 4) + api_key_env[-4:] if api_key_env else 'NOT SET'}")
        print('api_key', api_key)
        self.api_key = api_key
        self.assigned_user_id = assigned_user_id
        self.queue_id = queue_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def fetch_yesterdays_conversations(self) -> List[Dict]:
        """
        Fetch conversations from yesterday using assigned_user_id and queue_id.
        Args:
            limit: Maximum number of conversations to fetch.
        Returns:
            List of conversation metadata dicts.
        """
        search_url = "https://api.kustomerapp.com/v1/customers/search"
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        and_filters = []
        if self.assigned_user_id:
            and_filters.append({"conversation_assigned_users": {"equals": self.assigned_user_id}})
        if self.queue_id:
            and_filters.append({"conversation_queue": {"equals": self.queue_id}})
        and_filters.append({"conversation_created_at": {"lte": yesterday}})
        search_payload = {
            "and": and_filters,
            "or": [],
            "fields": [],
            "queryContext": "conversation",
            "sort": [{"conversation_created_at": "desc"}],
            "timeZone": "America/Los_Angeles",
        }
        try:
            response = requests.post(search_url, headers=self.headers, json=search_payload)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.RequestException as e:
            print(f"Error making request to Kustomer API: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return []

    def fetch_single_conversation(self, convo_id: str) -> Dict:
        """
        Fetch the details/messages for a single conversation by ID.
        Args:
            convo_id: The conversation ID to fetch.
        Returns:
            Dict containing the conversation's message data.
        """
        convo_url = f"{self.BASE_URL}/conversations/{convo_id}/messages"
        try:
            response = requests.get(convo_url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.RequestException:
            return {} 