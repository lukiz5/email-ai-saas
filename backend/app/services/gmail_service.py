import os
import base64
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailService:
    """Gmail integration service using OAuth2"""

    def __init__(self, credentials_dict: Dict[str, Any]):
        """
        Initialize Gmail service with OAuth credentials

        Args:
            credentials_dict: Dictionary with token, refresh_token, etc.
        """
        self.credentials = Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )

        self.service = build('gmail', 'v1', credentials=self.credentials)

    def list_messages(self, max_results: int = 10, query: str = '') -> List[Dict[str, Any]]:
        """
        List messages from Gmail inbox

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query (e.g., 'is:unread')

        Returns:
            List of message dictionaries
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])
            message_list = []

            for msg in messages:
                message = self.get_message(msg['id'])
                if message:
                    message_list.append(message)

            return message_list

        except HttpError as error:
            print(f"Gmail API error: {error}")
            return []

    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get full message details

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with message details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

            # Get message body
            body = self._get_message_body(message['payload'])

            return {
                'id': message_id,
                'subject': subject,
                'from': from_addr,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }

        except HttpError as error:
            print(f"Error getting message {message_id}: {error}")
            return None

    def _get_message_body(self, payload: Dict) -> str:
        """Extract message body from payload"""
        body = ''

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body

    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search messages with advanced query

        Args:
            query: Gmail search query
            max_results: Maximum results

        Returns:
            List of matching messages
        """
        return self.list_messages(max_results=max_results, query=query)

    def get_unread_count(self) -> int:
        """Get count of unread messages"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread'
            ).execute()

            return results.get('resultSizeEstimate', 0)

        except HttpError as error:
            print(f"Error getting unread count: {error}")
            return 0


def get_gmail_oauth_url() -> str:
    """Generate Gmail OAuth URL for authentication"""
    # This would typically use google_auth_oauthlib.flow
    # For now, return a placeholder
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/gmail/callback')

    scopes = 'https://www.googleapis.com/auth/gmail.readonly'

    oauth_url = (
        f'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={client_id}&'
        f'redirect_uri={redirect_uri}&'
        f'response_type=code&'
        f'scope={scopes}&'
        f'access_type=offline&'
        f'prompt=consent'
    )

    return oauth_url
