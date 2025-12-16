#!/bin/bash
# MCP 服务器调试脚本

CONFIG_FILE="${1:-config.json}"
BINARY="./dist/mcp-db-ro"

echo "🔍 检查 MCP 服务器..."
echo ""

# 1. 检查二进制文件
if [ ! -f "$BINARY" ]; then
    echo "❌ 二进制文件不存在: $BINARY"
    echo "   运行: make build"
    exit 1
fi
echo "✅ 二进制文件存在"

# 2. 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    echo "   创建配置文件: cp config.example.json config.json"
    exit 1
fi
echo "✅ 配置文件存在: $CONFIG_FILE"

# 3. 验证 JSON 格式
if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
    echo "❌ 配置文件 JSON 格式错误"
    exit 1
fi
echo "✅ JSON 格式正确"

# 4. 尝试启动（1秒超时）
echo ""
echo "📡 尝试连接数据库..."
timeout 2 "$BINARY" --db "$CONFIG_FILE" 2>&1 &
PID=$!
sleep 1
if kill -0 $PID 2>/dev/null; then
    echo "✅ 服务器启动成功！"
    kill $PID 2>/dev/null
    exit 0
else
    wait $PID
    EXIT_CODE=$?
    echo ""
    echo "❌ 启动失败 (exit code: $EXIT_CODE)"
    echo ""
    echo "💡 常见问题："
    echo "   - 数据库是否在运行？"
    echo "   - 用户名/密码是否正确？"
    echo "   - 网络连接是否正常？"
    echo "   - 防火墙是否阻止连接？"
    exit 1
fi
