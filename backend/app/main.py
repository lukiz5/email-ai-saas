from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .db.session import init_db
from .api import auth, summarize, gmail, outlook, imap, billing, history

# Initialize FastAPI app
app = FastAPI(
    title="Email AI SaaS API",
    description="AI-powered email summarization SaaS platform",
    version="1.0.0"
)

# CORS middleware - allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "https://yourdomain.com")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_db()
    print("✅ Database initialized")


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "ok",
        "service": "Email AI SaaS API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(summarize.router, prefix="/api")
app.include_router(gmail.router, prefix="/api")
app.include_router(outlook.router, prefix="/api")
app.include_router(imap.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(history.router, prefix="/api")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not found",
        "message": "The requested resource was not found"
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
