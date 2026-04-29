import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

COMPANIES = [
    "Microsoft", "Tesla", "Amazon", "Netflix",
    "Meta", "Nvidia", "Apple Inc", "Goldman Sachs"
]

def fetch_headlines(company, days_back=7):
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f'"{company}"',
        "from": from_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error fetching news for {company}: {response.status_code}")
        return []

    articles = response.json().get("articles", [])
    headlines = []

    for article in articles:
        source_name = article.get("source", {}).get("name", "unknown")
        title = article.get("title", "")
        if not title or title == "[Removed]":
            continue
        headlines.append({
            "company": company,
            "outlet": source_name,
            "headline": title,
            "published_at": article.get("publishedAt", "")
        })

    print(f"Fetched {len(headlines)} headlines for {company}")
    return headlines