"""FastAPI 入口：CORS、路由、启动时初始化数据库"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时创建表并可选执行 seed"""
    init_db()
    yield
    # shutdown 可做清理


app = FastAPI(
    title="SmartDataAssistant API",
    description="智能数据分析助理后端",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """健康检查"""
    return {"status": "ok"}


# 后续 Phase 在此挂载: app.include_router(session_router, prefix="/api", tags=["session"])
# app.include_router(chat_router, prefix="/api", tags=["chat"])
