import re


def clean_email_text(text: str) -> str:
    """Clean and normalize email text"""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

    # Remove common email signatures
    signature_patterns = [
        r'--\s*\n.*',
        r'Sent from my (iPhone|iPad|Android)',
        r'Get Outlook for.*',
        r'________________________________.*',
    ]

    for pattern in signature_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    # Clean up excessive spaces
    text = re.sub(r' +', ' ', text)
    text = text.strip()

    return text


def remove_quoted_text(text: str) -> str:
    """Remove quoted/forwarded email content"""
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Skip lines that look like quoted text
        if line.strip().startswith('>'):
            continue

        # Stop at common forward/reply markers
        if re.match(r'^On .* wrote:$', line.strip()):
            break
        if re.match(r'^-+\s*Forwarded message\s*-+', line.strip(), re.IGNORECASE):
            break

        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)
