from typing import Generator

from bs4 import BeautifulSoup
from requests import Session

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def get_all_children(url:str)->Generator:
    """Get all children of a url."""
    session = Session()
    response = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True,recursive=True):
        yield link.get("href")
        
        
for link in get_all_children("https://boto3.amazonaws.com/v1/documentation/api/latest/index.html"):
    print("https://boto3.amazonaws.com/v1/documentation/api/latest/"+link) if link.endswith(".html") else None
