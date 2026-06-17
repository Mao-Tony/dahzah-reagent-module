"""
数据库会话管理

集成到主项目时，请使用主项目的 database.py 实现。
此处提供简化版本用于独立测试。
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os

# 数据库配置 - 可通过环境变量覆盖
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/dahzah"
)


def create_engine_and_session():
    """创建数据库引擎和会话工厂"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, async_session


# 全局引擎和会话工厂（延迟初始化）
_engine = None
_async_session_factory = None


def _get_engine():
    global _engine, _async_session_factory
    if _engine is None:
        _engine, _async_session_factory = create_engine_and_session()
    return _engine


def _get_session_factory():
    global _engine, _async_session_factory
    if _async_session_factory is None:
        _engine, _async_session_factory = create_engine_and_session()
    return _async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖函数

    用于 FastAPI 的 Depends() 注入。
    集成到主项目时请使用主项目的实现。
    """
    session_factory = _get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_sync_db_session():
    """
    获取同步数据库会话

    某些场景可能需要同步会话。
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    sync_url = DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
