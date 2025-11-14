import os
from anthropic import Anthropic
from typing import Dict, Any, List
import json

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5-20250929"


async def summarize_email(email_text: str, email_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Summarize email using Claude Sonnet 4.5

    Args:
        email_text: The email content to summarize
        email_metadata: Optional metadata (subject, from, date, etc.)

    Returns:
        Dictionary with summary, actions, and priority
    """

    # Build context
    context = ""
    if email_metadata:
        if email_metadata.get('subject'):
            context += f"Subject: {email_metadata['subject']}\n"
        if email_metadata.get('from'):
            context += f"From: {email_metadata['from']}\n"
        if email_metadata.get('date'):
            context += f"Date: {email_metadata['date']}\n"
        context += "\n"

    context += f"Email Content:\n{email_text}"

    prompt = f"""Please analyze this email and provide:

1. A concise summary (2-3 sentences)
2. Key action items (if any)
3. Priority level (1-5, where 5 is most urgent)

{context}

Respond in JSON format:
{{
  "summary": "Brief summary here",
  "actions": ["action 1", "action 2"],
  "priority": 3,
  "key_points": ["point 1", "point 2"]
}}"""

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        # Parse JSON response
        result = json.loads(response_text)

        return {
            "summary": result.get("summary", ""),
            "actions": result.get("actions", []),
            "priority": result.get("priority", 3),
            "key_points": result.get("key_points", [])
        }

    except Exception as e:
        print(f"AI summarization error: {e}")
        return {
            "summary": "Error generating summary",
            "actions": [],
            "priority": 3,
            "key_points": []
        }


async def generate_smart_reply(email_text: str, tone: str = "professional") -> str:
    """
    Generate a smart reply to an email

    Args:
        email_text: The email to reply to
        tone: Desired tone (professional, friendly, brief)

    Returns:
        Generated reply text
    """

    prompt = f"""Generate a {tone} reply to this email. Keep it concise and appropriate.

Email:
{email_text}

Reply:"""

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text.strip()

    except Exception as e:
        print(f"Smart reply error: {e}")
        return "Error generating reply"


async def extract_tasks(emails: List[str]) -> List[Dict[str, Any]]:
    """
    Extract tasks from multiple emails

    Args:
        emails: List of email texts

    Returns:
        List of extracted tasks
    """

    combined_emails = "\n\n---\n\n".join(emails)

    prompt = f"""Extract all action items and tasks from these emails. Return as JSON array.

{combined_emails}

Format:
[
  {{"task": "Task description", "priority": "high/medium/low", "source": "Brief email context"}}
]"""

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        tasks = json.loads(response_text)

        return tasks

    except Exception as e:
        print(f"Task extraction error: {e}")
        return []


async def analyze_priority(email_text: str, email_metadata: Dict[str, Any] = None) -> int:
    """
    Analyze email priority (1-5 scale)

    Args:
        email_text: Email content
        email_metadata: Optional metadata

    Returns:
        Priority score (1-5)
    """

    context = ""
    if email_metadata:
        if email_metadata.get('subject'):
            context += f"Subject: {email_metadata['subject']}\n"
        if email_metadata.get('from'):
            context += f"From: {email_metadata['from']}\n"

    context += f"\n{email_text}"

    prompt = f"""Rate the priority/urgency of this email on a scale of 1-5, where:
1 = Low priority (newsletters, FYI)
2 = Below average
3 = Normal
4 = Important (requires response)
5 = Urgent (immediate action needed)

{context}

Respond with just the number (1-5):"""

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=10,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response = message.content[0].text.strip()
        priority = int(response)

        # Ensure valid range
        return max(1, min(5, priority))

    except Exception as e:
        print(f"Priority analysis error: {e}")
        return 3
