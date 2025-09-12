import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    """
    Cleans the extracted text by removing excessive newlines and whitespace.
    """
    # Split text into lines, strip whitespace from each line, and remove empty lines
    lines = (line.strip() for line in text.splitlines())
    # Rejoin the lines with a single newline, creating a cleaner text block
    return '\n'.join(line for line in lines if line)

def scrape_job_description(url):
    """
    Attempts to scrape the main text content from a job posting URL using a tiered
    search strategy for better accuracy and broader compatibility.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # --- TIER 1: Highly Specific and Common Selectors ---
        # This list contains selectors that are very likely to be the main job description.
        # We search for these first. The list is ordered by likely relevance.
        specific_selectors = [
            {'tag': 'div', 'attrs': {'class': re.compile(r'job-description|jobDetailsSection|job-details|description', re.I)}},
            {'tag': 'div', 'attrs': {'id': re.compile(r'job-description|jobDetailsSection|job-details|description', re.I)}},
            {'tag': 'div', 'attrs': {'class': 'job-post-content'}},
        ]
        
        # --- TIER 2: Semantic HTML Tags ---
        # If specific selectors fail, we fall back to semantic tags which often
        # wrap the main content of a page.
        generic_selectors = [
            {'tag': 'article', 'attrs': {}},
            {'tag': 'main', 'attrs': {}},
        ]

        job_description_container = None

        # --- Execute Tier 1 Search ---
        for selector in specific_selectors:
            job_description_container = soup.find(selector['tag'], **selector['attrs'])
            if job_description_container:
                print(f"Found content with specific selector: {selector}")
                break
        
        # --- Execute Tier 2 Search if Tier 1 Failed ---
        if not job_description_container:
            for selector in generic_selectors:
                job_description_container = soup.find(selector['tag'], **selector['attrs'])
                if job_description_container:
                    print(f"Found content with generic selector: {selector}")
                    break
        
        # --- Process and Return Text ---
        if job_description_container:
            # If a container was found, extract and clean its text
            return clean_text(job_description_container.get_text(separator='\n'))
        else:
            # --- TIER 3: Last Resort Fallback ---
            # If no specific or generic container is found, fall back to the whole body,
            # but still clean the text to remove as much noise as possible.
            print("Warning: No specific container found. Falling back to the entire page body.")
            return clean_text(soup.body.get_text(separator='\n'))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return f"Error: Could not fetch the URL. Please check the link and your connection. Details: {e}"
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        return f"Error: An unexpected error occurred. The site may be blocking scrapers. Details: {e}"