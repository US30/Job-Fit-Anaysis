import requests
from bs4 import BeautifulSoup

def scrape_job_description(url):
    """
    Attempts to scrape the main text content from a job posting URL.
    
    NOTE: This is a generic scraper and will NOT work for all websites.
    The HTML tags and classes must be adapted for specific job sites.
    """
    try:
        # Set a User-Agent header to mimic a browser and avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # --- THIS IS THE PART THAT NEEDS CUSTOMIZATION ---
        # We need to find the HTML element that contains the job description.
        # This requires inspecting the website's HTML to find the right tag and class.
        # Below are some common examples, but you WILL need to change this.
        
        job_description_container = None
        
        # Example for a site that uses <div class="job-description">
        if not job_description_container:
            job_description_container = soup.find('div', class_='job-description')
            
        # Example for a site that uses <div id="jobDetailsSection">
        if not job_description_container:
            job_description_container = soup.find('div', id='jobDetailsSection')
            
        # Example for a site that uses a more generic class
        if not job_description_container:
            job_description_container = soup.find('div', class_='job-post-content')
        
        # If a container was found, extract its text
        if job_description_container:
            # .get_text() extracts all text from the container and its children
            # separator='\n' adds newlines between tags for better readability
            # strip=True removes leading/trailing whitespace
            return job_description_container.get_text(separator='\n', strip=True)
        else:
            # If no specific container is found, fall back to the whole body
            # This will be noisy but is better than nothing.
            return soup.body.get_text(separator='\n', strip=True)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return f"Error: Could not fetch the URL. Please check the link and your connection. Details: {e}"
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        return f"Error: An unexpected error occurred. The site may be blocking scrapers. Details: {e}"