from bs4 import BeautifulSoup
import requests
from llama_index.core import Document

class CustomWebReader:
    def load_data(self, urls):
        documents = []
        for url in urls:
            try:
                print("fetching contents from " + url + ".....")
                response = requests.get(url,timeout=10) #timesout in 10secs if its taking long
                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove scripts, styles, and ads
                for script in soup(["script", "style", "header", "footer", "nav", "aside"]):
                    script.decompose()

                # Extract text from the body
                documents.append(Document(
                    text=soup.get_text(separator="\n", strip=True),
                    metadata={"url": url},
                ))
            except:
                print("failed loading contents from "+ url)

        return documents
