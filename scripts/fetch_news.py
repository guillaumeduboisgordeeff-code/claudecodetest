import json
import feedparser
from datetime import datetime, timedelta
from pathlib import Path
from dateutil import parser as dateparser


def load_sources():
    with open("sources.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_memory():
    memory_path = Path("memory.json")
    if memory_path.exists():
        with open(memory_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_urls": [], "last_run": None}


def save_memory(memory):
    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def parse_date(entry):
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6])
            except Exception:
                pass
    for attr in ("published", "updated"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return dateparser.parse(val, ignoretz=True)
            except Exception:
                pass
    return None


def fetch_articles(sources, memory, days=7):
    cutoff = datetime.now() - timedelta(days=days)
    new_articles = []
    processed_urls = set(memory.get("processed_urls", []))

    for source in sources:
        if not source.get("active") or not source.get("rss"):
            continue
        try:
            feed = feedparser.parse(source["rss"])
            for entry in feed.entries:
                url = entry.get("link", "").strip()
                if not url or url in processed_urls:
                    continue

                published = parse_date(entry)
                if published and published < cutoff:
                    continue

                summary = entry.get("summary", "") or entry.get("description", "")
                summary = summary[:600].strip()

                new_articles.append({
                    "title": entry.get("title", "").strip(),
                    "url": url,
                    "summary": summary,
                    "published": published.isoformat() if published else None,
                    "source_name": source["name"],
                    "source_category": source["category"],
                })
                processed_urls.add(url)

        except Exception as e:
            print(f"⚠ Erreur source '{source['name']}': {e}")

    return new_articles, processed_urls


def main():
    sources_data = load_sources()
    memory = load_memory()

    articles, all_processed_urls = fetch_articles(sources_data["sources"], memory)

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
