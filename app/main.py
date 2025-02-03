# app/main.py

from fastapi import (
    FastAPI,
    Request
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.config import settings
from app.utils import logger
from app.utils import initialize_roles_and_permissions, seed_superadmin
from app.models import *
from app.routers import *
from app.background_tasks.jobs import system_jobs

# Create the FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    print("Starting up the application...")
    
    # Create tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await initialize_roles_and_permissions()
    await seed_superadmin()

    try:
        yield
    finally:
        print("Shutting down the application...")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version="1.0.0",
    debug=settings.DEBUG,  # Enable debug mode if in development
    lifespan=lifespan,
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(course_router)
app.include_router(assignment_router)
app.include_router(discussion_router)
app.include_router(payment_router)
app.include_router(analytics_router)
app.include_router(notification_router)
app.include_router(background_task_router)


# Middleware to log route endpoints
@app.middleware("http")
async def log_requests(request: Request, call_next):
    endpoint = request.url.path
    method = request.method
    client_ip = request.client.host

    logger.info(f"Request: {method} {endpoint} from {client_ip}")
    
    response = await call_next(request)
    
    logger.info(f"Response: {method} {endpoint} returned {response.status_code}")
    return response



# Root endpoint for health check
@app.get("/")
def read_root():
    system_jobs.clean_old_submissions.delay()
    return {"message": f"{settings.APP_NAME} is running"}
