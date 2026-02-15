"""可视化服务：解析 [CHART]...[/CHART]，校验并补全 ECharts option"""
import json
import re


def extract_chart_json(text: str) -> str | None:
    """从 LLM 回答中提取 [CHART]...[/CHART] 内的 JSON 字符串"""
    m = re.search(r"\[CHART\](.*?)\[/CHART\]", text, re.DOTALL)
    if not m:
        return None
    return m.group(1).strip()


def ensure_echarts_option(raw: dict) -> dict:
    """
    校验并补全 ECharts option。
    确保有 tooltip、legend（如有多系列）、响应式等基础配置。
    """
    opt = dict(raw)
    if "tooltip" not in opt:
        opt["tooltip"] = {"trigger": "axis", "axisPointer": {"type": "shadow"}}
    if "series" in opt:
        for s in opt["series"]:
            if isinstance(s, dict) and "type" not in s:
                s["type"] = "bar"
    return opt


def parse_chart_from_response(full_response: str) -> tuple[str, dict | None]:
    """
    从完整 LLM 回答中分离：
    1. 纯文字部分（不含 [CHART]...[/CHART]）
    2. 图表 option（若有且有效）
    """
    chart_raw = extract_chart_json(full_response)
    text = re.sub(r"\[CHART\].*?\[/CHART\]", "", full_response, flags=re.DOTALL).strip()

    if not chart_raw:
        return text, None

    try:
        data = json.loads(chart_raw)
        if isinstance(data, dict):
            return text, ensure_echarts_option(data)
    except json.JSONDecodeError:
        pass
    return text, None
