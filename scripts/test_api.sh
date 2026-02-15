#!/bin/bash
# Phase3 后端接口测试脚本（需先启动后端 uvicorn 及执行 seed）
# 用法: bash scripts/test_api.sh

BASE="http://localhost:8000/api"

echo "=== 1. 健康检查 ==="
curl -s "http://localhost:8000/health" | head -1

echo -e "\n\n=== 2. 创建会话 ==="
S=$(curl -s -X POST "$BASE/sessions?title=测试会话")
echo "$S"
SID=$(echo "$S" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
echo "Session ID: $SID"

echo -e "\n\n=== 3. 获取会话列表 ==="
curl -s "$BASE/sessions" | head -5

echo -e "\n\n=== 4. 获取会话详情 ==="
curl -s "$BASE/sessions/$SID" | head -10

echo -e "\n\n=== 5. 重命名会话 ==="
curl -s -X PUT "$BASE/sessions/$SID" -H "Content-Type: application/json" -d '{"title":"重命名测试"}'

echo -e "\n\n=== 6. 聊天流式 (需要 KIMI_API_KEY) ==="
echo "POST $BASE/chat/stream 发送: 各部门销售额对比"
curl -s -X POST "$BASE/chat/stream" -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SID\",\"message\":\"各部门销售额对比\"}" | head -20

echo -e "\n\n测试完成"
