"""
Database connection and session management.

Uses asyncpg for async PostgreSQL operations with connection pooling.
All database operations should use this module for connections.

Example:
    from database import db
    
    # Execute query
    await db.execute("INSERT INTO orch_models VALUES ($1, $2)", model_id, name)
    
    # Fetch results
    rows = await db.fetch("SELECT * FROM orch_models WHERE installed = true")
    
    # Single value
    count = await db.fetchval("SELECT COUNT(*) FROM orch_models")
"""

import asyncpg
from typing import AsyncGenerator, Optional, List, Any
from contextlib import asynccontextmanager
import logging

from .config import settings

logger = logging.getLogger(__name__)


class Database:
    """
    Database connection manager with connection pooling.
    
    Provides async methods for database operations:
    - execute(): Run INSERT/UPDATE/DELETE
    - fetch(): Get multiple rows
    - fetchrow(): Get single row
    - fetchval(): Get single value
    
    Uses connection pooling for efficiency.
    """
    
    def __init__(self):
        """Initialize database manager (pool created on first connect)."""
        self.pool: Optional[asyncpg.Pool] = None
        self._connected = False
    
    async def connect(self):
        """
        Create connection pool.
        
        Called automatically on first database operation.
        Can also be called explicitly at startup.
        
        Raises:
            Exception: If connection fails
        """
        if self.pool is not None:
            logger.warning("Database pool already exists")
            return
        
        try:
            # Parse database URL
            # Format: postgresql://user@host:port/database
            url = settings.DATABASE_URL
            
            self.pool = await asyncpg.create_pool(
                url,
                min_size=2,
                max_size=settings.DATABASE_POOL_SIZE,
                max_inactive_connection_lifetime=300,  # 5 minutes
                command_timeout=60
            )
            
            self._connected = True
            logger.info("Database connection pool created")
            
            # Test connection
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"PostgreSQL version: {version.split(',')[0]}")
        
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            self._connected = False
            raise
    
    async def disconnect(self):
        """
        Close connection pool.
        
        Should be called on application shutdown.
        """
        if self.pool:
            await self.pool.close()
            self.pool = None
            self._connected = False
            logger.info("Database connection pool closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connected and self.pool is not None
    
    async def _ensure_connected(self):
        """Ensure database is connected (internal use)."""
        if not self.is_connected:
            await self.connect()
    
    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Get database connection from pool.
        
        Yields:
            asyncpg.Connection: Database connection
            
        Example:
            async with db.connection() as conn:
                await conn.execute("INSERT INTO ...")
        """
        await self._ensure_connected()
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query (INSERT/UPDATE/DELETE).
        
        Args:
            query: SQL query with $1, $2, ... placeholders
            *args: Query parameters
            
        Returns:
            Status string from PostgreSQL
            
        Example:
            await db.execute(
                "INSERT INTO orch_models (model_id, name) VALUES ($1, $2)",
                "llama3_70b",
                "llama3.1:70b"
            )
        """
        async with self.connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """
        Fetch multiple rows.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            List of records (dict-like objects)
            
        Example:
            rows = await db.fetch("SELECT * FROM orch_models WHERE installed = $1", True)
            for row in rows:
                print(row['model_id'], row['name'])
        """
        async with self.connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Fetch single row.
        
        Args:
            query: SQL query
            *args: Query parameters
            
        Returns:
            Single record or None
            
        Example:
            row = await db.fetchrow("SELECT * FROM orch_models WHERE model_id = $1", "llama3_70b")
            if row:
                print(row['name'])
        """
        async with self.connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args, column: int = 0) -> Any:
        """
        Fetch single value.
        
        Args:
            query: SQL query
            *args: Query parameters
            column: Column index (default 0)
            
        Returns:
            Single value or None
            
        Example:
            count = await db.fetchval("SELECT COUNT(*) FROM orch_models")
            print(f"Total models: {count}")
        """
        async with self.connection() as conn:
            return await conn.fetchval(query, *args, column=column)
    
    async def transaction(self):
        """
        Create a transaction context.
        
        Returns:
            Transaction context manager
            
        Example:
            async with db.transaction() as tx:
                await tx.execute("INSERT INTO ...")
                await tx.execute("UPDATE ...")
                # Auto-commits on success, rolls back on exception
        """
        await self._ensure_connected()
        return self.pool.acquire()


# Global database instance
# Import this in other modules: from database import db
db = Database()


async def init_db():
    """
    Initialize database connection.
    
    Call this at application startup.
    
    Example:
        import asyncio
        from database import init_db
        
        async def main():
            await init_db()
            # ... application code ...
        
        asyncio.run(main())
    """
    await db.connect()


async def close_db():
    """
    Close database connection.
    
    Call this at application shutdown.
    
    Example:
        import asyncio
        from database import close_db
        
        async def shutdown():
            await close_db()
        
        asyncio.run(shutdown())
    """
    await db.disconnect()


@asynccontextmanager
async def get_db() -> AsyncGenerator[Database, None]:
    """
    Get database instance for dependency injection.
    
    This is for FastAPI dependency injection.
    
    Yields:
        Database instance
        
    Example:
        from fastapi import Depends
        from database import get_db, Database
        
        @app.get("/models")
        async def list_models(db: Database = Depends(get_db)):
            models = await db.fetch("SELECT * FROM orch_models")
            return models
    """
    yield db
