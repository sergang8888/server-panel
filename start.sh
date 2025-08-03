#!/bin/bash

# Ubuntu 22 Web管理面板启动脚本

echo "=== Ubuntu 22 Web管理面板启动脚本 ==="
echo

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

echo "检测到Python版本: $(python3 --version)"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖包..."
pip install -r requirements.txt

# 检查权限
echo "检查系统权限..."
if [ "$EUID" -ne 0 ]; then
    echo "警告: 当前用户不是root，某些系统管理功能可能需要sudo权限"
    echo "建议使用: sudo ./start.sh"
fi

# 创建日志目录
mkdir -p logs

echo
echo "=== 启动Web管理面板 ==="
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo

# 启动应用
python3 app.py