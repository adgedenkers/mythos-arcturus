"""
Iris Browser Core — Playwright wrapper for headless browser automation.

Provides a clean Python API for:
- Page navigation and content extraction
- Element interaction (click, type, select)
- Screenshot capture
- JavaScript execution
- Network request interception
- Cookie/session management

Design:
- Sync API (runs in thread, compatible with Mythos skill engine)
- Single browser instance with context pooling
- Auto-cleanup on exit
- Screenshot storage in /opt/mythos/browser/screenshots/
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path("/opt/mythos/browser/screenshots")
DEFAULT_TIMEOUT = 30_000  # 30s
DEFAULT_VIEWPORT = {"width": 1280, "height": 720}
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Iris/1.0"
)


@dataclass
class BrowserResult:
    """Result from a browser action."""
    success: bool
    url: str = ""
    title: str = ""
    text: str = ""
    html: str = ""
    screenshot_path: str = ""
    data: Any = None
    error: str = ""
    elapsed_ms: int = 0

    def to_context(self, max_text: int = 4000) -> str:
        """Format as a context block for Iris's prompt."""
        parts = []
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.title:
            parts.append(f"Title: {self.title}")
        if self.error:
            parts.append(f"Error: {self.error}")
        if self.text:
            text = self.text[:max_text]
            if len(self.text) > max_text:
                text += f"\n... [truncated, {len(self.text)} chars total]"
            parts.append(f"Content:\n{text}")
        if self.data:
            try:
                data_str = json.dumps(self.data, indent=2, default=str)
                if len(data_str) > 2000:
                    data_str = data_str[:2000] + "\n... [truncated]"
                parts.append(f"Extracted Data:\n{data_str}")
            except (TypeError, ValueError):
                parts.append(f"Extracted Data: {str(self.data)[:2000]}")
        if self.screenshot_path:
            parts.append(f"Screenshot: {self.screenshot_path}")
        return "\n".join(parts)


