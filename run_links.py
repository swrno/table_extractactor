#!/usr/bin/env python3
"""
run_links.py — Read URLs from links.csv and execute main.py for each one.

Expected CSV format (tab or comma separated):
    links                                           save_dir
    https://fbref.com/en/squads/.../Man-City-Stats  PL-17-18
    ...

Outputs are saved to: outputs/{save_dir}/

Usage:
    python3 run_links.py [--headless] [--force-refresh]
"""

import argparse
import csv
import os
import subprocess
import sys

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
LINKS_FILE  = os.path.join(BASE_DIR, "links.csv")
MAIN_SCRIPT = os.path.join(BASE_DIR, "main.py")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def read_links(filepath: str) -> list[dict]:
    """
    Parse links.csv.  Accepts both comma and tab delimiters.
    Returns a list of dicts with keys 'links' and 'save_dir'.
    """
    if not os.path.exists(filepath):
        print(f"Error: CSV file not found: {filepath}")
        sys.exit(1)

    rows = []
    with open(filepath, newline="", encoding="utf-8") as fh:
        # Sniff delimiter (handles both comma and tab)
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        except csv.Error:
            dialect = csv.excel  # fall back to comma

        reader = csv.DictReader(fh, dialect=dialect)
        for row in reader:
            url      = row.get("links", "").strip()
            save_dir = row.get("save_dir", "").strip()
            if url and not url.startswith("#"):
                rows.append({"url": url, "save_dir": save_dir})

    return rows


def run_for_row(url: str, save_dir: str, extra_args: list[str]) -> bool:
    """
    Execute main.py for a single URL, saving output to outputs/{save_dir}/.
    Returns True on success (exit code 0).
    """
    output_dir = os.path.join(OUTPUTS_DIR, save_dir) if save_dir else OUTPUTS_DIR

    cmd = [
        sys.executable, MAIN_SCRIPT,
        "--url", url,
        "--output-dir", output_dir,
    ] + extra_args

    print(f"\n{'='*60}")
    print(f"URL      : {url}")
    print(f"Save dir : {output_dir}")
    print(f"Command  : {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd)
    success = result.returncode == 0

    if success:
        print(f"✅  Done: {url}")
    else:
        print(f"❌  Failed (exit {result.returncode}): {url}")

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Run main.py for every row in links.csv."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (default: visible).",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Ignore cache and fetch fresh content for every URL.",
    )
    args = parser.parse_args()

    # Flags forwarded to main.py
    forwarded = ["--headless" if args.headless else "--no-headless"]
    if args.force_refresh:
        forwarded.append("--force-refresh")

    rows = read_links(LINKS_FILE)

    if not rows:
        print(f"No URLs found in {LINKS_FILE}.")
        sys.exit(0)

    print(f"Found {len(rows)} URL(s) to process.\n")

    results: dict[str, bool] = {}
    for i, row in enumerate(rows, start=1):
        url      = row["url"]
        save_dir = row["save_dir"]
        print(f"[{i}/{len(rows)}] {url}  →  outputs/{save_dir}/")
        results[url] = run_for_row(url, save_dir, forwarded)

    # ── Summary ─────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = [u for u, ok in results.items() if ok]
    failed = [u for u, ok in results.items() if not ok]

    for u in passed:
        print(f"  ✅  {u}")
    for u in failed:
        print(f"  ❌  {u}")

    print(f"\nTotal: {len(rows)} | Success: {len(passed)} | Failed: {len(failed)}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
