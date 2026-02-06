#!/usr/bin/env python3
"""
Mythos Web Routes - Serves HTML pages for the dashboard
/opt/mythos/api/routes/web.py
"""
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(prefix="/app", tags=["web"])

TEMPLATES = Path('/opt/mythos/web/templates')
REPORTS = Path('/opt/mythos/finance/reports')


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page - public"""
    return HTMLResponse(content=(TEMPLATES / 'login.html').read_text())


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page - protected by AuthMiddleware"""
    return HTMLResponse(content=(TEMPLATES / 'dashboard.html').read_text())


@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    """Full report page - serves the generated HTML report with live data"""
    # Read the template and inject live data via API fetch
    template = TEMPLATES / 'report_live.html'
    if template.exists():
        return HTMLResponse(content=template.read_text())
    
    # Fallback to static report
    reports = sorted(REPORTS.glob('report_*.html'), reverse=True)
    if reports:
        return HTMLResponse(content=reports[0].read_text())
    
    return HTMLResponse(content="<h1>No report available. Run the report generator.</h1>")


@router.get("/forecast", response_class=HTMLResponse)
async def forecast_page(request: Request):
    """Forecast page - placeholder"""
    return HTMLResponse(content=(TEMPLATES / 'dashboard.html').read_text())
