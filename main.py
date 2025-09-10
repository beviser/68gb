"""
Main application entry point for 68GB Game API Crawler
"""
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from config import settings
from database import init_database
from api.routes import router as api_router
from crawler.game_crawler import GameCrawler
from services.notification_service import NotificationService

# Global instances
crawler = None
notification_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global crawler, notification_service
    
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    await init_database()
    logger.info("Database initialized")
    
    # Initialize services
    crawler = GameCrawler()
    notification_service = NotificationService()
    
    # Start background crawler
    asyncio.create_task(crawler.start_crawling())
    logger.info("Background crawler started")
    
    yield
    
    # Shutdown
    if crawler:
        await crawler.stop_crawling()
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for crawling and serving 68GB game results",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "crawler_status": "running" if crawler and crawler.is_running else "stopped"
    }

if __name__ == "__main__":
    # Configure logging
    logger.add(
        settings.LOG_FILE,
        rotation="1 day",
        retention="30 days",
        level=settings.LOG_LEVEL
    )
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
