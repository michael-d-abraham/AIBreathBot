"""Web scraper for breathing exercise URLs (HTML and PDF)."""

from pathlib import Path
from typing import List, Dict
from io import BytesIO
import requests
from bs4 import BeautifulSoup

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None


def read_urls_from_file(url_file_path: Path) -> List[str]:
    """Read URLs from a text file, one URL per line.
    
    Args:
        url_file_path: Path to the text file containing URLs
        
    Returns:
        List of cleaned URLs (strips whitespace and quotes)
    """
    if not url_file_path.exists():
        raise FileNotFoundError(f"URL file not found: {url_file_path}")
    
    urls = []
    with open(url_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                # Remove quotes if present
                line = line.strip('"\'')
                urls.append(line)
    
    return urls


def is_pdf_url(url: str, content_type: str = None) -> bool:
    """Check if URL points to a PDF file.
    
    Args:
        url: The URL to check
        content_type: Optional Content-Type header from response
        
    Returns:
        True if URL appears to be a PDF
    """
    # Check Content-Type header first (most reliable)
    if content_type:
        if 'application/pdf' in content_type.lower():
            return True
    
    # Check URL extension
    url_lower = url.lower()
    if url_lower.endswith('.pdf') or '.pdf?' in url_lower or '.pdf#' in url_lower:
        return True
    
    # Check common PDF URL patterns
    if '/pdf' in url_lower or '/pdfExtended' in url_lower:
        return True
    
    return False


def extract_pdf_content_from_file(pdf_path: Path) -> tuple[str, str]:
    """Extract text content from a local PDF file.
    
    Args:
        pdf_path: Path to the local PDF file
        
    Returns:
        Tuple of (title, content)
    """
    if PdfReader is None:
        raise ImportError(
            "PDF extraction requires pypdf or PyPDF2. "
            "Install with: pip install pypdf"
        )
    
    pdf_reader = PdfReader(str(pdf_path))
    
    # Extract title from PDF metadata or first page
    title = ""
    if pdf_reader.metadata and pdf_reader.metadata.title:
        title = pdf_reader.metadata.title
    elif pdf_reader.metadata and pdf_reader.metadata.get('/Title'):
        title = str(pdf_reader.metadata.get('/Title'))
    
    # Extract text from all pages
    text_parts = []
    for page_num, page in enumerate(pdf_reader.pages):
        try:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        except Exception as e:
            # Skip pages that can't be extracted
            continue
    
    content = '\n\n'.join(text_parts)
    # Normalize whitespace
    content = ' '.join(content.split())
    
    # Use filename as title if no title found
    if not title:
        title = pdf_path.stem.replace('_', ' ').replace('-', ' ')
        if not title or len(title) < 3:
            title = "PDF Document"
    
    return title, content


def extract_pdf_content(response: requests.Response) -> tuple[str, str]:
    """Extract text content from a PDF response.
    
    Args:
        response: HTTP response containing PDF data
        
    Returns:
        Tuple of (title, content)
    """
    if PdfReader is None:
        raise ImportError(
            "PDF extraction requires pypdf or PyPDF2. "
            "Install with: pip install pypdf"
        )
    
    pdf_file = BytesIO(response.content)
    pdf_reader = PdfReader(pdf_file)
    
    # Extract title from PDF metadata or first page
    title = ""
    if pdf_reader.metadata and pdf_reader.metadata.title:
        title = pdf_reader.metadata.title
    elif pdf_reader.metadata and pdf_reader.metadata.get('/Title'):
        title = str(pdf_reader.metadata.get('/Title'))
    
    # Extract text from all pages
    text_parts = []
    for page_num, page in enumerate(pdf_reader.pages):
        try:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        except Exception as e:
            # Skip pages that can't be extracted
            continue
    
    content = '\n\n'.join(text_parts)
    # Normalize whitespace
    content = ' '.join(content.split())
    
    # Use URL as title if no title found
    if not title:
        title = response.url.split('/')[-1].replace('.pdf', '')
        if not title or len(title) < 3:
            title = "PDF Document"
    
    return title, content


def scrape_url(url: str, timeout: int = 10) -> Dict[str, str]:
    """Scrape a single URL and extract cleaned text content (HTML or PDF).
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'url', 'title', 'content', 'status', and 'error'
    """
    result = {
        'url': url,
        'title': '',
        'content': '',
        'status': 'success',
        'error': None
    }
    
    try:
        # Fetch the page/content
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Check if it's a PDF
        content_type = response.headers.get('Content-Type', '')
        is_pdf = is_pdf_url(url, content_type)
        
        if is_pdf:
            # Handle PDF extraction
            try:
                title, content = extract_pdf_content(response)
                result['title'] = title
                result['content'] = content
                
                if not content:
                    result['status'] = 'warning'
                    result['error'] = 'No text content extracted from PDF'
            except ImportError as e:
                result['status'] = 'error'
                result['error'] = str(e)
            except Exception as e:
                result['status'] = 'error'
                result['error'] = f'PDF extraction error: {e}'
        else:
            # Handle HTML extraction
            # Read response text (only for non-PDF)
            response_text = response.text
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Extract title
            if soup.title and soup.title.string:
                result['title'] = soup.title.string.strip()
            else:
                result['title'] = url
            
            # Remove unwanted tags
            for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
                tag.decompose()
            
            # Extract text from relevant tags
            text_parts = []
            for tag in soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']):
                text = tag.get_text(' ', strip=True)
                if text:
                    text_parts.append(text)
            
            # Join and clean text
            content = ' '.join(text_parts)
            # Normalize whitespace
            content = ' '.join(content.split())
            
            result['content'] = content
            
            if not content:
                result['status'] = 'warning'
                result['error'] = 'No content extracted'
        
    except requests.exceptions.Timeout:
        result['status'] = 'error'
        result['error'] = f'Request timeout after {timeout} seconds'
    except requests.exceptions.HTTPError as e:
        result['status'] = 'error'
        result['error'] = f'HTTP error: {e}'
    except requests.exceptions.RequestException as e:
        result['status'] = 'error'
        result['error'] = f'Request failed: {e}'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Unexpected error: {e}'
    
    return result


def scrape_all_urls(url_file_path: Path, timeout: int = 10) -> List[Dict[str, str]]:
    """Scrape all URLs from a file.
    
    Args:
        url_file_path: Path to the text file containing URLs
        timeout: Request timeout in seconds for each URL
        
    Returns:
        List of dictionaries with scraping results for each URL
    """
    urls = read_urls_from_file(url_file_path)
    
    if not urls:
        print(f"Warning: No URLs found in {url_file_path}")
        return []
    
    results = []
    for url in urls:
        # Detect file type for logging
        url_type = "PDF" if is_pdf_url(url) else "HTML"
        print(f"Scraping [{url_type}]: {url}")
        result = scrape_url(url, timeout=timeout)
        
        if result['status'] == 'success':
            print(f"  ✓ Success: {len(result['content'])} characters extracted")
        else:
            print(f"  ✗ {result['status'].upper()}: {result['error']}")
        
        results.append(result)
    
    return results


def main():
    """CLI entry point for testing the scraper."""
    import sys
    
    # Get URL file path from command line or use default
    if len(sys.argv) > 1:
        url_file = Path(sys.argv[1])
    else:
        script_dir = Path(__file__).parent
        url_file = script_dir / "papers" / "url.txt"
    
    print(f"Reading URLs from: {url_file}")
    results = scrape_all_urls(url_file)
    
    print(f"\n{'='*60}")
    print(f"Scraping Summary:")
    print(f"{'='*60}")
    print(f"Total URLs: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] == 'error')}")
    
    # Show content preview
    for result in results:
        if result['status'] == 'success' and result['content']:
            print(f"\n{result['title'][:80]}")
            print(f"Preview: {result['content'][:200]}...")


if __name__ == "__main__":
    main()
