#!/usr/bin/env python3
"""
Scrape Databricks MLflow 3 docs from docs.databricks.com/aws/en/mlflow3/
Converts HTML to clean Markdown and saves to docs/databricks/
"""

import re
import time
import random
import sys
from pathlib import Path

import requests
import html2text
from bs4 import BeautifulSoup

# ── Config ──────────────────────────────────────────────────────────────────
SITEMAP_FILE = Path("/home/ph19/.cursor/projects/home-ph19-workspace-ai-evals/agent-tools/3614b761-3e0d-41a5-90fd-08ebec937b5b.txt")
OUT_DIR = Path("/home/ph19/workspace/ai-evals/docs/databricks")
MIN_DELAY = 1.5   # seconds between requests
MAX_DELAY = 3.5
MAX_RETRIES = 3

SESSION_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# ── HTML → Markdown converter setup ─────────────────────────────────────────
h2t = html2text.HTML2Text()
h2t.ignore_links = False
h2t.ignore_images = True
h2t.ignore_tables = False
h2t.body_width = 0          # no wrapping
h2t.protect_links = True
h2t.unicode_snob = True


def extract_urls(sitemap_path: Path) -> list[str]:
    content = sitemap_path.read_text()
    urls = re.findall(r"https://docs\.databricks\.com/aws/en/mlflow3[^<\s]+", content)
    return sorted(set(urls))


def url_to_output_path(url: str) -> Path:
    # strip https://docs.databricks.com/aws/en/
    slug = url.replace("https://docs.databricks.com/aws/en/", "")
    slug = slug.rstrip("/")
    if not slug:
        slug = "index"
    return OUT_DIR / (slug.replace("/", "__") + ".md")


def extract_main_content(html: str, url: str) -> str:
    """Extract the main doc body, stripping nav/sidebar/footer."""
    soup = BeautifulSoup(html, "html.parser")

    # Docusaurus main content is in <article> or .theme-doc-markdown
    article = (
        soup.find("article")
        or soup.find(class_="theme-doc-markdown")
        or soup.find(attrs={"role": "main"})
        or soup.find("main")
    )

    if article:
        # Remove nav elements that leak into article
        for tag in article.find_all(["nav", "aside", "footer"]):
            tag.decompose()
        content_html = str(article)
    else:
        content_html = html

    md = h2t.handle(content_html)

    # Add source URL as front-matter comment
    header = f"<!-- source: {url} -->\n\n"
    return header + md.strip()


def fetch_with_retry(session: requests.Session, url: str) -> requests.Response | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 60))
                print(f"  429 rate-limited, sleeping {wait}s …", flush=True)
                time.sleep(wait)
                continue
            if resp.status_code == 200:
                return resp
            print(f"  HTTP {resp.status_code} on attempt {attempt}", flush=True)
        except requests.RequestException as e:
            print(f"  Request error attempt {attempt}: {e}", flush=True)
        time.sleep(5 * attempt)
    return None


def main():
    urls = extract_urls(SITEMAP_FILE)
    print(f"Found {len(urls)} mlflow3 URLs in sitemap", flush=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(SESSION_HEADERS)

    ok, skipped, failed = 0, 0, []

    for i, url in enumerate(urls, 1):
        out_path = url_to_output_path(url)

        if out_path.exists():
            print(f"[{i:3}/{len(urls)}] SKIP  {out_path.name}", flush=True)
            skipped += 1
            continue

        print(f"[{i:3}/{len(urls)}] GET   {url}", flush=True)
        resp = fetch_with_retry(session, url)

        if resp is None:
            print(f"  FAILED: {url}", flush=True)
            failed.append(url)
            continue

        try:
            md = extract_main_content(resp.text, url)
            out_path.write_text(md, encoding="utf-8")
            print(f"        → {out_path.name} ({len(md):,} chars)", flush=True)
            ok += 1
        except Exception as e:
            print(f"  Parse error: {e}", flush=True)
            failed.append(url)

        # Polite pacing
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    print(f"\n{'─'*60}", flush=True)
    print(f"Done: {ok} saved, {skipped} skipped, {len(failed)} failed", flush=True)
    if failed:
        print("Failed URLs:", flush=True)
        for u in failed:
            print(f"  {u}", flush=True)


if __name__ == "__main__":
    main()
