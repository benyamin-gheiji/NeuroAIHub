import requests
from bs4 import BeautifulSoup
import io
import PyPDF2

def fetch_text(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        if url.lower().endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(resp.content))
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        else:
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "footer", "header", "nav"]):
                tag.decompose()
            text = " ".join(soup.stripped_strings)
        return text
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return ""
