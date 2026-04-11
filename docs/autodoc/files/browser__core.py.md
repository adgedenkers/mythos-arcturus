# browser/core.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 674

---

### File: `browser/core.py`

#### Purpose
This file provides a Python API for managing a headless Chromium browser session using Playwright. It supports page navigation, content extraction, element interaction, screenshot capture, JavaScript execution, network request interception, and cookie/session management.

#### Architecture
The file contains two main classes:
1. **`BrowserResult`**: Represents the result of a browser action, including success status, URL, title, text content, HTML, screenshot path, extracted data, error message, and elapsed time.
2. **`BrowserSession`**: Manages the browser session, providing methods for navigation, content extraction, element interaction, and session management.

The `BrowserSession` class uses the context manager (`__enter__` and `__exit__`) to ensure proper initialization and cleanup of the browser instance.

#### Patterns
- **Context Manager**: The `BrowserSession` class uses the context manager pattern to ensure that the browser session is properly started and stopped.
- **Data Class**: The `BrowserResult` class is a data class, which simplifies the creation and management of result objects.

#### Dependencies
- **Standard Libraries**: `json`, `logging`, `os`, `re`, `time`
- **External Libraries**: `dataclasses`, `pathlib`, `typing`, `playwright`

#### Interfaces
- **Public Methods**:
  - `BrowserSession.goto(url, wait_until)`: Navigate to a URL and return page info.
  - `BrowserSession.back()`: Navigate back.
  - `BrowserSession.forward()`: Navigate forward.
  - `BrowserSession.reload()`: Reload the current page.
  - `BrowserSession.extract_text(selector)`: Extract visible text from the page or a specific element.
  - `BrowserSession.extract_links(selector)`: Extract all links from the page.
  - `BrowserSession.extract_tables(selector)`: Extract table data as a list of dictionaries.
  - `BrowserSession.extract_structured(schema)`: Extract structured data using CSS selectors.
  - `BrowserSession.query_selector_all_text(selector)`: Get text content from all matching elements.
  - `BrowserSession.click(selector, timeout)`: Click an element.
  - `BrowserSession.type_text(selector, text, delay)`: Type text into an input field.
  - `BrowserSession.select_option(selector, value)`: Select a dropdown option.
  - `BrowserSession.submit_form(form_selector)`: Submit a form.
  - `BrowserSession.scroll(direction, amount)`: Scroll the page.
  - `BrowserSession.screenshot(path, full_page, selector)`: Take a screenshot.
  - `BrowserSession.run_js(script)`: Execute JavaScript on the page.
  - `BrowserSession.wait_for(selector, state, timeout)`: Wait for an element to reach a state.
  - `BrowserSession.wait_for_navigation(timeout)`: Wait for a navigation event.
  - `BrowserSession.get_cookies()`: Get all cookies for the current context.
  - `BrowserSession.set_cookies(cookies)`: Set cookies on the current context.
  - `BrowserSession.clear_cookies()`: Clear all cookies.
  - `BrowserSession.block_resources(resource_types)`: Block certain resource types.
  - `BrowserSession.unblock_resources()`: Remove all route handlers.
  - `BrowserSession.new_tab(url)`: Open a new tab.
  - `BrowserSession.close_tab()`: Close the current tab.
  - `BrowserSession.get_page_info()`: Get current page metadata.

- **Public Properties**:
  - `BrowserSession.page`: Direct access to the Playwright page for advanced use.

#### Database
- **No direct database interactions**: The file does not interact directly with PostgreSQL, Neo4j, or Redis.

#### Configuration
- **Environment Variables**: None
- **Configuration Files**: None
- **Constants**:
  - `SCREENSHOT_DIR`: Path to store screenshots (`/opt/mythos/browser/screenshots`).
  - `DEFAULT_TIMEOUT`: Default timeout for operations (30 seconds).
  - `DEFAULT_VIEWPORT`: Default viewport size (`{"width": 1280, "height": 720}`).
  - `USER_AGENT`: Default user agent string.

#### Key Logic
- **Browser Initialization**: The `start` method initializes the Playwright browser and context, setting up the viewport, user agent, and other configurations.
- **Navigation**: Methods like `goto`, `back`, `forward`, and `reload` handle page navigation.
- **Content Extraction**: Methods like `extract_text`, `extract_links`, `extract_tables`, and `extract_structured` extract various types of content from the page.
- **Element Interaction**: Methods like `click`, `type_text`, `select_option`, and `submit_form` interact with page elements.
- **Screenshot Capture**: The `screenshot` method captures screenshots and stores them in the specified directory.
- **JavaScript Execution**: The `run_js` method executes JavaScript on the page.
- **Resource Blocking**: The `block_resources` and `unblock_resources` methods control resource loading.

#### Integration Points
- **Mythos Skill Engine**: The `BrowserSession` class is designed to be used within the Mythos skill engine, providing a synchronous API for browser automation.
- **Iris Prompt**: The `to_context` method in `BrowserResult` formats the result as a context block for Iris's prompt.
- **Logging**: The file uses the `logging` module to log important events and errors.

This file serves as a core component of the Mythos system, enabling automated browser interactions and content extraction for various use cases within the platform.
