#!/bin/bash

# 检查是否安装了 Docker
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，正在安装..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
else
    echo "Docker 已安装"
fi

# 设置变量
REPO_URL="https://github.com/sergang8888/server-panel.git"
INSTALL_DIR="/tmp/server-panel-install"
IMAGE_NAME="server-panel"
CONTAINER_NAME="server-panel-container"

# 清理旧的安装目录
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi

# 克隆项目
echo "正在下载项目..."
git clone "$REPO_URL" "$INSTALL_DIR" || {
    echo "下载失败，请检查网络或仓库地址"
    exit 1
}

# 进入项目目录
cd "$INSTALL_DIR" || exit

# 构建 Docker 镜像
echo "正在构建 Docker 镜像..."
docker build -t "$IMAGE_NAME" . || {
    echo "构建失败，请检查 Dockerfile"
    exit 1
}

# 停止并删除旧容器（如果存在）
docker stop "$CONTAINER_NAME" 2>/dev/null
docker rm "$CONTAINER_NAME" 2>/dev/null

# 运行容器
echo "启动服务器管理面板..."
docker run -d --name "$CONTAINER_NAME" -p 8080:8080 "$IMAGE_NAME" || {
    echo "启动失败，请检查 Docker 配置"
    exit 1
}

# 清理安装目录
rm -rf "$INSTALL_DIR"

# 输出成功信息
echo "安装完成！请访问 http://localhost:8080/frontend 使用面板"
