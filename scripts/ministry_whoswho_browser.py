#!/usr/bin/env python3
"""Real-browser scraper for JS-shell ministry who's-who pages using Playwright.

Targets the Akamai-fronted Next.js / headless-WP sites that don't render via
curl. Uses browser automation to wait for tables/content to load, then parses
like the static scraper.
"""
import asyncio
import csv
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
APPEND = DATA / "ministry_officials_browser.csv"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

BROWSERS = ["meity", "dot", "dst", "dst-ai", "ipo", "fsi", "nsti", "sansad",
            "dsw", "fmeict"]
URLS = {
    "meity": "https://www.meity.gov.in/whoswho",
    "dot": "https://www.dot.gov.in/whos-who",
    "dst": "https://dst.gov.in/whos-who",
    "dst-ai": "https://airesearch.gov.in/whoswho",
    "ipo": "https://www.ipo.gov.in/whos-who",
    "fsi": "https://fsi.gov.in/en/whos-who",
    "nsti": "https://nsti.gov.in/who-s-who",
    "sansad": "https://pib.gov.in/whos-who",
    "dsw": "https://dsw.gov.in/whos-who",
    "fmeict": "https://fmeict.gov.in/whos-who",
}

async def scrape_one(browser_name, url):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_extra_http_headers({"User-Agent": UA})
        try:
            await page.goto(url, timeout=30000, wait_until="networkidle")
            await page.wait_for_load_state("networkidle")
            # wait for tables or "officer" headings
            try:
                await page.wait_for_selector("table, [class*='officer'], [class*='staff']",
                                            timeout=10000)
            except:
                pass
            html = await page.content()
            return browser_name, html
        except Exception as e:
            print(f"  {browser_name} load FAILED: {e}", file=sys.stderr)
            return browser_name, None
        finally:
            await browser.close()


async def main():
    from bs4 import BeautifulSoup
    # import parse_tables from the main module
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from ministry_whoswho import parse_tables

    print(f"browser scrape: {len(URLS)} sites", file=sys.stderr)
    results = []
    for browser_name, url in URLS.items():
        print(f"  {browser_name}: {url}", file=sys.stderr)
        name, html = await scrape_one(browser_name, url)
        if html is None:
            continue
        rows = parse_tables(html, url)
        if rows:
            results.extend([{"ministry": browser_name.upper(), "website": url, **r} for r in rows])
            print(f"    -> {len(rows)} officials", file=sys.stderr)
        else:
            print(f"    -> no tables parsed", file=sys.stderr)

    if not results:
        print("no results from browser scrape", file=sys.stderr)
        return

    with APPEND.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ministry", "website", "division", "name",
                                          "designation", "room", "phones", "email",
                                          "source_url"])
        w.writeheader()
        w.writerows(results)
    print(f"wrote {len(results)} officials -> {APPEND}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
