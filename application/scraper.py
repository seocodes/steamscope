import requests 
from bs4 import BeautifulSoup


def fetch_deals():
    url = "https://store.steampowered.com/search/?specials=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    print(f"Page title: {soup.title.text}")
    print(f"Status code: {response.status_code}")
        

if __name__ == "__main__":
    fetch_deals()