class BrowserSession:
    """
    Manages a headless Chromium browser session via Playwright (sync API).

    Usage:
        with BrowserSession() as browser:
            result = browser.goto("https://example.com")
            print(result.title)
            result = browser.extract_text("article")
            print(result.text)
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
    ):
        self.headless = headless
        self.timeout = timeout
        self.viewport = viewport or DEFAULT_VIEWPORT
        self.user_agent = user_agent or USER_AGENT
        self.proxy = proxy
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._started = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def start(self):
        """Launch the browser."""
        if self._started:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise RuntimeError(
                "Playwright not installed. Run:\n"
                "  /opt/mythos/.venv/bin/pip install playwright\n"
                "  /opt/mythos/.venv/bin/playwright install chromium"
            )

        self._playwright = sync_playwright().start()

        launch_args = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
            ],
        }
        if self.proxy:
            launch_args["proxy"] = {"server": self.proxy}

        self._browser = self._playwright.chromium.launch(**launch_args)
        self._context = self._browser.new_context(
            viewport=self.viewport,
            user_agent=self.user_agent,
            java_script_enabled=True,
            accept_downloads=True,
        )
        self._context.set_default_timeout(self.timeout)
        self._page = self._context.new_page()
        self._started = True
        logger.info("Browser session started (headless=%s)", self.headless)

    def stop(self):
        """Close the browser and clean up."""
        if not self._started:
            return
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            logger.warning("Error during browser cleanup: %s", e)
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            self._started = False
            logger.info("Browser session stopped")

    @property
    def page(self):
        """Direct access to Playwright page for advanced use."""
        if not self._started:
            raise RuntimeError("Browser not started. Call start() or use context manager.")
        return self._page

    # ── Navigation ────────────────────────────────────────────────────────

    def goto(self, url: str, wait_until: str = "domcontentloaded") -> BrowserResult:
        """Navigate to a URL and return page info."""
        t0 = time.monotonic()
        try:
            response = self._page.goto(url, wait_until=wait_until)
            self._page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            # networkidle timeout is non-fatal — page may still be usable
            pass

        try:
            return BrowserResult(
                success=True,
                url=self._page.url,
                title=self._page.title(),
                text=self._get_visible_text(),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False,
                url=url,
                error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def back(self) -> BrowserResult:
        """Navigate back."""
        self._page.go_back()
        return BrowserResult(success=True, url=self._page.url, title=self._page.title())

    def forward(self) -> BrowserResult:
        """Navigate forward."""
        self._page.go_forward()
        return BrowserResult(success=True, url=self._page.url, title=self._page.title())

    def reload(self) -> BrowserResult:
        """Reload the current page."""
        self._page.reload()
        return BrowserResult(success=True, url=self._page.url, title=self._page.title())

    # ── Content Extraction ────────────────────────────────────────────────

    def extract_text(self, selector: Optional[str] = None) -> BrowserResult:
        """Extract visible text from the page or a specific element."""
        t0 = time.monotonic()
        try:
            if selector:
                el = self._page.query_selector(selector)
                if el:
                    text = el.inner_text()
                else:
                    return BrowserResult(
                        success=False,
                        url=self._page.url,
                        error=f"No element found for selector: {selector}",
                        elapsed_ms=int((time.monotonic() - t0) * 1000),
                    )
            else:
                text = self._get_visible_text()

            return BrowserResult(
                success=True,
                url=self._page.url,
                title=self._page.title(),
                text=text,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False,
                url=self._page.url,
                error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def extract_links(self, selector: str = "a[href]") -> BrowserResult:
        """Extract all links from the page."""
        t0 = time.monotonic()
        try:
            links = self._page.eval_on_selector_all(
                selector,
                """elements => elements.map(el => ({
                    text: el.innerText.trim().substring(0, 200),
                    href: el.href,
                    title: el.title || ''
                }))""",
            )
            return BrowserResult(
                success=True,
                url=self._page.url,
                data=links,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def extract_tables(self, selector: str = "table") -> BrowserResult:
        """Extract table data as list of dicts."""
        t0 = time.monotonic()
        try:
            tables = self._page.eval_on_selector_all(
                selector,
                """tables => tables.map(table => {
                    const headers = Array.from(table.querySelectorAll('thead th, tr:first-child th'))
                        .map(th => th.innerText.trim());
                    const rows = Array.from(table.querySelectorAll('tbody tr, tr:not(:first-child)'))
                        .map(tr => {
                            const cells = Array.from(tr.querySelectorAll('td'))
                                .map(td => td.innerText.trim());
                            if (headers.length && cells.length === headers.length) {
                                return Object.fromEntries(headers.map((h, i) => [h, cells[i]]));
                            }
                            return cells;
                        });
                    return { headers, rows };
                })""",
            )
            return BrowserResult(
                success=True,
                url=self._page.url,
                data=tables,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def extract_structured(self, schema: Dict[str, str]) -> BrowserResult:
        """
        Extract structured data using CSS selectors.

        Args:
            schema: Dict mapping field names to CSS selectors.
                    e.g. {"title": "h1", "price": ".price", "rating": ".stars"}

        Returns:
            BrowserResult with data as dict of extracted values.
        """
        t0 = time.monotonic()
        data = {}
        for field_name, sel in schema.items():
            try:
                el = self._page.query_selector(sel)
                data[field_name] = el.inner_text().strip() if el else None
            except Exception:
                data[field_name] = None

        return BrowserResult(
            success=True,
            url=self._page.url,
            data=data,
            elapsed_ms=int((time.monotonic() - t0) * 1000),
        )

    def query_selector_all_text(self, selector: str) -> BrowserResult:
        """Get text content from all matching elements."""
        t0 = time.monotonic()
        try:
            texts = self._page.eval_on_selector_all(
                selector,
                "els => els.map(el => el.innerText.trim()).filter(t => t.length > 0)",
            )
            return BrowserResult(
                success=True,
                url=self._page.url,
                data=texts,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    # ── Interaction ───────────────────────────────────────────────────────

    def click(self, selector: str, timeout: Optional[int] = None) -> BrowserResult:
        """Click an element."""
        t0 = time.monotonic()
        try:
            self._page.click(selector, timeout=timeout or self.timeout)
            self._page.wait_for_load_state("domcontentloaded", timeout=5_000)
            return BrowserResult(
                success=True,
                url=self._page.url,
                title=self._page.title(),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def type_text(self, selector: str, text: str, delay: int = 50) -> BrowserResult:
        """Type text into an input field."""
        t0 = time.monotonic()
        try:
            self._page.fill(selector, "")  # Clear first
            self._page.type(selector, text, delay=delay)
            return BrowserResult(
                success=True,
                url=self._page.url,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def select_option(self, selector: str, value: str) -> BrowserResult:
        """Select a dropdown option."""
        t0 = time.monotonic()
        try:
            self._page.select_option(selector, value)
            return BrowserResult(
                success=True, url=self._page.url,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def submit_form(self, form_selector: str = "form") -> BrowserResult:
        """Submit a form by pressing Enter on it or clicking submit button."""
        t0 = time.monotonic()
        try:
            submit = self._page.query_selector(
                f"{form_selector} [type=submit], {form_selector} button[type=submit], "
                f"{form_selector} input[type=submit]"
            )
            if submit:
                submit.click()
            else:
                self._page.press(form_selector, "Enter")
            self._page.wait_for_load_state("domcontentloaded", timeout=10_000)
            return BrowserResult(
                success=True,
                url=self._page.url,
                title=self._page.title(),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def scroll(self, direction: str = "down", amount: int = 500) -> BrowserResult:
        """Scroll the page."""
        t0 = time.monotonic()
        try:
            if direction == "down":
                self._page.mouse.wheel(0, amount)
            elif direction == "up":
                self._page.mouse.wheel(0, -amount)
            elif direction == "bottom":
                self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif direction == "top":
                self._page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)  # Let content load
            return BrowserResult(
                success=True, url=self._page.url,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    # ── Screenshots ───────────────────────────────────────────────────────

    def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
        selector: Optional[str] = None,
    ) -> BrowserResult:
        """Take a screenshot."""
        t0 = time.monotonic()
        try:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            if not path:
                ts = time.strftime("%Y%m%d_%H%M%S")
                path = str(SCREENSHOT_DIR / f"iris_screenshot_{ts}.png")

            if selector:
                el = self._page.query_selector(selector)
                if el:
                    el.screenshot(path=path)
                else:
                    return BrowserResult(
                        success=False,
                        error=f"Element not found: {selector}",
                        elapsed_ms=int((time.monotonic() - t0) * 1000),
                    )
            else:
                self._page.screenshot(path=path, full_page=full_page)

            return BrowserResult(
                success=True,
                url=self._page.url,
                screenshot_path=path,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    # ── JavaScript ────────────────────────────────────────────────────────

    def run_js(self, script: str) -> BrowserResult:
        """Execute JavaScript on the page and return the result."""
        t0 = time.monotonic()
        try:
            result = self._page.evaluate(script)
            return BrowserResult(
                success=True,
                url=self._page.url,
                data=result,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    # ── Waiting ───────────────────────────────────────────────────────────

    def wait_for(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> BrowserResult:
        """Wait for an element to reach a state (visible, hidden, attached, detached)."""
        t0 = time.monotonic()
        try:
            self._page.wait_for_selector(selector, state=state, timeout=timeout or self.timeout)
            return BrowserResult(
                success=True, url=self._page.url,
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def wait_for_navigation(self, timeout: Optional[int] = None) -> BrowserResult:
        """Wait for a navigation event."""
        t0 = time.monotonic()
        try:
            self._page.wait_for_load_state("domcontentloaded", timeout=timeout or self.timeout)
            return BrowserResult(
                success=True,
                url=self._page.url,
                title=self._page.title(),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, url=self._page.url, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    # ── Cookies / Storage ─────────────────────────────────────────────────

    def get_cookies(self) -> BrowserResult:
        """Get all cookies for the current context."""
        cookies = self._context.cookies()
        return BrowserResult(success=True, url=self._page.url, data=cookies)

    def set_cookies(self, cookies: List[Dict]) -> BrowserResult:
        """Set cookies on the current context."""
        try:
            self._context.add_cookies(cookies)
            return BrowserResult(success=True, url=self._page.url)
        except Exception as e:
            return BrowserResult(success=False, error=str(e))

    def clear_cookies(self) -> BrowserResult:
        """Clear all cookies."""
        self._context.clear_cookies()
        return BrowserResult(success=True, url=self._page.url)

    # ── Network ───────────────────────────────────────────────────────────

    def block_resources(self, resource_types: Optional[List[str]] = None):
        """
        Block certain resource types to speed up loading.
        Default blocks images, fonts, stylesheets, media.
        """
        blocked = resource_types or ["image", "font", "stylesheet", "media"]

        def handle_route(route):
            if route.request.resource_type in blocked:
                route.abort()
            else:
                route.continue_()

        self._page.route("**/*", handle_route)
        logger.info("Blocking resource types: %s", blocked)

    def unblock_resources(self):
        """Remove all route handlers."""
        self._page.unroute("**/*")

    # ── Multi-page ────────────────────────────────────────────────────────

    def new_tab(self, url: Optional[str] = None) -> BrowserResult:
        """Open a new tab, optionally navigating to a URL."""
        t0 = time.monotonic()
        try:
            self._page = self._context.new_page()
            if url:
                self._page.goto(url, wait_until="domcontentloaded")
            return BrowserResult(
                success=True,
                url=self._page.url if url else "about:blank",
                title=self._page.title() if url else "",
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )
        except Exception as e:
            return BrowserResult(
                success=False, error=str(e),
                elapsed_ms=int((time.monotonic() - t0) * 1000),
            )

    def close_tab(self) -> BrowserResult:
        """Close the current tab and switch to the last remaining one."""
        try:
            self._page.close()
            pages = self._context.pages
            if pages:
                self._page = pages[-1]
                return BrowserResult(success=True, url=self._page.url)
            return BrowserResult(success=False, error="No tabs remaining")
        except Exception as e:
            return BrowserResult(success=False, error=str(e))

    # ── Utility / Private ─────────────────────────────────────────────────

    def _get_visible_text(self, max_length: int = 50_000) -> str:
        """Extract readable text from the page, stripping nav/footer/script noise."""
        try:
            text = self._page.evaluate(
                """() => {
                    // Prefer main content areas
                    const main = document.querySelector('main, article, [role="main"], .content, #content');
                    const target = main || document.body;

                    // Clone and strip noise
                    const clone = target.cloneNode(true);
                    clone.querySelectorAll('script, style, nav, footer, header, noscript, iframe, svg')
                        .forEach(el => el.remove());

                    return clone.innerText;
                }"""
            )
            # Clean up whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            return text.strip()[:max_length]
        except Exception:
            # Fallback: just get all body text
            try:
                return self._page.inner_text("body")[:max_length]
            except Exception:
                return ""

    def get_page_info(self) -> Dict[str, Any]:
        """Get current page metadata."""
        return {
            "url": self._page.url,
            "title": self._page.title(),
            "viewport": self.viewport,
        }
