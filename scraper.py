"""Web scraper for breathing exercise URLs."""

from pathlib import Path
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


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


def scrape_url(url: str, timeout: int = 10) -> Dict[str, str]:
    """Scrape a single URL and extract cleaned text content.
    
    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'url', 'title', 'content', and 'status'
    """
    result = {
        'url': url,
        'title': '',
        'content': '',
        'status': 'success',
        'error': None
    }
    
    try:
        # Fetch the page
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        print(f"Scraping: {url}")
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
