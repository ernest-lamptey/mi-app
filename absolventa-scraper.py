import requests
import re
from bs4 import BeautifulSoup

def get_job_links(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve page {url}")
        return []
    
    # Parse the content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all job listings that mention "English"
    job_links = []
    # ids that contain "teaser_job_offer" are the job listings
    for job in soup.find_all('a', id=re.compile("teaser_job_offer")):
        extension = job['href']
        job_response = requests.get(f'https://www.absolventa.de{extension}')
        job_soup = BeautifulSoup(job_response.content, 'html.parser')
        job_text = job_soup.find(id="inbox-design-main").get_text().lower()
        if 'englisch' in job_text:
            job_details = {
                'link': f'https://www.absolventa.de{extension}',
                # 'description': job_text,
            }
            job_links.append(job_details)
    return job_links

def get_all_job_links(base_url, num_pages):
    all_job_links = []
    
    # Iterate through the specified number of pages
    for page_num in range(1, num_pages + 1):
        url = f"{base_url}?page={page_num}"
        job_links = get_job_links(url)
        all_job_links.extend(job_links)
    
    return all_job_links

# Base URL of the job listings (modify this to the actual website URL)
base_url = "https://www.absolventa.de/berufseinstieg"
# base_url = "https://www.absolventa.de/werkstudentenjobs"

# Number of pages to scrape (modify this as needed)
num_pages = 1

# Get all job links that require English
english_job_links = get_all_job_links(base_url, num_pages)

# Print the collected job links
# for link in english_job_links:
#     print(link)

print(f"Found {len(english_job_links)} job listings that require English")
status_message = f"Found {len(english_job_links)} job listings that require English"
