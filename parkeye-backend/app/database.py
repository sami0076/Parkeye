"""Supabase database connection and session management."""
import ssl
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings


def _build_engine_url() -> str:
    """Strip sslmode/ssl from URL -- asyncpg handles SSL via connect_args."""
    parsed = urlparse(settings.DATABASE_URL)
    query = parse_qs(parsed.query)
    query.pop("sslmode", None)
    query.pop("ssl", None)
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    _build_engine_url(),
    echo=settings.ENV == "development",
    connect_args={
        "ssl": ssl_context,
        "statement_cache_size": 0,  # required for Supabase pooler (Supavisor)
    },
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


async def get_db() -> AsyncSession:
    """Dependency for FastAPI routes - yields async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
