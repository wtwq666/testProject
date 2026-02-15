"""SQLite 连接管理"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database.models import BusinessBase, SessionBase


def _ensure_data_dir(url: str) -> str:
    """确保 data 目录存在，并返回绝对路径的 URL"""
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "").split("?")[0]
        if not path.startswith("/") and ":" not in path[:2]:
            base = Path(__file__).resolve().parent.parent.parent
            full = base / path
            full.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{full.as_posix()}"
    return url


def get_database_url() -> str:
    """获取业务库的解析后 URL（供 LangChain SQLDatabase 使用）"""
    return _ensure_data_dir(settings.DATABASE_URL)


def get_engine(db_url: str | None = None):
    """获取业务数据库 engine"""
    url = db_url or settings.DATABASE_URL
    url = _ensure_data_dir(url)
    return create_engine(url, connect_args={"check_same_thread": False}, echo=False)


def get_session_db_engine():
    """获取会话数据库 engine"""
    url = _ensure_data_dir(settings.SESSION_DB_URL)
    return create_engine(url, connect_args={"check_same_thread": False}, echo=False)


def get_session_factory(engine=None):
    """获取业务库 Session 工厂"""
    engine = engine or get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session_db_factory():
    """获取会话库 Session 工厂"""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_session_db_engine())


def init_db():
    """创建所有表（业务库 + 会话库）"""
    engine = get_engine()
    session_engine = get_session_db_engine()
    BusinessBase.metadata.create_all(bind=engine)
    SessionBase.metadata.create_all(bind=session_engine)
