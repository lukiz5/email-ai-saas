import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_imap_host(host: str) -> bool:
    """Validate IMAP host format"""
    # Check for valid hostname or IP
    pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    return bool(re.match(pattern, host))


def validate_port(port: int) -> bool:
    """Validate port number"""
    return 1 <= port <= 65535


def sanitize_input(text: str, max_length: int = 50000) -> str:
    """Sanitize user input"""
    if not text:
        return ""

    # Truncate to max length
    text = text[:max_length]

    # Remove null bytes
    text = text.replace('\x00', '')

    return text.strip()
