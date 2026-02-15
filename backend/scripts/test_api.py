"""
Phase3 接口测试脚本。在 backend 目录下运行: python scripts/test_api.py
需要已配置 .env 中的 KIMI_API_KEY，并已执行过 seed。
"""
import json
import os
import sys

# 确保 backend 为当前工作目录，以便导入 app
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
results = []


def ok(name: str, res):
    if res.status_code >= 200 and res.status_code < 300:
        results.append((name, True, res.status_code, None))
        print(f"  [PASS] {name} -> {res.status_code}")
        return True
    results.append((name, False, res.status_code, res.text))
    print(f"  [FAIL] {name} -> {res.status_code} {res.text[:200]}")
    return False


def main():
    print("=== Phase3 API 测试 ===\n")

    # 1. 健康检查
    print("1. 健康检查")
    r = client.get("/health")
    ok("GET /health", r)

    # 2. 创建会话
    print("\n2. 创建会话")
    r = client.post("/api/sessions?title=测试会话")
    if not ok("POST /api/sessions", r):
        print("  跳过后续依赖会话的测试")
        summary()
        return
    data = r.json()
    sid = data.get("id")
    if not sid:
        results.append(("POST /api/sessions 返回 id", False, 0, str(data)))
        print("  无 session id，跳过后续测试")
        summary()
        return
    print(f"   Session ID: {sid}")

    # 3. 会话列表
    print("\n3. 会话列表")
    r = client.get("/api/sessions")
    ok("GET /api/sessions", r)
    if r.status_code == 200 and isinstance(r.json().get("sessions"), list):
        results.append(("GET /api/sessions 返回列表", True, 200, None))
        print("  [PASS] 返回 sessions 列表")
    else:
        results.append(("GET /api/sessions 返回列表", False, r.status_code, r.text))

    # 4. 会话详情
    print("\n4. 会话详情")
    r = client.get(f"/api/sessions/{sid}")
    ok("GET /api/sessions/{id}", r)

    # 5. 重命名
    print("\n5. 重命名会话")
    r = client.put(f"/api/sessions/{sid}", json={"title": "重命名测试"})
    ok("PUT /api/sessions/{id}", r)

    # 6. 聊天流式（需要 KIMI_API_KEY 和 seed 数据）
    print("\n6. 聊天流式 POST /api/chat/stream")
    try:
        r = client.post(
            "/api/chat/stream",
            json={"session_id": sid, "message": "各部门员工人数各有多少？"},
            timeout=90,
        )
        if r.status_code != 200:
            ok("POST /api/chat/stream", r)
        else:
            text = r.text or ""
            has_message = "event: message" in text or "event:message" in text.replace(" ", "")
            has_done = "event: done" in text or "event:done" in text.replace(" ", "")
            if has_message and has_done:
                results.append(("POST /api/chat/stream", True, 200, None))
                print("  [PASS] POST /api/chat/stream -> 200, 含 message 与 done 事件")
            else:
                results.append(("POST /api/chat/stream", False, 200, "缺少 message 或 done 事件"))
                print("  [FAIL] 响应中缺少 message 或 done 事件")
    except Exception as e:
        results.append(("POST /api/chat/stream", False, 0, str(e)))
        print(f"  [FAIL] 异常: {e}")

    # 7. 删除会话（用新会话测，避免删掉上面的）
    print("\n7. 删除会话")
    r2 = client.post("/api/sessions?title=待删除")
    if r2.status_code == 200:
        del_id = r2.json().get("id")
        if del_id:
            r = client.delete(f"/api/sessions/{del_id}")
            ok("DELETE /api/sessions/{id}", r)
        else:
            results.append(("DELETE 准备", False, 0, "无 id"))
    else:
        results.append(("DELETE 准备", False, r2.status_code, r2.text))

    summary()


def summary():
    print("\n=== 测试汇总 ===")
    passed = sum(1 for _, p, _, _ in results if p)
    total = len(results)
    for name, p, code, err in results:
        status = "PASS" if p else "FAIL"
        print(f"  [{status}] {name}" + (f" ({code})" if code else "") + (f" -> {err[:80]}" if err else ""))
    print(f"\n通过: {passed}/{total}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
