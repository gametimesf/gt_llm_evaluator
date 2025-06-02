import os
from typing import Dict, List
import requests
from dotenv import load_dotenv
import csv
from datetime import datetime

from deepeval.conversation_simulator import ConversationSimulator

async def model_callback(input_text: str) -> str:
        """
        Callback function to interact with the API.

        Args:
            input_text: The input prompt to send to the model

        Returns:
            The model's response as a string
        """
        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret:
            print("WARNING: JWT_SECRET environment variable not set")
            jwt_secret = "test-token"
            
        payload = {
            "userMessage": input_text,
            "purchaseConfirmationNumber": "ZT268QDK3D"
        }
        
        print(f"Sending request to API with prompt: {input_text[:50]}...")
        
        try:
            # Use the DOT_SERVER_URL from .env or fallback to localhost
            response = requests.post(
                "http://localhost:3000/api/dot/test-response",
                json=payload,
                headers={
                    "Authorization": f"Bearer {jwt_secret}",
                    "Accept": "application/json"
                },
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error response: {response.text}")
                return f"Error: {response.status_code}"
                
            try:
                response_data = response.json()
                result = response_data.get("text", "")
                print(f"Received response: {result[:50]}...")
                return result
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return f"Error parsing response: {str(e)}"
        except Exception as e:
            print(f"Exception during API call: {e}")
            return f"Error: {str(e)}"

def write_conversations_to_csv(test_cases, filename):
    """
    Write conversations to a CSV file with 3 empty lines between each conversation.
    
    Args:
        test_cases (list): List of conversation test cases
        filename (str): Name of the CSV file to write to
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Turn', 'Input', 'Actual Output'])
        
        for i, convo in enumerate(test_cases):
            for j, turn in enumerate(convo.turns):
                writer.writerow([f"Turn {j+1}", turn.input, turn.actual_output])
            
            # Add 3 empty lines between conversations
            if i < len(test_cases) - 1:
                writer.writerow([])
                writer.writerow([])
                writer.writerow([])

def main():
    print("Loading environment variables...")
    load_dotenv()
    
    print("Starting conversation simulation...")

    user_intentions = [
         "I can't find my tickets",
         "I need to cancel my order",
         "I need help with my homework",
    ]

    user_profile_items = ["phone number", "verifcation code"]

    simulator = ConversationSimulator(
        user_intentions=user_intentions,
        user_profile_items=user_profile_items
    )

    test_cases = simulator.simulate(
        model_callback=model_callback,
        min_turns=5,
        max_turns=20,
        num_conversations=2
    )

    # Create output directory if it doesn't exist
    os.makedirs('conversation_results', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'conversation_results/simulated_conversations_{timestamp}.csv'
    
    # Write conversations to CSV
    write_conversations_to_csv(test_cases, csv_filename)
    print(f"Conversations written to {csv_filename}")
  
if __name__ == "__main__":
    main()