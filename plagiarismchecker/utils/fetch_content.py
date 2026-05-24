import requests
from bs4 import BeautifulSoup


def fetch_page_text(url):

    try:

        headers = {
            "User-Agent":
            "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        paragraphs = soup.find_all("p")

        text = " ".join(
            p.get_text()
            for p in paragraphs
        )

        return text

    except Exception as e:

        print("FETCH ERROR:", e)

        return ""