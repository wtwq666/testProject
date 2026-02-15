"""会话管理 API：创建 / 列表 / 详情 / 重命名 / 删除"""
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

from app.services.session_service import (
    create_session,
    delete_session,
    get_session,
    list_sessions,
    rename_session,
)

router = APIRouter()


class RenameBody(BaseModel):
    title: str


@router.post("/sessions")
def api_create_session(title: str = "新对话"):
    """创建新会话"""
    s = create_session(title=title)
    return {"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()}


@router.get("/sessions")
def api_list_sessions():
    """获取会话列表"""
    items = list_sessions()
    return {
        "sessions": [
            {"id": s.id, "title": s.title, "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()}
            for s in items
        ]
    }


@router.get("/sessions/{session_id}")
def api_get_session(session_id: str):
    """获取会话详情（含消息）"""
    s = get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": s.id,
        "title": s.title,
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat(),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "chart_data": m.chart_data,
                "created_at": m.created_at.isoformat(),
            }
            for m in sorted(s.messages, key=lambda x: x.created_at or "")
        ],
    }


@router.put("/sessions/{session_id}")
def api_rename_session(session_id: str, body: RenameBody):
    """重命名会话"""
    title = body.title
    ok = rename_session(session_id, title)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


@router.delete("/sessions/{session_id}")
def api_delete_session(session_id: str):
    """删除会话"""
    ok = delete_session(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}
