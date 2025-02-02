# app/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

# Create the asynchronous database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an asynchronous session factory
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for declarative models
Base = declarative_base()


# Dependency to get the asynchronous database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
