#!/bin/bash

# 日志文件
LOG_FILE="/var/log/server-panel-install.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 输出到终端和日志文件
log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# 检查命令是否成功
check_status() {
    if [ $? -ne 0 ]; then
        log "错误: $1"
        exit 1
    fi
}

# 检查网络连接
check_network() {
    ping -c 1 github.com > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log "网络不可用，请检查网络连接"
        exit 1
    fi
}

# 检查磁盘空间（至少需要 1GB 可用空间）
check_disk_space() {
    AVAILABLE=$(df -h / | tail -1 | awk '{print $4}' | sed 's/G//')
    if (( $(echo "$AVAILABLE < 1" | bc -l) )); then
        log "磁盘空间不足，至少需要 1GB 可用空间"
        exit 1
    fi
}

# 安装 Docker
install_docker() {
    if ! command -v docker &> /dev/null; then
        log "Docker 未安装，正在安装..."
        sudo apt-get update -y >> "$LOG_FILE" 2>&1
        sudo apt-get install -y docker.io >> "$LOG_FILE" 2>&1
        check_status "Docker 安装失败"
        sudo systemctl start docker >> "$LOG_FILE" 2>&1
        sudo systemctl enable docker >> "$LOG_FILE" 2>&1
    else
        log "Docker 已安装"
    fi
}

# 安装面板
install_panel() {
    # 设置变量
    REPO_URL="https://github.com/sergang8888/server-panel.git"
    INSTALL_DIR="/tmp/server-panel-install"
    IMAGE_NAME="server-panel"
    CONTAINER_NAME="server-panel-container"
    PORT=${PORT:-8080} # 默认端口，可通过环境变量自定义

    # 前置检查
    check_network
    check_disk_space

    # 清理旧的安装目录
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        check_status "清理旧目录失败"
    fi

    # 下载项目
    log "正在下载项目..."
    git clone "$REPO_URL" "$INSTALL_DIR" >> "$LOG_FILE" 2>&1
    check_status "下载项目失败，请检查网络或仓库地址"

    # 进入项目目录
    cd "$INSTALL_DIR" || check_status "进入安装目录失败"

    # 构建 Docker 镜像
    log "正在构建 Docker 镜像..."
    docker build -t "$IMAGE_NAME" . >> "$LOG_FILE" 2>&1
    check_status "构建 Docker 镜像失败"

    # 停止并删除旧容器
    docker stop "$CONTAINER_NAME" >> "$LOG_FILE" 2>&1
    docker rm "$CONTAINER_NAME" >> "$LOG_FILE" 2>&1

    # 运行容器
    log "启动服务器管理面板..."
    docker run -d --name "$CONTAINER_NAME" -p "$PORT":8080 "$IMAGE_NAME" >> "$LOG_FILE" 2>&1
    check_status "启动容器失败"

    # 清理安装目录
    rm -rf "$INSTALL_DIR"
    log "安装完成！请访问 http://localhost:$PORT/frontend 使用面板"
    log "日志已记录到 $LOG_FILE"
}

# 卸载面板
uninstall_panel() {
    IMAGE_NAME="server-panel"
    CONTAINER_NAME="server-panel-container"

    log "正在卸载服务器管理面板..."
    docker stop "$CONTAINER_NAME" >> "$LOG_FILE" 2>&1
    docker rm "$CONTAINER_NAME" >> "$LOG_FILE" 2>&1
    docker rmi "$IMAGE_NAME" >> "$LOG_FILE" 2>&1
    log "卸载完成！镜像和容器已删除"
}

# 主逻辑
case "$1" in
    uninstall)
        uninstall_panel
        ;;
    *)
        install_panel
        ;;
esac
