import os
import requests
from enum import Enum
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from serpapi.google_search import GoogleSearch
from helpers import dprint

Provider = Enum("Provider", "Google DuckDuckGo")


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


def search(search_query, provider=Provider.Google, fetch_docs=False, max_results=20):
    results = None
    if provider == Provider.DuckDuckGo:
        results = DDGS().text(search_query, max_results=max_results)
        urls = [result["href"] for result in results]
    else:
        params = {
            "api_key": os.getenv("SERP_API_KEY"),
            "engine": "google",
            "q": search_query,
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "num": max_results,
        }
        results = GoogleSearch(params).get_dict()
        urls = [result["link"] for result in results["organic_results"]]

    if fetch_docs:
        all_content = []
        for url in urls:
            dprint(f"Fetching content from: {url}")
            page_content = extract_page_content(url)
            all_content.append(page_content)
        return set(all_content)
    else:
        return urls
