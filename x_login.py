#!/usr/bin/env python
"""
Manual X/Twitter login helper.

Run this once to log into X manually and save session cookies.
The main ICE monitor will then use these cookies automatically.

Usage:
    python x_login.py

A browser window will open to X's login page.
Log in however you prefer (Google, Apple, username/password, etc.)
Once you reach the home feed, cookies are saved.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

COOKIE_FILE = Path(".twitter_cookies.json")


async def main():
    print()
    print("=" * 60)
    print("  X/TWITTER MANUAL LOGIN")
    print("=" * 60)
    print()

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: playwright not installed.")
        print("Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    playwright = await async_playwright().start()

    # Try to use real Chrome first (allows Google OAuth)
    # Fall back to Playwright's Chromium if Chrome not found
    chrome_path = None
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            chrome_path = p
            break

    if chrome_path:
        print(f"  Using your installed Chrome browser")
        print(f"  (Google Sign-In will work!)")
        browser = await playwright.chromium.launch(
            headless=False,
            executable_path=chrome_path,
            args=["--start-maximized"],
        )
    else:
        print("  Using Playwright Chromium (Google Sign-In may not work)")
        print("  Tip: Use username/password login instead")
        browser = await playwright.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )

    context = await browser.new_context(
        no_viewport=True,  # Use the window's full size
    )

    page = await context.new_page()

    print("  A browser window is opening...")
    print()
    print("  Log in using ANY method:")
    print("    - Google Sign-In")
    print("    - Apple Sign-In")
    print("    - Username + Password")
    print()
    print("  Once you reach your home feed, cookies will be saved.")
    print("  Press Ctrl+C to cancel.")
    print()
    print("=" * 60)
    print()

    await page.goto("https://x.com/i/flow/login")

    # Wait for user to complete login (detected by URL change)
    check_count = 0
    while True:
        await asyncio.sleep(2)
        check_count += 1
        try:
            url = page.url
            # Success: redirected away from login/flow pages
            if "login" not in url.lower() and "flow" not in url.lower():
                print(f"\n  Login detected! URL: {url[:50]}...")
                break
        except Exception:
            pass

        # Progress indicator every 30 seconds
        if check_count % 15 == 0:
            print(f"  Still waiting for login... ({check_count * 2}s)")

    # Save cookies
    cookies = await context.cookies()
    COOKIE_FILE.write_text(json.dumps(cookies, indent=2))
    print(f"\n  Saved {len(cookies)} cookies to {COOKIE_FILE}")

    # Verify by loading home
    print("  Verifying session...")
    await page.goto("https://x.com/home")
    await asyncio.sleep(3)

    if "login" not in page.url.lower():
        print()
        print("=" * 60)
        print("  SUCCESS! Session cookies saved.")
        print()
        print("  You can now run the main monitor:")
        print("    python main.py")
        print("=" * 60)
        print()
    else:
        print()
        print("  WARNING: Session verification failed.")
        print("  Cookies were saved but may not work.")
        print()

    await browser.close()
    await playwright.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n  Cancelled.\n")
        sys.exit(0)
