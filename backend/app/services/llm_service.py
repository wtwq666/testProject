"""Kimi LLM 接入、LangChain SQL Agent、上下文记忆"""
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.database.connection import get_database_url
from app.services.session_service import get_recent_messages

# SQL Agent 单例（延迟初始化）
_agent = None


def _get_llm():
    return ChatOpenAI(
        model=settings.KIMI_MODEL,
        openai_api_key=settings.KIMI_API_KEY,
        openai_api_base=settings.KIMI_BASE_URL,
        temperature=0.3,
    )


def _get_db():
    url = get_database_url()
    return SQLDatabase.from_uri(url)


def get_sql_agent():
    """获取或创建 SQL Agent"""
    global _agent
    if _agent is None:
        llm = _get_llm()
        db = _get_db()
        _agent = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="zero-shot-react-description",
            verbose=True,
        )
    return _agent


SYSTEM_PREFIX = """你是一个智能数据分析助手，基于 SQLite 数据库回答用户问题。

数据库表结构：
- departments: 部门表 (id, name, manager, budget)
- employees: 员工表 (id, name, department_id, position, salary, hire_date)
- products: 产品表 (id, name, category, price, stock)
- sales_records: 销售记录表 (id, product_id, employee_id, quantity, amount, sale_date)

规则：
1. 只执行 SELECT 查询，禁止 INSERT/UPDATE/DELETE。
2. 根据用户问题写出正确的 SQL 并执行，用自然语言总结结果。
3. 若查询结果适合可视化（如对比、趋势、占比），在回答末尾附带 ECharts 图表配置，格式如下：

[CHART]
{
  "title": {"text": "图表标题"},
  "xAxis": {"type": "category", "data": ["A", "B", "C"]},
  "yAxis": {"type": "value"},
  "series": [{"type": "bar", "data": [10, 20, 30]}]
}
[/CHART]

4. 图表 JSON 必须使用上述结构的有效 ECharts option，xAxis.data 和 series[0].data 来自查询结果。
"""


def build_chat_history(session_id: str) -> list:
    """从数据库加载最近 N 条消息，构建 LangChain 消息列表"""
    msgs = get_recent_messages(session_id, limit=settings.CONTEXT_WINDOW_SIZE)
    history = []
    for m in msgs:
        if m.role == "user":
            history.append(HumanMessage(content=m.content))
        else:
            # 去除 [CHART]...[/CHART] 部分，只保留文字
            content = m.content
            if "[CHART]" in content and "[/CHART]" in content:
                content = content.split("[CHART]")[0].strip()
            history.append(AIMessage(content=content))
    return history


def invoke_agent(question: str, session_id: str | None = None) -> str:
    """
    调用 SQL Agent 回答用户问题。
    若有 session_id 则加载最近消息作为上下文注入到 input。
    返回完整回答（含可能的 [CHART]...[/CHART]）
    """
    agent = get_sql_agent()
    chart_hint = "\n\n若查询结果适合可视化（如对比、趋势、占比），请在回答末尾附带 [CHART]{...ECharts option JSON...}[/CHART] 格式的图表配置。"
    input_text = question + chart_hint
    if session_id:
        history = build_chat_history(session_id)
        if history:
            ctx = "\n".join(
                ("用户: " + m.content) if isinstance(m, HumanMessage) else ("助手: " + m.content)
                for m in history
            )
            input_text = f"【历史对话上下文】\n{ctx}\n\n【当前用户问题】\n{question}{chart_hint}"
    result = agent.invoke({"input": input_text})
    return result.get("output", str(result)) if isinstance(result, dict) else str(result)
