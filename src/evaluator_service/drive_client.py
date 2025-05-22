import os
import json
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleDriveClient:
    def __init__(self, credentials_json: str):
        """Initialize the Google Drive client with service account credentials.
        
        Args:
            credentials_json (str): JSON string containing service account credentials
        """
        self.credentials = service_account.Credentials.from_service_account_info(
            json.loads(credentials_json),
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    def upload_file(self, file_path: str, folder_id: str) -> str:
        """Upload a file to a specific Google Drive folder.
        
        Args:
            file_path (str): Path to the file to upload
            folder_id (str): ID of the Google Drive folder to upload to
            
        Returns:
            str: ID of the uploaded file in Google Drive
        """
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(
            file_path,
            mimetype='text/csv',
            resumable=True
        )
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')