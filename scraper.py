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
    if not url_file_path.exists():
        raise FileNotFoundError(f"URL file not found: {url_file_path}")
    
    urls = []
    with open(url_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                line = line.strip('"\'')
                urls.append(line)
    
    return urls


def is_pdf_url(url: str, content_type: str = None) -> bool:
    if content_type:
        if 'application/pdf' in content_type.lower():
            return True
    
    url_lower = url.lower()
    if url_lower.endswith('.pdf') or '.pdf?' in url_lower or '.pdf#' in url_lower:
        return True
    
    if '/pdf' in url_lower or '/pdfExtended' in url_lower:
        return True
    
    return False


def extract_pdf_content_from_file(pdf_path: Path) -> tuple[str, str]:
    if PdfReader is None:
        raise ImportError(
            "PDF extraction requires pypdf or PyPDF2. "
            "Install with: pip install pypdf"
        )
    
    pdf_reader = PdfReader(str(pdf_path))
    
    title = ""
    if pdf_reader.metadata and pdf_reader.metadata.title:
        title = pdf_reader.metadata.title
    elif pdf_reader.metadata and pdf_reader.metadata.get('/Title'):
        title = str(pdf_reader.metadata.get('/Title'))
    
    text_parts = []
    for page in pdf_reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        except Exception:
            continue
    
    content = '\n\n'.join(text_parts)
    content = ' '.join(content.split())
    
    if not title:
        title = pdf_path.stem.replace('_', ' ').replace('-', ' ')
        if not title or len(title) < 3:
            title = "PDF Document"
    
    return title, content


def extract_pdf_content(response: requests.Response) -> tuple[str, str]:
    if PdfReader is None:
        raise ImportError(
            "PDF extraction requires pypdf or PyPDF2. "
            "Install with: pip install pypdf"
        )
    
    pdf_file = BytesIO(response.content)
    pdf_reader = PdfReader(pdf_file)
    
    title = ""
    if pdf_reader.metadata and pdf_reader.metadata.title:
        title = pdf_reader.metadata.title
    elif pdf_reader.metadata and pdf_reader.metadata.get('/Title'):
        title = str(pdf_reader.metadata.get('/Title'))
    
    text_parts = []
    for page in pdf_reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        except Exception:
            continue
    
    content = '\n\n'.join(text_parts)
    content = ' '.join(content.split())
    
    if not title:
        title = response.url.split('/')[-1].replace('.pdf', '')
        if not title or len(title) < 3:
            title = "PDF Document"
    
    return title, content


def scrape_url(url: str, timeout: int = 10) -> Dict[str, str]:
    result = {
        'url': url,
        'title': '',
        'content': '',
        'status': 'success',
        'error': None
    }
    
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        is_pdf = is_pdf_url(url, content_type)
        
        if is_pdf:
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
            response_text = response.text
            soup = BeautifulSoup(response_text, 'html.parser')
            
            if soup.title and soup.title.string:
                result['title'] = soup.title.string.strip()
            else:
                result['title'] = url
            
            for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
                tag.decompose()
            
            text_parts = []
            for tag in soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']):
                text = tag.get_text(' ', strip=True)
                if text:
                    text_parts.append(text)
            
            content = ' '.join(text_parts)
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
    urls = read_urls_from_file(url_file_path)
    
    if not urls:
        print(f"Warning: No URLs found in {url_file_path}")
        return []
    
    results = []
    for url in urls:
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
    import sys
    
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
    
    for result in results:
        if result['status'] == 'success' and result['content']:
            print(f"\n{result['title'][:80]}")
            print(f"Preview: {result['content'][:200]}...")


if __name__ == "__main__":
    main()
