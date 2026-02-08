#!/usr/bin/env python3
"""
Mythos Web - Template Renderer
/opt/mythos/web/renderer.py

Assembles full pages from base.html + individual page content files.
Each page file has sections delimited by markers:
  <!--PAGE_STYLES-->...<!--/PAGE_STYLES-->
  <!--PAGE_CONTENT-->...<!--/PAGE_CONTENT-->
  <!--PAGE_SCRIPT-->...<!--/PAGE_SCRIPT-->
"""
import re
from pathlib import Path
from functools import lru_cache

TEMPLATES_DIR = Path('/opt/mythos/web/templates')


def extract_section(content: str, section: str) -> str:
    """Extract content between section markers"""
    pattern = rf'<!--{section}-->(.*?)<!--/{section}-->'
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ''


def render_page(page_name: str, nav_active: str = '', page_title: str = '') -> str:
    """
    Render a full page by combining base.html with a page content file.
    
    Args:
        page_name: Name of the template file (without .html)
        nav_active: Which nav item to mark active (HOME, DASHBOARD, FINANCE, etc.)
        page_title: Page title for <title> tag
    """
    base = (TEMPLATES_DIR / 'base.html').read_text()
    
    page_file = TEMPLATES_DIR / f'{page_name}.html'
    if not page_file.exists():
        return base.replace('{{PAGE_CONTENT}}', f'<div class="page-content"><h2>Page not found: {page_name}</h2></div>')
    
    page_content = page_file.read_text()
    
    # Extract sections from page file
    styles = extract_section(page_content, 'PAGE_STYLES')
    content = extract_section(page_content, 'PAGE_CONTENT')
    script = extract_section(page_content, 'PAGE_SCRIPT')
    
    # Build nav active states
    nav_items = ['HOME', 'DASHBOARD', 'FINANCE', 'STATUS', 'SESSIONS', 'REGISTRY', 'REPORT', 'FORECAST']
    nav_replacements = {}
    for item in nav_items:
        nav_replacements[f'{{{{NAV_{item}}}}}'] = 'active' if item == nav_active.upper() else ''
    
    # Assemble
    html = base
    html = html.replace('{{PAGE_TITLE}}', page_title or page_name.title())
    html = html.replace('{{PAGE_STYLES}}', f'<style>{styles}</style>' if styles else '')
    html = html.replace('{{PAGE_CONTENT}}', content)
    html = html.replace('{{PAGE_SCRIPT}}', script)
    
    for key, value in nav_replacements.items():
        html = html.replace(key, value)
    
    return html
