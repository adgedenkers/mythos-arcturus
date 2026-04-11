#!/usr/bin/env python3
"""
Mythos API - React Frontend Routes
/opt/mythos/api/routes/frontend.py

Serves the React Command Center v2 from /app/v2/
Static assets from /opt/mythos/web/frontend/dist/
All non-asset routes fall through to index.html for client-side routing.
"""
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(tags=["frontend"])

DIST_DIR = Path('/opt/mythos/web/frontend/dist')
INDEX_HTML = DIST_DIR / 'index.html'


@router.get("/app/v2/assets/{filepath:path}")
async def serve_asset(filepath: str):
    """Serve static assets (JS, CSS) from the Vite build"""
    asset = DIST_DIR / 'assets' / filepath
    if asset.exists() and asset.is_file():
        # Determine content type
        suffix = asset.suffix.lower()
        media_types = {
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.map': 'application/json',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.svg': 'image/svg+xml',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
        }
        media_type = media_types.get(suffix, 'application/octet-stream')
        return FileResponse(asset, media_type=media_type)
    return HTMLResponse(content="Not found", status_code=404)


@router.get("/app/v2/{path:path}", response_class=HTMLResponse)
@router.get("/app/v2", response_class=HTMLResponse)
async def serve_react_app(request: Request, path: str = ""):
    """
    Catch-all: serve index.html for all /app/v2/* routes.
    React Router handles client-side routing from there.
    """
    if INDEX_HTML.exists():
        return HTMLResponse(content=INDEX_HTML.read_text())
    return HTMLResponse(
        content="<h1>React app not built</h1><p>Run: cd /opt/mythos/web/frontend && npm run build</p>",
        status_code=503
    )
