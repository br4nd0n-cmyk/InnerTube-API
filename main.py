"""
InnerTube API - Main Application
A powerful, unlimited YouTube API wrapper

Created with ❤️ by Kobir Shah 🇧🇩 (Bangladesh)
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
import json
import urllib.request

from config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    API_HOST,
    API_PORT,
    CORS_ORIGINS,
    CORS_METHODS,
    CORS_HEADERS
)

from routes import (
    youtube_router,
    channels_router,
    playlists_router,
    comments_router,
    music_router,
    advanced_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(youtube_router)
app.include_router(channels_router)
app.include_router(playlists_router)
app.include_router(comments_router)
app.include_router(music_router)
app.include_router(advanced_router)


# ==================================================
# AUTOMATED ROTATING PROXY & COOKIE LIFECYCLE HOOK
# ==================================================
@app.on_event("startup")
async def apply_cookies_and_proxy_override():
    """Fetches a free proxy dynamically and injects browser configuration tokens"""
    try:
        import innertube
        _orig_init = innertube.InnerTube.__init__
        
        # Fetch an anonymous HTTP proxy automatically using ProxyScrape API
        fetched_proxy = None
        try:
            proxy_api_url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=yes&anonymity=elite"
            with urllib.request.urlopen(proxy_api_url, timeout=5) as response:
                proxies_list = response.read().decode('utf-8').strip().split('\r\n')
                if proxies_list and len(proxies_list[0]) > 4:
                    # Select the first high-speed elite proxy from the fresh pool
                    fetched_proxy = f"http://{proxies_list[0]}"
                    logger.info(f"🌐 [ProxyScrape] Harvested active proxy location successfully: {fetched_proxy}")
        except Exception as proxy_fetch_err:
            logger.error(f"⚠️ [ProxyScrape] Couldn't fetch proxy automatically: {proxy_fetch_err}")

        def _patched_init(self, client_name="WEB", *args, **kwargs):
            # 1. Inject Cookies
            cookie_file = Path(__file__).parent / "cookies.json"
            if cookie_file.exists():
                try:
                    with open(cookie_file, "r", encoding="utf-8") as f:
                        raw_cookies = json.load(f)
                    
                    cookie_dict = {}
                    if isinstance(raw_cookies, list):
                        for cookie in raw_cookies:
                            if "name" in cookie and "value" in cookie:
                                cookie_dict[cookie["name"]] = cookie["value"]
                    elif isinstance(raw_cookies, dict):
                        cookie_dict = raw_cookies

                    if cookie_dict:
                        kwargs['cookies'] = cookie_dict
                except Exception as cookie_err:
                    logger.error(f"⚠️ [InnerTube Patch] Cookie injection mismatch: {cookie_err}")
            
            # 2. Inject the dynamic proxy path
            if fetched_proxy:
                kwargs['proxies'] = fetched_proxy
                
            _orig_init(self, client_name, *args, **kwargs)
            
        innertube.InnerTube.__init__ = _patched_init
        logger.info("🔒 [Lifecycle Patch] Auto-proxy configuration loaded into the system architecture successfully.")
    except Exception as patch_err:
        logger.error(f"❌ Automation engine setup failed: {patch_err}")
# ==================================================


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the landing page"""
    index_file = static_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>InnerTube API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            h1 { font-size: 3em; margin-bottom: 10px; }
            a {
                color: #fff;
                background: rgba(255,255,255,0.2);
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
                margin: 10px 5px;
            }
            a:hover { background: rgba(255,255,255,0.3); }
        </style>
    </head>
    <body>
        <h1>🚀 InnerTube API</h1>
        <p>Your powerful, unlimited YouTube API wrapper is running!</p>
        <div>
            <a href="/docs">📚 API Documentation</a>
            <a href="/redoc">📖 ReDoc</a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "service": "InnerTube API"
    }

@app.get("/info")
async def api_info():
    """Get API information"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": "Powerful YouTube API wrapper with unlimited features",
        "endpoints": {
            "youtube": ["/api/search", "/api/video/{video_id}", "/api/player/{video_id}"],
            "music": ["/api/music/search", "/api/music/home"]
        }
    }

app = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)
