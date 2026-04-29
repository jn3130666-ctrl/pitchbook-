import os
import json
import re
import logging
from urllib.parse import urlparse, unquote

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def filename_from_url(url, content_type=None, default="report"):
    """Infer a filename from the URL, Content-Disposition header, or content type."""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    basename = os.path.basename(path)

    if basename and '.' in basename:
        return basename

    if content_type:
        ext_map = {
            'application/pdf': '.pdf',
            'text/html': '.html',
            'application/zip': '.zip',
            'application/x-zip-compressed': '.zip',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-excel': '.xls',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        }
        for ct, ext in ext_map.items():
            if ct in content_type:
                return f"{default}{ext}"

    return default


def try_download(url, timeout=30):
    """Download a file, following redirects, returning (content, filename, content_type) or None."""
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()

        # Try to extract filename from Content-Disposition
        content_disposition = resp.headers.get("Content-Disposition", "")
        fname = None
        if "filename=" in content_disposition:
            match = re.search(r'filename\*?=([^;]+)', content_disposition)
            if match:
                fname = match.group(1).strip().strip('"\'')
                # Handle RFC 5987 encoding (filename*=UTF-8''name.pdf)
                if "''" in fname:
                    fname = fname.split("''", 1)[1]
                fname = unquote(fname)

        content_type = resp.headers.get("Content-Type", "")
        if not fname:
            fname = filename_from_url(resp.url, content_type)

        return resp.content, fname, content_type

    except requests.RequestException as e:
        log.warning(f"Download failed for {url}: {e}")
        return None


def main():
    ensure_dir("reports")

    if not os.path.exists("data/emails.json"):
        log.warning("data/emails.json not found, skipping.")
        return

    with open("data/emails.json", "r", encoding="utf-8") as f:
        emails = json.load(f)

    all_report_links = []
    for email in emails:
        all_report_links.extend(email.get("report_links", []))

    if not all_report_links:
        log.info("No report links found in emails.json.")
        return

    downloaded = 0
    for link in all_report_links:
        url = link["url"]
        text = link.get("text", "")
        log.info(f"Downloading: {text or url}")

        result = try_download(url)
        if result is None:
            log.warning(f"Skipped {url}")
            continue

        content, fname, content_type = result

        # Deduplicate filename
        filepath = os.path.join("reports", fname)
        if os.path.exists(filepath):
            name, ext = os.path.splitext(fname)
            filepath = os.path.join("reports", f"{name}_1{ext}")

        with open(filepath, "wb") as f:
            f.write(content)

        log.info(f"Saved to {filepath} ({len(content)} bytes)")
        downloaded += 1

    log.info(f"Done. Downloaded {downloaded} file(s) to reports/")


if __name__ == "__main__":
    main()
