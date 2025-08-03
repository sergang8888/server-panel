#!/bin/bash

echo
echo "=========================================="
echo "    Go Web Panel - 构建脚本"
echo "=========================================="
echo

# 检查Go是否安装
if ! command -v go &> /dev/null; then
    echo "Go未安装，请先安装Go 1.21+"
    echo "下载地址: https://golang.org/dl/"
    exit 1
fi

echo "Go已安装"
go version
echo

# 初始化Go模块（如果需要）
if [ ! -f "go.sum" ]; then
    echo "初始化Go模块依赖..."
    go mod tidy
    if [ $? -ne 0 ]; then
        echo "依赖安装失败"
        exit 1
    fi
    echo "依赖安装完成"
    echo
fi

# 构建应用
echo "开始构建Go Web Panel..."
go build -o webserver-panel .
if [ $? -ne 0 ]; then
    echo "构建失败"
    exit 1
fi

echo "构建成功！"
echo "可执行文件: webserver-panel"
echo

# 询问是否立即运行
read -p "是否立即运行应用？(y/n): " RUN_NOW
if [[ $RUN_NOW =~ ^[Yy]$ ]]; then
    echo
    echo "启动Go Web Panel..."
    echo "访问地址: http://localhost:5000"
    echo "按 Ctrl+C 停止服务器"
    echo
    ./webserver-panel
else
    echo
    echo "构建完成！运行以下命令启动应用:"
    echo "./webserver-panel"
    echo
fi