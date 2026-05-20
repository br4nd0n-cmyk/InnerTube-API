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

# ==========================================
# ROBUST COOKIE PARSER & INTERCEPT OVERRIDE
# ==========================================
logger = logging.getLogger(__name__)

try:
    import innertube
    _orig_init = innertube.InnerTube.__init__
    
    def _patched_init(self, client_name="WEB", *args, **kwargs):
        cookie_file = Path(__file__).parent / "cookies.json"
        if cookie_file.exists():
            try:
                with open(cookie_file, "r", encoding="utf-8") as f:
                    raw_cookies = json.load(f)
                
                # Convert browser Cookie-Editor array into a standard Python dict
                cookie_dict = {}
                if isinstance(raw_cookies, list):
                    for cookie in raw_cookies:
                        if "name" in cookie and "value" in cookie:
                            cookie_dict[cookie["name"]] = cookie["value"]
                elif isinstance(raw_cookies, dict):
                    cookie_dict = raw_cookies

                if cookie_dict:
                    # Inject safe parsed dictionary instead of raw file path string
                    kwargs['cookies'] = cookie_dict
                    print("🚀 [InnerTube Patch] Parsed and injected browser session profiles safely.")
            except Exception as cookie_err:
                print(f"⚠️ [InnerTube Patch] Failed parsing cookies.json: {cookie_err}")
        else:
            print("⚠️ [InnerTube Patch] cookies.json file not found in root repository path.")
            
        _orig_init(self, client_name, *args, **kwargs)
        
    innertube.InnerTube.__init__ = _patched_init
except Exception as patch_err:
    print(f"❌ Could not apply global cookie profile patch: {patch_err}")
# ==========================================

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
            "youtube": [
                "/api/search",
                "/api/video/{video_id}",
                "/api/player/{video_id}",
                "/api/next/{video_id}",
                "/api/browse/{browse_id}",
                "/api/trending",
                "/api/homepage"
            ],
            "channels": [
                "/api/channel/{channel_id}",
                "/api/channel/{channel_id}/videos",
                "/api/channel/{channel_id}/playlists",
                "/api/channel/{channel_id}/about",
                "/api/channel/{channel_id}/community"
            ],
            "playlists": [
                "/api/playlist/{playlist_id}",
                "/api/playlist/{playlist_id}/videos"
            ],
            "comments": [
                "/api/comments/{video_id}"
            ],
            "music": [
                "/api/music/search",
                "/api/music/home",
                "/api/music/artist/{artist_id}",
                "/api/music/album/{album_id}",
                "/api/music/playlist/{playlist_id}"
            ],
            "advanced": [
                "/api/batch",
                "/api/captions/{video_id}",
                "/api/livestream/{video_id}",
                "/api/shorts/{shorts_id}",
                "/api/analytics",
                "/api/cache/clear"
            ]
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

app = app  # Explicitly exposes the FastAPI instance to Vercel's handler

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    logger.info(f"Server running at http://{API_HOST}:{API_PORT}")
    logger.info(f"Documentation available at http://{API_HOST}:{API_PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
