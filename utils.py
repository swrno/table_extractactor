import os
import hashlib
from urllib.parse import urlparse

CACHE_DIR = "cache"

def get_cache_filename(url):
    """Generates a safe filename for the cache based on the URL."""
    # Create a hash of the URL to ensure uniqueness and safe filenames
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    return os.path.join(CACHE_DIR, f"{domain}_{url_hash}.html")

def save_cache(url, content):
    """Saves the content to the cache directory."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    
    filepath = get_cache_filename(url)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Cached content to {filepath}")
    return filepath

def load_cache(url):
    """Loads content from the cache if it exists."""
    filepath = get_cache_filename(url)
    if os.path.exists(filepath):
        print(f"Loading content from cache: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def sanitize_filename(url):
    """Generates a safe filename for the output file."""
    parsed = urlparse(url)
    path = parsed.path.strip('/').replace('/', '_')
    if not path:
        path = parsed.netloc.replace('.', '_')
    # Limit length and remove unsafe chars
    path = "".join([c for c in path if c.isalnum() or c in ('_', '-')])
    return path[:50]
