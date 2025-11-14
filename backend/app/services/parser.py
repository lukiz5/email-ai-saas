import re
from typing import Dict, Any, Optional
from datetime import datetime
from ..utils.html_to_text import html_to_text
from ..utils.email_cleaner import clean_email_text, remove_quoted_text


def parse_email(raw_text: str, is_html: bool = False) -> Dict[str, Any]:
    """
    Powerful email parser that extracts structure from raw text or HTML

    Features:
    - Detects email boundaries
    - Extracts headers (From, Subject, Date)
    - Falls back to heuristics if missing
    - Detects signatures
    - Cleans HTML to text
    - Supports forwarded messages

    Args:
        raw_text: Raw email text or HTML
        is_html: Whether input is HTML

    Returns:
        Normalized dictionary with parsed email data
    """

    result = {
        'from': None,
        'to': None,
        'subject': None,
        'date': None,
        'body': '',
        'has_headers': False,
        'is_forwarded': False,
        'cleaned_body': ''
    }

    # Convert HTML to text if needed
    if is_html:
        raw_text = html_to_text(raw_text)

    # Try to extract headers
    headers_match = re.search(
        r'^(From:|Subject:|To:|Date:).*?(?=\n\n|\Z)',
        raw_text,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    if headers_match:
        result['has_headers'] = True
        header_text = headers_match.group(0)
        body_text = raw_text[headers_match.end():].strip()

        # Extract individual headers
        result['from'] = extract_header(header_text, 'From')
        result['to'] = extract_header(header_text, 'To')
        result['subject'] = extract_header(header_text, 'Subject')
        result['date'] = extract_header(header_text, 'Date')

        result['body'] = body_text
    else:
        # No headers found - treat entire text as body
        result['body'] = raw_text

        # Try heuristic subject extraction (first line if short)
        lines = raw_text.strip().split('\n')
        if lines and len(lines[0]) < 100:
            result['subject'] = lines[0].strip()
            result['body'] = '\n'.join(lines[1:]).strip()

    # Check if forwarded
    if re.search(r'(Forwarded message|---------- Forwarded|Begin forwarded message)',
                 raw_text, re.IGNORECASE):
        result['is_forwarded'] = True

    # Clean body
    cleaned = clean_email_text(result['body'])
    cleaned = remove_quoted_text(cleaned)
    result['cleaned_body'] = cleaned

    return result


def extract_header(header_text: str, header_name: str) -> Optional[str]:
    """Extract a specific header value"""
    pattern = rf'{header_name}:\s*(.+?)(?=\n[A-Z][a-z]+:|\n\n|\Z)'
    match = re.search(pattern, header_text, re.IGNORECASE | re.DOTALL)

    if match:
        value = match.group(1).strip()
        # Clean up multi-line headers
        value = re.sub(r'\s+', ' ', value)
        return value

    return None


def parse_email_thread(thread_text: str) -> list[Dict[str, Any]]:
    """
    Parse an email thread into individual messages

    Args:
        thread_text: Full thread text

    Returns:
        List of parsed emails
    """

    # Split on common thread separators
    separators = [
        r'\n\s*On .+ wrote:\s*\n',
        r'\n-{5,}\s*Forwarded message\s*-{5,}\n',
        r'\n>{5,}\s*\n',
        r'\nFrom:.*?\nSent:.*?\nTo:.*?\n'
    ]

    emails = [thread_text]

    for separator in separators:
        new_emails = []
        for email in emails:
            parts = re.split(separator, email, flags=re.IGNORECASE)
            new_emails.extend(parts)
        emails = new_emails

    # Parse each email
    parsed_emails = []
    for email_text in emails:
        if email_text.strip():
            parsed = parse_email(email_text)
            if parsed['cleaned_body']:  # Only include if has content
                parsed_emails.append(parsed)

    return parsed_emails


def extract_sender_email(from_field: str) -> Optional[str]:
    """Extract email address from From field"""
    if not from_field:
        return None

    # Try to find email in angle brackets
    match = re.search(r'<(.+?)>', from_field)
    if match:
        return match.group(1).strip()

    # Try to find email pattern
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', from_field)
    if match:
        return match.group(0).strip()

    return None


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse email date string to datetime"""
    if not date_str:
        return None

    # Common email date formats
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%d %b %Y %H:%M:%S %z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue

    return None
