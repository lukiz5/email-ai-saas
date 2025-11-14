import os
from typing import List, Dict, Any
import msal
import httpx


class OutlookService:
    """Outlook/Microsoft 365 integration using Microsoft Graph API"""

    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
    SCOPES = ['Mail.Read', 'User.Read']

    def __init__(self, access_token: str):
        """
        Initialize Outlook service with access token

        Args:
            access_token: Microsoft Graph access token
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    async def list_messages(self, max_results: int = 10, folder: str = 'inbox') -> List[Dict[str, Any]]:
        """
        List messages from Outlook inbox

        Args:
            max_results: Maximum number of messages
            folder: Mail folder (inbox, sent, etc.)

        Returns:
            List of message dictionaries
        """
        url = f'{self.GRAPH_API_ENDPOINT}/me/mailFolders/{folder}/messages'
        params = {
            '$top': max_results,
            '$select': 'id,subject,from,receivedDateTime,bodyPreview,body'
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()
                messages = []

                for msg in data.get('value', []):
                    messages.append({
                        'id': msg['id'],
                        'subject': msg.get('subject', ''),
                        'from': msg.get('from', {}).get('emailAddress', {}).get('address', ''),
                        'date': msg.get('receivedDateTime', ''),
                        'body': msg.get('body', {}).get('content', ''),
                        'body_type': msg.get('body', {}).get('contentType', 'text'),
                        'preview': msg.get('bodyPreview', '')
                    })

                return messages

        except httpx.HTTPError as error:
            print(f"Outlook API error: {error}")
            return []

    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get full message details

        Args:
            message_id: Message ID

        Returns:
            Dictionary with message details
        """
        url = f'{self.GRAPH_API_ENDPOINT}/me/messages/{message_id}'

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                msg = response.json()

                return {
                    'id': msg['id'],
                    'subject': msg.get('subject', ''),
                    'from': msg.get('from', {}).get('emailAddress', {}).get('address', ''),
                    'date': msg.get('receivedDateTime', ''),
                    'body': msg.get('body', {}).get('content', ''),
                    'body_type': msg.get('body', {}).get('contentType', 'text'),
                    'to': [addr.get('emailAddress', {}).get('address', '')
                           for addr in msg.get('toRecipients', [])],
                    'cc': [addr.get('emailAddress', {}).get('address', '')
                           for addr in msg.get('ccRecipients', [])]
                }

        except httpx.HTTPError as error:
            print(f"Error getting message {message_id}: {error}")
            return None

    async def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search messages

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            List of matching messages
        """
        url = f'{self.GRAPH_API_ENDPOINT}/me/messages'
        params = {
            '$search': f'"{query}"',
            '$top': max_results,
            '$select': 'id,subject,from,receivedDateTime,bodyPreview'
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()
                return data.get('value', [])

        except httpx.HTTPError as error:
            print(f"Search error: {error}")
            return []

    async def get_unread_count(self) -> int:
        """Get count of unread messages"""
        url = f'{self.GRAPH_API_ENDPOINT}/me/mailFolders/inbox'

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                data = response.json()
                return data.get('unreadItemCount', 0)

        except httpx.HTTPError as error:
            print(f"Error getting unread count: {error}")
            return 0


def get_outlook_oauth_url() -> str:
    """Generate Outlook OAuth URL"""
    client_id = os.getenv('MICROSOFT_CLIENT_ID')
    redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:8000/api/outlook/callback')
    tenant = os.getenv('MICROSOFT_TENANT_ID', 'common')

    authority = f'https://login.microsoftonline.com/{tenant}'

    app = msal.PublicClientApplication(
        client_id,
        authority=authority
    )

    scopes = ['Mail.Read', 'User.Read']

    # Get authorization URL
    auth_url = app.get_authorization_request_url(
        scopes,
        redirect_uri=redirect_uri
    )

    return auth_url


async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token"""
    client_id = os.getenv('MICROSOFT_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
    redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:8000/api/outlook/callback')
    tenant = os.getenv('MICROSOFT_TENANT_ID', 'common')

    authority = f'https://login.microsoftonline.com/{tenant}'

    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )

    result = app.acquire_token_by_authorization_code(
        code,
        scopes=['Mail.Read', 'User.Read'],
        redirect_uri=redirect_uri
    )

    return result
