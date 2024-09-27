import asyncio
import time

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from llama_index.core import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from helpers import dprint


class AsyncWebReader:
    def __init__(self, max_workers=10):
        # Setup Selenium options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument(
            "--disable-dev-shm-usage"
        )  # Overcome limited resource problems

        # Customize headers to avoid bot detection
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Set executable path for Selenium
        self.driver_options = chrome_options

        # Create a thread pool executor with a specified number of workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Timeout (in seconds) for AsyncWebReader to execute fetching contents
        self.timeout = 25

    def _fetch_content(self, url):
        dprint(f"Fetching content from {url}...")

        # Initialize WebDriver (Chrome)
        driver = webdriver.Chrome(options=self.driver_options)
        driver.get(url)

        # Wait for the page to fully load
        time.sleep(1.5)  # Adjust this wait time based on the website

        dprint(f"Parsing content from {url}...")

        # Use BeautifulSoup to parse the page content
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Close WebDriver after getting the page source
        driver.quit()

        # Remove unwanted elements
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.decompose()

        dprint(f"Done scraping content from {url}...")

        # Return the cleaned text content
        return Document(
            text=soup.get_text(separator="\n", strip=True),
            metadata={"url": url},
        )

    async def _fetch_content_async(self, url):
        # Run blocking content fetch in the custom thread pool executor with timeout
        loop = asyncio.get_event_loop()

        # Use futures to add a timeout for the content fetching
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._fetch_content, url),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            dprint(f"Timeout occurred while fetching content from {url}")
            return None
        except Exception as e:
            dprint(f"An error occurred while fetching content from {url}: {e}")
            return None

    async def load_data(self, urls):
        # Use asyncio.gather to fetch content from URLs concurrently
        tasks = [self._fetch_content_async(url) for url in urls]
        dprint("Done fetching content from URLs...")
        documents = await asyncio.gather(*tasks)

        # Filter out any None results from failed requests
        documents = [doc for doc in documents if doc is not None]

        return documents

    def close_executor(self):
        # Properly shutdown the executor
        self.executor.shutdown(wait=True)


if __name__ == "__main__":
    reader = AsyncWebReader()
    urls = ["https://www.google.com", "https://duckduckgo.com/"]
    documents = reader.load_data(urls)
    dprint(documents)
