"""
Phase1 方案验证脚本：对比 openai-tools 与 zero-shot-react-description 的返回质量。
在 backend 目录下运行: python scripts/verify_agent_type.py
需要已配置 .env 中的 KIMI_API_KEY，并已执行过 seed。
"""
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())

from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI

from app.config import settings
from app.database.connection import get_database_url


def run_verify():
    if not settings.KIMI_API_KEY:
        print("[WARN] KIMI_API_KEY 未配置，跳过实际调用，结论：采用方案 C（切换 + 清洗）")
        return "C"

    llm = ChatOpenAI(
        model=settings.KIMI_MODEL,
        openai_api_key=settings.KIMI_API_KEY,
        openai_api_base=settings.KIMI_BASE_URL,
        temperature=0.3,
    )
    db = SQLDatabase.from_uri(get_database_url())
    query = "各部门的销售对比"
    chart_hint = "\n\n若查询结果适合可视化，请在回答末尾附带 [CHART]{...ECharts option JSON...}[/CHART] 格式。"
    input_text = query + chart_hint

    results = {}
    for agent_type in ["openai-tools", "zero-shot-react-description"]:
        try:
            agent = create_sql_agent(llm=llm, db=db, agent_type=agent_type, verbose=False)
            result = agent.invoke({"input": input_text})
            output = result.get("output", str(result)) if isinstance(result, dict) else str(result)
            has_garbage = "functions.sql_db_" in output or ('"tool_input"' in output and "{" in output)
            results[agent_type] = {"has_garbage": has_garbage, "len": len(output), "output_preview": output[:300]}
            print(f"[{agent_type}] has_garbage={has_garbage}, len={len(output)}")
        except Exception as e:
            results[agent_type] = {"error": str(e)}
            print(f"[{agent_type}] ERROR: {e}")

    # 结论规则
    react = results.get("zero-shot-react-description", {})
    openai = results.get("openai-tools", {})

    if "error" in react:
        print("结论: 方案 B（仅输出清洗），ReAct 不兼容")
        return "B"
    if react.get("has_garbage") and openai.get("has_garbage"):
        print("结论: 方案 C（切换 + 清洗）")
        return "C"
    if not react.get("has_garbage"):
        print("结论: 方案 A（切换 agent_type）")
        return "A"
    print("结论: 方案 C（切换 + 清洗）")
    return "C"


if __name__ == "__main__":
    run_verify()
