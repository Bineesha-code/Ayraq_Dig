from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from .config.settings import settings
from .config.database import supabase_client
from .routes import auth, connections, chat, threats, notifications, support

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AYRAQ Backend API",
    description="Backend API for AYRAQ - AI-powered mobile application for women's safety",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(connections.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(threats.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        logger.info("Starting AYRAQ Backend API...")
        
        # Test Supabase connection
        if supabase_client.test_connection():
            logger.info("Supabase connection successful")
        else:
            logger.warning("Supabase connection test failed")
            
        logger.info("AYRAQ Backend API started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down AYRAQ Backend API...")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "error": "An unexpected error occurred. Please try again later."
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AYRAQ Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_status = supabase_client.test_connection()
        
        return {
            "status": "healthy" if db_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "version": "1.0.0",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
