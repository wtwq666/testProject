"""聊天 SSE 流式接口"""
import asyncio
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.services.llm_service import invoke_agent
from app.services.session_service import add_message, get_session
from app.services.viz_service import parse_chart_from_response

router = APIRouter()


class ChatStreamBody(BaseModel):
    session_id: str
    message: str


async def _chat_stream_generator(session_id: str, user_message: str):
    """SSE 生成器：先保存用户消息，调用 Agent，解析并流式返回"""
    # 1. 校验会话存在
    s = get_session(session_id)
    if not s:
        yield {"event": "error", "data": json.dumps({"error": "Session not found"})}
        return

    # 2. 保存用户消息
    add_message(session_id, "user", user_message)

    # 3. 调用 Agent（同步阻塞，放到线程池避免阻塞事件循环）
    try:
        full_response = await asyncio.to_thread(invoke_agent, user_message, session_id)
    except Exception as e:
        yield {"event": "error", "data": json.dumps({"error": str(e)})}
        return

    # 4. 解析文字与图表
    text, chart_option = parse_chart_from_response(full_response)

    # 5. 保存助手消息
    msg = add_message(session_id, "assistant", text, chart_data=chart_option)

    # 6. 流式推送
    yield {"event": "message", "data": json.dumps({"content": text})}
    if chart_option:
        yield {"event": "chart", "data": json.dumps({"option": chart_option})}
    yield {"event": "done", "data": json.dumps({"message_id": msg.id})}


@router.post("/chat/stream")
async def api_chat_stream(body: ChatStreamBody):
    """SSE 流式聊天接口"""
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="message 不能为空")
    return EventSourceResponse(
        _chat_stream_generator(body.session_id, body.message.strip()),
    )
