from playwright.sync_api import sync_playwright
try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

import time
import random
import os

# Persistent profile directory so Cloudflare cookies survive across runs
_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".browser_profile")

def _is_cloudflare(content):
    """Check if the page content is a Cloudflare challenge."""
    return "Just a moment..." in content or "Enable JavaScript and cookies to continue" in content

def _launch_and_fetch(playwright, url, headless):
    """Launch browser, navigate to URL, and return (page_content, is_cloudflare_blocked)."""

    # Use real Chrome (not Playwright's bundled Chromium) to avoid
    # Cloudflare fingerprinting the browser as automated.
    # Also disable the AutomationControlled blink feature that sets
    # navigator.webdriver = true.
    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    # Use a persistent context so cookies (including Cloudflare clearance)
    # are saved across runs. This means Cloudflare may not challenge you
    # on subsequent visits.
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=_PROFILE_DIR,
        channel="chrome",            # Use real Chrome, not Chromium
        headless=headless,
        args=launch_args,
        viewport={'width': 1920, 'height': 1080},
        # Don't set user_agent — let real Chrome use its own genuine UA
    )
    page = context.new_page()

    if stealth_sync:
        stealth_sync(page)

    try:
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        # Give Cloudflare's JS challenge time to auto-resolve
        wait_seconds = 15
        for remaining in range(wait_seconds, 0, -1):
            print(f"\rWaiting for page to settle... {remaining}s ", end="", flush=True)
            time.sleep(1)
        print("\rPage ready. Checking content...        ")

        # Use page.title() for lightweight Cloudflare detection
        print("Checking for Cloudflare challenge...")
        page_title = page.title()
        is_cf = "Just a moment" in page_title

        if is_cf:
            if headless:
                print("Cloudflare challenge detected in headless mode. Will retry with visible browser...")
                context.close()
                return None, True

            # === COMPLETELY HANDS-OFF CLOUDFLARE HANDLING ===
            # Do NOT call page.content(), page.evaluate(), page.wait_for_function(),
            # or ANY method that injects JS into the page.
            print("\n" + "="*60)
            print("CLOUDFLARE CHALLENGE DETECTED")
            print("="*60)
            print("1. Solve the challenge in the browser window")
            print("2. Wait for the real page to load")
            print("3. Then come back here and press ENTER")
            print("="*60)
            input("\n>>> Press ENTER after the page has loaded... ")
            print("Continuing...")
        else:
            print("No Cloudflare challenge. Page title:", page_title[:60])

        # Now that the challenge should be cleared, wait for full load
        print("Waiting for network to settle (max 15s)...")
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
            print("Network idle.")
        except Exception:
            print("Network didn't fully settle, continuing anyway...")

        # Simulate human scrolling to trigger lazy-loaded content
        print("Scrolling page to load lazy content...")
        page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(random.uniform(1, 3))

        print("Extracting page content...")
        final_content = page.content()
        print(f"Got {len(final_content):,} characters of HTML.")
        context.close()
        print("Browser closed.")
        return final_content, _is_cloudflare(final_content)

    except Exception as e:
        print(f"Error fetching URL: {e}")
        context.close()
        return None, False

def fetch_url(url, headless=True):
    """
    Fetches the HTML content of a URL using Playwright.
    Uses real Chrome with a persistent profile to avoid Cloudflare detection.
    If Cloudflare is detected in headless mode, automatically retries
    with a visible browser window so the user can solve the challenge.
    """
    print(f"Fetching {url}...")

    with sync_playwright() as p:
        # First attempt (headless or not, based on user flag)
        content, blocked = _launch_and_fetch(p, url, headless)

        # If blocked in headless mode, auto-retry in visible mode
        if blocked and headless:
            print("\nRe-launching browser in visible mode for manual Cloudflare bypass...")
            content, blocked = _launch_and_fetch(p, url, headless=False)

        if blocked:
            print("Warning: Content still appears to be a Cloudflare challenge page after retry.")

        return content
