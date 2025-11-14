from bs4 import BeautifulSoup
import re


def html_to_text(html_content: str) -> str:
    """Convert HTML email to clean text"""
    if not html_content:
        return ""

    # Parse HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove script and style elements
    for element in soup(['script', 'style', 'head', 'title', 'meta', '[document]']):
        element.decompose()

    # Get text
    text = soup.get_text()

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def extract_links(html_content: str) -> list:
    """Extract all links from HTML email"""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    links = []

    for link in soup.find_all('a', href=True):
        links.append({
            'text': link.get_text().strip(),
            'url': link['href']
        })

    return links
