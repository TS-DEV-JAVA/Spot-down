# youtube_scrape.py
import sys
import requests
import re
import urllib.parse

def scrape_first_url(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    html = requests.get(url, headers=headers).text

    match = re.search(r'"videoId":"(.*?)"', html)
    if match:
        return f"https://www.youtube.com/watch?v={match.group(1)}"
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: youtube_scrape.py <query>")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    print(scrape_first_url(query))
