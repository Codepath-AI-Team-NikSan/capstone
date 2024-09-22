import requests
from bs4 import BeautifulSoup
import urllib.parse
from duckduckgo_search import DDGS
from enum import Enum

Provider = Enum("Provider", "Google DuckDuckGo")


# Search on Google using BS4 manually and get individually fetch the results
def google_search(query, max_results=10):
    query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={query}&num={max_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for g in soup.find_all("div", class_="g"):
            title = g.find("h3")
            link = g.find("a", href=True)

            if title and link:
                results.append({"title": title.text, "href": link["href"]})
        return results
    else:
        print(f"Error: {response.status_code}")
        return []


def extract_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove scripts, styles, and ads
            for script in soup(["script", "style", "header", "footer", "nav", "aside"]):
                script.decompose()

            # Extract text
            content = soup.get_text(separator="\n", strip=True)
            return content
        else:
            print(f"Failed to retrieve {url}: {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def search(
    search_query, provider=Provider.DuckDuckGo, fetch_docs=False, max_results=20
):
    results = None
    if provider == Provider.DuckDuckGo:
        results = DDGS().text(search_query, max_results=max_results)
    else:
        results = google_search(search_query)

    if fetch_docs:
        all_content = []
        for result in results:
            print(f"Fetching content from: {result['href']}")
            page_content = extract_page_content(result["href"])
            all_content.append(page_content)
        return set(all_content)
    else:
        return [result["href"] for result in results]
