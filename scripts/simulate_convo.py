#!/usr/bin/env python3
"""
Script to generate simulated conversations for chatbot evaluation.
Uses a configured API endpoint to generate responses and writes conversations to CSV.
"""
import os
import logging
from typing import Dict, List
import requests
from dotenv import load_dotenv
import csv
from datetime import datetime

from deepeval.conversation_simulator import ConversationSimulator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConversationGenerator:
    """Handles generation of simulated conversations using an API endpoint."""
    
    def __init__(self, api_url: str = "https://gametime-ai-chatbot-staging.vercel.app/api/dot/test-response"):
        """
        Initialize the conversation generator.
        
        Args:
            api_url (str): URL of the API endpoint to use for responses
        """
        self.api_url = api_url
        self.jwt_secret = os.getenv("JWT_SECRET", "test-token")
        
        # Define standard user intentions for simulation
        self.user_intentions = [
            "I can't find my tickets",
            "I need to cancel my order",
            "I need help with my homework",
        ]
        
        # Define user profile items that might be requested
        self.user_profile_items = [
            "phone number",
            "verification code"
        ]

    async def model_callback(self, input_text: str) -> str:
        """
        Callback function to interact with the API.

        Args:
            input_text: The input prompt to send to the model

        Returns:
            The model's response as a string
        """
        payload = {
            "userMessage": input_text,
            "purchaseConfirmationNumber": "ZT268QDK3D"
        }
        
        logger.info(f"Sending request to API with prompt: {input_text[:50]}...")
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.jwt_secret}",
                    "Accept": "application/json"
                },
                timeout=30
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Error response: {response.text}")
                return f"Error: {response.status_code}"
                
            try:
                response_data = response.json()
                result = response_data.get("text", "")
                logger.info(f"Received response: {result[:50]}...")
                return result
            except Exception as e:
                logger.error(f"Error parsing JSON: {e}")
                return f"Error parsing response: {str(e)}"
        except Exception as e:
            logger.error(f"Exception during API call: {e}")
            return f"Error: {str(e)}"

    def generate_conversations(self, num_conversations: int = 2, 
                             min_turns: int = 5, 
                             max_turns: int = 20) -> List:
        """
        Generate simulated conversations.
        
        Args:
            num_conversations (int): Number of conversations to generate
            min_turns (int): Minimum number of turns per conversation
            max_turns (int): Maximum number of turns per conversation
            
        Returns:
            List: List of generated conversation test cases
        """
        logger.info(f"Generating {num_conversations} conversations...")
        
        simulator = ConversationSimulator(
            user_intentions=self.user_intentions,
            user_profile_items=self.user_profile_items
        )
        
        test_cases = simulator.simulate(
            model_callback=self.model_callback,
            min_turns=min_turns,
            max_turns=max_turns,
            num_conversations=num_conversations
        )
        
        logger.info(f"Successfully generated {len(test_cases)} conversations")
        return test_cases

    def write_conversations_to_csv(self, test_cases: List, output_dir: str = "mock_data") -> str:
        """
        Write conversations to a CSV file.
        
        Args:
            test_cases (List): List of conversation test cases
            output_dir (str): Directory to write the CSV file to
            
        Returns:
            str: Path to the generated CSV file
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = os.path.join(output_dir, f'simulated_conversations_{timestamp}.csv')
        
        with open(csv_filename, 'w', newline='') as csvfile:
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
        
        logger.info(f"Conversations written to {csv_filename}")
        return csv_filename

def main():
    """Main entry point for the script."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize generator
        generator = ConversationGenerator()
        
        # Generate conversations
        test_cases = generator.generate_conversations(
            num_conversations=2,
            min_turns=5,
            max_turns=20
        )
        
        # Write to CSV
        csv_path = generator.write_conversations_to_csv(test_cases)
        logger.info(f"Successfully generated conversations at {csv_path}")
        
    except Exception as e:
        logger.error(f"Error generating conversations: {str(e)}")
        raise

if __name__ == "__main__":
    main()