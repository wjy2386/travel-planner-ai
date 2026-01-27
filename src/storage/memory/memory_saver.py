import psycopg
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from typing import Optional, Union
import logging
import time

logger = logging.getLogger(__name__)

# 数据库连接超时时间（秒），每次尝试 15 秒，共尝试 2 次
DB_CONNECTION_TIMEOUT = 15
DB_MAX_RETRIES = 2


class MemoryManager:
    """Memory Manager 单例类"""

    _instance: Optional['MemoryManager'] = None
    _checkpointer: Optional[Union[AsyncPostgresSaver, MemorySaver]] = None
    _pool: Optional[AsyncConnectionPool] = None
    _setup_done: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _connect_with_retry(self, db_url: str) -> Optional[psycopg.Connection]:
        """带重试的数据库连接，每次 15 秒超时，共尝试 2 次"""
        last_error = None
        for attempt in range(1, DB_MAX_RETRIES + 1):
            try:
                logger.info(f"Attempting database connection (attempt {attempt}/{DB_MAX_RETRIES})")
                conn = psycopg.connect(db_url, autocommit=True, connect_timeout=DB_CONNECTION_TIMEOUT)
                logger.info(f"Database connection established on attempt {attempt}")
                return conn
            except Exception as e:
                last_error = e
                logger.warning(f"Database connection attempt {attempt} failed: {e}")
                if attempt < DB_MAX_RETRIES:
                    time.sleep(1)  # 重试前短暂等待
        logger.error(f"All {DB_MAX_RETRIES} database connection attempts failed, last error: {last_error}")
        return None

    def _setup_schema_and_tables(self, db_url: str) -> bool:
        """同步创建 schema 和表（只执行一次），返回是否成功"""
        if self._setup_done:
            return True

        conn = self._connect_with_retry(db_url)
        if conn is None:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute("CREATE SCHEMA IF NOT EXISTS memory")
            conn.execute("SET search_path TO memory")
            PostgresSaver(conn).setup()
            self._setup_done = True
            logger.info("Memory schema and tables created")
            return True
        except Exception as e:
            logger.warning(f"Failed to setup schema/tables: {e}")
            return False
        finally:
            conn.close()

    def _get_db_url_safe(self) -> Optional[str]:
        """安全获取 db_url，失败时返回 None"""
        try:
            from storage.database.db import get_db_url
            db_url = get_db_url()
            if db_url and db_url.strip():
                return db_url
            logger.warning("db_url is empty, will fallback to MemorySaver")
            return None
        except Exception as e:
            logger.warning(f"Failed to get db_url: {e}, will fallback to MemorySaver")
            return None

    def _create_fallback_checkpointer(self) -> MemorySaver:
        """创建内存兜底 checkpointer"""
        self._checkpointer = MemorySaver()
        logger.warning("Using MemorySaver as fallback checkpointer (data will not persist across restarts)")
        return self._checkpointer

    def get_checkpointer(self) -> BaseCheckpointSaver:
        """获取 checkpointer，优先使用 PostgresSaver，失败时退化为 MemorySaver"""
        if self._checkpointer is not None:
            return self._checkpointer

        # 1. 尝试获取 db_url
        db_url = self._get_db_url_safe()
        if not db_url:
            return self._create_fallback_checkpointer()

        # 2. 尝试连接数据库并创建 schema/表（带重试）
        if not self._setup_schema_and_tables(db_url):
            return self._create_fallback_checkpointer()

        # 3. 连接字符串加上 search_path 和超时参数（更严格的超时控制）
        timeout_params = "options=-csearch_path%3Dmemory%20-c%20statement_timeout%3D30000%20-c%20idle_in_transaction_session_timeout%3D20000%20-c%20lock_timeout%3D10000"
        if "?" in db_url:
            db_url = f"{db_url}&{timeout_params}"
        else:
            db_url = f"{db_url}?{timeout_params}"

        # 4. 尝试创建连接池和 checkpointer（优化连接池参数）
        try:
            self._pool = AsyncConnectionPool(
                conninfo=db_url,
                timeout=DB_CONNECTION_TIMEOUT,
                min_size=1,
                max_size=5,  # 限制最大连接数，避免过多连接占用
                max_idle=60,  # 减少最大空闲时间到60秒
                max_lifetime=300,  # 连接最大生命周期5分钟
            )
            # 修复deprecation warning：使用context manager或显式调用open()
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果event loop正在运行，使用create_task
                    asyncio.create_task(self._pool.open())
                else:
                    # 如果event loop未运行，使用run_until_complete
                    loop.run_until_complete(self._pool.open())
            except Exception as pool_open_error:
                logger.warning(f"Failed to open connection pool: {pool_open_error}, using pool directly")
            
            self._checkpointer = AsyncPostgresSaver(self._pool)
            logger.info("AsyncPostgresSaver initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to create AsyncPostgresSaver: {e}, will fallback to MemorySaver")
            return self._create_fallback_checkpointer()

        return self._checkpointer

_memory_manager: Optional[MemoryManager] = None


def get_memory_saver() -> BaseCheckpointSaver:
    """获取 checkpointer，优先使用 PostgresSaver，db_url 不可用或连接失败时退化为 MemorySaver"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager.get_checkpointer()