import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from html.parser import HTMLParser

class MultiSearchParser(HTMLParser):
    def __init__(self, search_terms):
        super().__init__()
        self.search_terms = [term.lower() for term in search_terms]
        self.matches = {term: None for term in self.search_terms}  # term: context

    def handle_data(self, data):
        data_lower = data.lower()
        for term in self.search_terms:
            if self.matches[term] is None and term in data_lower:
                self.matches[term] = data.strip()

def get_all_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = set()
        for tag in soup.find_all('a', href=True):
            full_url = urljoin(url, tag['href'])
            if "/jam/" in full_url: 
                links.add(full_url)

        return links
    except requests.RequestException as e:
        print(f"Error {url}: {e}")
        return set()

def get_my_money(url):
    white_list = ["$", "USD"]
    black_list = ["This jam is over.", "This jam is now over.", "Submissions due in"]
    search_terms = white_list + black_list
    response = requests.get(url)
    parser = MultiSearchParser(search_terms)
    parser.feed(response.text)

    do_print = False
    for item in black_list:
        if parser.matches[item.lower()]:
            return

    for item in white_list:
        if parser.matches[item.lower()]:
            do_print = parser.matches[item.lower()]

    if do_print and len(do_print) > 200:
        do_print = False

    if do_print:
        print("\n" + "="*60)
        print(f"🎯  Possible Match Found at: \033[94m{url}\033[0m")
        print("-" * 60)
        print(f"💬  Context:", highlight_phrases(do_print, white_list))
        print("="*60 + "\n")

def highlight_phrases(text, phrases, color="\033[92m", is_regex=False):
    for phrase in phrases:
        pattern = phrase if is_regex else re.escape(phrase)
        text = re.sub(f"({pattern})", rf"{color}\1\033[0m", text, flags=re.IGNORECASE)
    return text

if __name__ == "__main__":
    target_url = "https://itch.io/jams"
    urls = get_all_links(target_url)
    
    for link in urls:
        get_my_money(link)
