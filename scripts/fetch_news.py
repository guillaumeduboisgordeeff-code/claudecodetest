import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from dateutil import parser as dateparser

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/everything"


def load_sources():
    sources_path = Path(__file__).parent.parent / "sources.json"
    with open(sources_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    domains = []
    for s in data.get("sources", []):
        if not s.get("active", True):
            continue
        url = s.get("url", "")
        if url:
            host = urlparse(url).netloc.lstrip("www.")
            if host:
                domains.append(host)
    return domains


def load_memory():
    memory_path = Path("memory.json")
    if memory_path.exists():
        with open(memory_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_urls": [], "last_run": None}


def save_memory(memory):
    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def fetch_from_newsapi(query, from_date, to_date, domains=None):
    params = {
        "apiKey": NEWS_API_KEY,
        "q": query,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 30,
    }
    if domains:
        params["domains"] = ",".join(domains)

    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print(f"⚠ Erreur NewsAPI (query='{query}'): {e}")
        return []


def fetch_articles(memory, days=7):
    processed_urls = set(memory.get("processed_urls", []))
    new_articles = []
    seen_urls = set()
    allowed_domains = load_sources()

    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    from_str = from_date.strftime("%Y-%m-%dT%H:%M:%S")
    to_str = to_date.strftime("%Y-%m-%dT%H:%M:%S")

    # Recherche 1 : publications des acteurs majeurs IA
    domain_articles = fetch_from_newsapi(
        query="artificial intelligence",
        from_date=from_str,
        to_date=to_str,
        domains=allowed_domains,
    )

    # Recherche 2 : gouvernance IA en entreprise
    governance_articles = fetch_from_newsapi(
        query="\"AI governance\" OR \"artificial intelligence governance\" OR \"AI board\" OR \"AI regulation\" enterprise",
        from_date=from_str,
        to_date=to_str,
        domains=allowed_domains,
    )

    # Recherche 3 : responsabilité dirigeants face à l'IA
    leadership_articles = fetch_from_newsapi(
        query="\"AI risk\" OR \"AI strategy\" board directors CEO executives enterprise 2026",
        from_date=from_str,
        to_date=to_str,
        domains=allowed_domains,
    )

    all_raw = domain_articles + governance_articles + leadership_articles

    for item in all_raw:
        url = (item.get("url") or "").strip()
        if not url or url in processed_urls or url in seen_urls:
            continue
        seen_urls.add(url)

        published = None
        raw_date = item.get("publishedAt")
        if raw_date:
            try:
                published = dateparser.parse(raw_date, ignoretz=True)
            except Exception:
                pass

        source_name = (item.get("source") or {}).get("name", "Source inconnue")

        new_articles.append({
            "title": (item.get("title") or "").strip(),
            "url": url,
            "summary": (item.get("description") or item.get("content") or "")[:600].strip(),
            "published": published.isoformat() if published else None,
            "source_name": source_name,
            "source_category": "news",
        })

    return new_articles, seen_urls | processed_urls


def main():
    if not NEWS_API_KEY:
        print("⚠ Variable d'environnement NEWS_API_KEY manquante.")
        return

    memory = load_memory()
    articles, all_processed_urls = fetch_articles(memory)

    date_str = datetime.now().strftime("%Y-%m-%d")
    briefings_dir = Path("briefings")
    briefings_dir.mkdir(exist_ok=True)

    output_path = briefings_dir / f"{date_str}_raw.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "articles_count": len(articles),
            "articles": articles,
        }, f, ensure_ascii=False, indent=2)

    memory["processed_urls"] = list(all_processed_urls)
    memory["last_run"] = date_str
    save_memory(memory)

    print(f"✓ {len(articles)} nouveaux articles collectés — fichier : {output_path}")


if __name__ == "__main__":
    main()
