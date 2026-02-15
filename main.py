import argparse
import sys
import os

from utils import save_cache, load_cache, sanitize_filename
from fetcher import fetch_url
from extractor import extract_tables, save_tables

def main():
    parser = argparse.ArgumentParser(description="Extract tables from a URL to an Excel file.")
    parser.add_argument("--url", help="The URL to scrape.")
    parser.add_argument("--file", help="Local HTML file to process.")
    parser.add_argument("--force-refresh", action="store_true", help="Ignore cache and fetch fresh content.")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode.")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run browser in visible mode.")
    
    args = parser.parse_args()
    
    content = None
    output_filename_prefix = None

    if args.file:
        if os.path.exists(args.file):
            print(f"Reading local file: {args.file}")
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            output_filename_prefix = os.path.splitext(os.path.basename(args.file))[0]
        else:
            print(f"Error: File not found: {args.file}")
            return
            
    elif args.url:
        output_filename_prefix = sanitize_filename(args.url)
        
        # Check cache first
        if not args.force_refresh:
            content = load_cache(args.url)
            
        if not content:
            print(f"Fetching fresh content for {args.url}...")
            content = fetch_url(args.url, headless=args.headless)
            if content:
                print("Content fetched successfully.")
                save_cache(args.url, content)
            else:
                print("Failed to fetch content.")
                return
        else:
             print("Using cached content.")

    else:
        print("Error: You must provide either --url or --file.")
        parser.print_help()
        return

    # Extract and save tables
    if content:
        tables = extract_tables(content)
        if tables:
            saved_path = save_tables(tables, output_filename_prefix)
            if saved_path:
                print(f"Done! Tables saved to: {saved_path}")
        else:
            print("No tables found to extract.")
    else:
        print("No content available to process.")

if __name__ == "__main__":
    main()
