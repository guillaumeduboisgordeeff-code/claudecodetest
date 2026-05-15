import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dateutil import parser as dateparser

ROOT = Path(__file__).parent.parent
SOURCES_PATH = ROOT / "sources.json"
MEMORY_PATH = ROOT / "memory.json"
BRIEFINGS_DIR = ROOT / "briefings"

LOOKBACK_DAYS = 7
TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; VeilleIABot/1.0)"

# Namespaces utilisés par les flux Atom et RSS
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def load_sources():
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [s for s in data.get("sources", []) if s.get("active", True)]


def load_memory():
    if MEMORY_PATH.exists():
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_urls": [], "last_run": None}


def save_memory(memory):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_date(raw):
    if not raw:
        return None
    try:
        return dateparser.parse(raw, ignoretz=True)
    except Exception:
        return None


def find_text(element, paths):
    """Try multiple element paths and return the first non-empty text."""
    for path in paths:
        node = element.find(path, NS) if ":" in path else element.find(path)
        if node is not None and node.text:
            return node.text.strip()
    return ""


def parse_rss_item(item):
    title = find_text(item, ["title"])
    link = find_text(item, ["link"])
    summary = find_text(item, ["description", "content:encoded"])
    published_raw = find_text(item, ["pubDate", "dc:date"])
    return {
        "title": title,
        "link": link,
        "summary": summary,
        "published": parse_date(published_raw),
    }


def parse_atom_entry(entry):
    title = find_text(entry, ["atom:title"])
    link = ""
    link_node = entry.find("atom:link", NS)
    if link_node is not None:
        link = link_node.get("href", "").strip()
    summary = find_text(entry, ["atom:summary", "atom:content"])
    published_raw = find_text(entry, ["atom:published", "atom:updated"])
    return {
        "title": title,
        "link": link,
        "summary": summary,
        "published": parse_date(published_raw),
    }


def fetch_feed(source):
    rss_url = source.get("rss")
    if not rss_url:
        return []
    try:
        response = requests.get(
            rss_url,
            timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"},
        )
        response.raise_for_status()
    except Exception as e:
        print(f"⚠ {source['name']} : échec téléchargement ({e})")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"⚠ {source['name']} : XML invalide ({e})")
        return []

    items = []
    tag = root.tag.lower()

    # RSS 2.0 : <rss><channel><item>
    for item in root.iter("item"):
        items.append(parse_rss_item(item))

    # Atom : <feed><entry>
    if "feed" in tag or root.find("atom:entry", NS) is not None:
        for entry in root.findall("atom:entry", NS):
            items.append(parse_atom_entry(entry))

    return items


def fetch_articles(memory):
    processed_urls = set(memory.get("processed_urls", []))
    seen_urls = set()
    new_articles = []

    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    sources = load_sources()

    for source in sources:
        entries = fetch_feed(source)
        kept = 0
        for entry in entries:
            url = entry["link"]
            if not url or url in processed_urls or url in seen_urls:
                continue
            if entry["published"] and entry["published"] < cutoff:
                continue
            seen_urls.add(url)
            new_articles.append({
                "title": strip_html(entry["title"]),
                "url": url,
                "summary": strip_html(entry["summary"])[:600],
                "published": entry["published"].isoformat() if entry["published"] else None,
                "source_name": source["name"],
                "source_category": source.get("category", "news"),
            })
            kept += 1
        print(f"  → {source['name']} : {kept} articles retenus sur {len(entries)}")

    return new_articles, seen_urls | processed_urls


def main():
    memory = load_memory()
    articles, all_processed_urls = fetch_articles(memory)

    date_str = datetime.now().strftime("%Y-%m-%d")
    BRIEFINGS_DIR.mkdir(exist_ok=True)
    output_path = BRIEFINGS_DIR / f"{date_str}_raw.json"

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
