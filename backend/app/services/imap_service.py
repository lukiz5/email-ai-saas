from typing import List, Dict, Any
from imapclient import IMAPClient
import email
from email.header import decode_header
import ssl


class IMAPService:
    """Generic IMAP email service"""

    def __init__(self, host: str, email_addr: str, password: str, port: int = 993, use_ssl: bool = True):
        """
        Initialize IMAP connection

        Args:
            host: IMAP server host (e.g., imap.gmail.com)
            email_addr: Email address
            password: Email password or app password
            port: IMAP port (default 993 for SSL)
            use_ssl: Whether to use SSL
        """
        self.host = host
        self.email = email_addr
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.client = None

    def connect(self) -> bool:
        """
        Connect to IMAP server

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_ssl:
                context = ssl.create_default_context()
                self.client = IMAPClient(self.host, port=self.port, ssl_context=context)
            else:
                self.client = IMAPClient(self.host, port=self.port, ssl=False)

            self.client.login(self.email, self.password)
            return True

        except Exception as e:
            print(f"IMAP connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.client:
            try:
                self.client.logout()
            except:
                pass

    def list_messages(self, folder: str = 'INBOX', max_results: int = 10, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        List messages from folder

        Args:
            folder: Mail folder name
            max_results: Maximum number of messages
            unread_only: Only fetch unread messages

        Returns:
            List of message dictionaries
        """
        if not self.client:
            if not self.connect():
                return []

        try:
            self.client.select_folder(folder, readonly=True)

            # Search for messages
            if unread_only:
                messages = self.client.search(['UNSEEN'])
            else:
                messages = self.client.search(['ALL'])

            # Get most recent messages
            messages = list(messages)[-max_results:]

            message_list = []

            # Fetch message data
            if messages:
                fetch_data = self.client.fetch(messages, ['ENVELOPE', 'RFC822'])

                for msg_id, data in fetch_data.items():
                    envelope = data.get(b'ENVELOPE')
                    raw_email = data.get(b'RFC822')

                    if raw_email:
                        parsed_msg = self._parse_message(raw_email)
                        parsed_msg['id'] = str(msg_id)
                        message_list.append(parsed_msg)

            return message_list

        except Exception as e:
            print(f"Error listing messages: {e}")
            return []

    def get_message(self, message_id: int) -> Dict[str, Any]:
        """
        Get single message

        Args:
            message_id: Message ID

        Returns:
            Message dictionary
        """
        if not self.client:
            if not self.connect():
                return None

        try:
            fetch_data = self.client.fetch([message_id], ['RFC822'])

            if message_id in fetch_data:
                raw_email = fetch_data[message_id][b'RFC822']
                parsed_msg = self._parse_message(raw_email)
                parsed_msg['id'] = str(message_id)
                return parsed_msg

            return None

        except Exception as e:
            print(f"Error getting message: {e}")
            return None

    def _parse_message(self, raw_email: bytes) -> Dict[str, Any]:
        """Parse raw email bytes to dictionary"""
        msg = email.message_from_bytes(raw_email)

        # Decode subject
        subject = ''
        if msg['Subject']:
            decoded_subject = decode_header(msg['Subject'])
            subject = ''.join(
                [str(part, encoding or 'utf-8') if isinstance(part, bytes) else part
                 for part, encoding in decoded_subject]
            )

        # Get body
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
                elif content_type == 'text/html' and not body:
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                body = str(msg.get_payload())

        return {
            'subject': subject,
            'from': msg['From'],
            'to': msg['To'],
            'date': msg['Date'],
            'body': body
        }

    def get_folders(self) -> List[str]:
        """Get list of available folders"""
        if not self.client:
            if not self.connect():
                return []

        try:
            folders = self.client.list_folders()
            return [folder[2] for folder in folders]

        except Exception as e:
            print(f"Error getting folders: {e}")
            return []

    def get_unread_count(self, folder: str = 'INBOX') -> int:
        """Get count of unread messages"""
        if not self.client:
            if not self.connect():
                return 0

        try:
            self.client.select_folder(folder, readonly=True)
            messages = self.client.search(['UNSEEN'])
            return len(messages)

        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0


def test_imap_connection(host: str, email_addr: str, password: str, port: int = 993) -> bool:
    """
    Test IMAP connection

    Returns:
        True if connection successful
    """
    service = IMAPService(host, email_addr, password, port)
    success = service.connect()
    service.disconnect()
    return success
