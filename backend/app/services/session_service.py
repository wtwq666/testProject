"""会话服务层：sessions 表 + messages 表的 CRUD"""
import uuid
from datetime import datetime

from sqlalchemy.orm import Session as DBSession, selectinload

from app.database.connection import get_session_db_factory
from app.database.models import Message, Session as SessionModel


def _get_db():
    factory = get_session_db_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """获取会话库的 DB Session（用于依赖注入）"""
    return next(_get_db())


def create_session(title: str = "新对话") -> SessionModel:
    """创建新会话"""
    factory = get_session_db_factory()
    db = factory()
    try:
        sid = str(uuid.uuid4())
        now = datetime.utcnow()
        s = SessionModel(id=sid, title=title, created_at=now, updated_at=now)
        db.add(s)
        db.commit()
        db.refresh(s)
        return s
    finally:
        db.close()


def list_sessions() -> list[SessionModel]:
    """获取会话列表，按 updated_at 降序"""
    factory = get_session_db_factory()
    db = factory()
    try:
        return db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    finally:
        db.close()


def get_session(session_id: str) -> SessionModel | None:
    """获取会话详情（含消息）。预加载 messages 避免返回后惰性加载导致 DetachedInstanceError。"""
    factory = get_session_db_factory()
    db = factory()
    try:
        s = (
            db.query(SessionModel)
            .options(selectinload(SessionModel.messages))
            .filter(SessionModel.id == session_id)
            .first()
        )
        return s
    finally:
        db.close()


def rename_session(session_id: str, title: str) -> bool:
    """重命名会话"""
    factory = get_session_db_factory()
    db = factory()
    try:
        s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not s:
            return False
        s.title = title
        s.updated_at = datetime.utcnow()
        db.commit()
        return True
    finally:
        db.close()


def delete_session(session_id: str) -> bool:
    """删除会话（级联删除消息）"""
    factory = get_session_db_factory()
    db = factory()
    try:
        s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not s:
            return False
        db.delete(s)
        db.commit()
        return True
    finally:
        db.close()


def get_recent_messages(session_id: str, limit: int = 10) -> list[Message]:
    """获取会话最近 N 条消息（用于上下文）"""
    factory = get_session_db_factory()
    db = factory()
    try:
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )[::-1]
    finally:
        db.close()


def add_message(session_id: str, role: str, content: str, chart_data: dict | None = None) -> Message:
    """添加消息并更新会话 updated_at"""
    factory = get_session_db_factory()
    db = factory()
    try:
        mid = str(uuid.uuid4())
        m = Message(
            id=mid,
            session_id=session_id,
            role=role,
            content=content,
            chart_data=chart_data,
        )
        db.add(m)
        s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if s:
            s.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(m)
        return m
    finally:
        db.close()


def update_session_title_from_first_message(session_id: str, title: str) -> None:
    """根据首条用户消息更新会话标题（可选）"""
    rename_session(session_id, title[:200])
