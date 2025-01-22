from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pandas as pd
import os
from pathlib import Path
from src.utils.logger import setup_logger
import json
import time

# Create logger
logger = setup_logger("webapp")

# Create FastAPI app
app = FastAPI(title="Lead Generation Dashboard")

# Setup templates and static files
templates = Jinja2Templates(directory="src/web/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page with leads data"""
    leads_data = []
    
    try:
        # Read Google leads
        google_leads_file = Path("data/google_leads.csv")
        if google_leads_file.exists():
            logger.info(f"Reading Google leads from {google_leads_file}")
            df = pd.read_csv(google_leads_file)
            leads_data.extend(df.to_dict('records'))
            logger.info(f"Found {len(df)} Google leads")
        
        # Sort leads by timestamp (newest first)
        if leads_data:
            leads_data.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
        
        logger.info(f"Total leads to display: {len(leads_data)}")
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "leads": leads_data,
                "total_leads": len(leads_data),
                "sources": {
                    "google": len([l for l in leads_data if l.get('platform') == 'google'])
                }
            }
        )
    except Exception as e:
        logger.error(f"Error processing leads: {e}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Error loading leads: {str(e)}"
            },
            status_code=500
        )

@app.get("/status")
async def scraping_status(request: Request):
    """Show scraping status and recent leads"""
    try:
        # Read latest leads
        df = pd.read_csv('data/google_leads.csv')
        
        # Get last 24 hours of leads
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        last_24h = df[df['timestamp'] > (pd.Timestamp.now() - pd.Timedelta(days=1))]
        
        status = {
            "total_leads": len(df),
            "leads_last_24h": len(last_24h),
            "last_scrape": df['timestamp'].max().strftime("%Y-%m-%d %H:%M:%S") if not df.empty else None,
            "recent_companies": last_24h['name'].tolist()[-10:] if not last_24h.empty else []
        }
        
        return templates.TemplateResponse(
            "status.html",
            {
                "request": request,
                "status": status
            }
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {"error": str(e)}

@app.get("/progress")
async def scraping_progress():
    """Get real-time scraping progress"""
    try:
        with open('data/scraping_progress.json', 'r') as f:
            progress = json.load(f)
            
        # Calculate additional stats
        elapsed = time.time() - progress['start_time']
        rate = progress['completed'] / (elapsed / 3600) if elapsed > 0 else 0
        
        return {
            "status": "active" if time.time() - progress['last_update'] < 300 else "idle",
            "progress": f"{(progress['completed'] / progress['total']) * 100:.1f}%",
            "completed": progress['completed'],
            "total": progress['total'],
            "current_company": progress['current_company'],
            "rate": f"{rate:.1f} companies/hour",
            "elapsed_time": f"{elapsed/3600:.1f} hours"
        }
    except Exception as e:
        return {"error": str(e)}

# Add error handlers
@app.exception_handler(500)
async def internal_error(request: Request, exc: Exception):
    logger.error(f"Internal Server Error: {str(exc)}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": str(exc)},
        status_code=500
    ) 