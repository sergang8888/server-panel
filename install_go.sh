#!/bin/bash

# Go Web Panel - 一键安装脚本 (无Python依赖)
# 支持 Linux/macOS 系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
GO_VERSION="1.21.0"
PROJECT_NAME="webserver-panel"
# 请将下面的仓库地址替换为实际的GitHub仓库地址
GITHUB_REPO="sergang8888/server-panel"
INSTALL_DIR="$HOME/webserver-panel"
GO_INSTALL_DIR="$HOME/go"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统和架构
detect_os_arch() {
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    case $ARCH in
        x86_64) ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        armv7l) ARCH="armv6l" ;;
        *) print_error "不支持的架构: $ARCH"; exit 1 ;;
    esac
    
    case $OS in
        linux) OS="linux" ;;
        darwin) OS="darwin" ;;
        *) print_error "不支持的操作系统: $OS"; exit 1 ;;
    esac
    
    print_info "检测到系统: $OS-$ARCH"
}

# 检查Go是否已安装
check_go() {
    if command -v go >/dev/null 2>&1; then
        GO_VERSION_INSTALLED=$(go version | awk '{print $3}' | sed 's/go//')
        print_info "检测到Go版本: $GO_VERSION_INSTALLED"
        return 0
    else
        print_warning "未检测到Go环境"
        return 1
    fi
}

# 安装Go
install_go() {
    print_info "开始安装Go $GO_VERSION..."
    
    GO_TARBALL="go${GO_VERSION}.${OS}-${ARCH}.tar.gz"
    GO_URL="https://golang.org/dl/${GO_TARBALL}"
    
    # 创建临时目录
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # 下载Go
    print_info "下载Go安装包..."
    if command -v curl >/dev/null 2>&1; then
        curl -L "$GO_URL" -o "$GO_TARBALL"
    elif command -v wget >/dev/null 2>&1; then
        wget "$GO_URL" -O "$GO_TARBALL"
    else
        print_error "需要curl或wget来下载文件"
        exit 1
    fi
    
    # 解压并安装
    print_info "安装Go到 $GO_INSTALL_DIR..."
    mkdir -p "$GO_INSTALL_DIR"
    tar -C "$GO_INSTALL_DIR" --strip-components=1 -xzf "$GO_TARBALL"
    
    # 设置环境变量
    export PATH="$GO_INSTALL_DIR/bin:$PATH"
    export GOPATH="$HOME/go-workspace"
    export GOROOT="$GO_INSTALL_DIR"
    
    # 添加到shell配置文件
    SHELL_RC="$HOME/.bashrc"
    if [[ "$SHELL" == */zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if ! grep -q "GO_INSTALL_DIR" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Go environment" >> "$SHELL_RC"
        echo "export PATH=\"$GO_INSTALL_DIR/bin:\$PATH\"" >> "$SHELL_RC"
        echo "export GOPATH=\"$HOME/go-workspace\"" >> "$SHELL_RC"
        echo "export GOROOT=\"$GO_INSTALL_DIR\"" >> "$SHELL_RC"
    fi
    
    # 清理临时文件
    cd /
    rm -rf "$TEMP_DIR"
    
    print_success "Go安装完成!"
}

# 下载项目源码
download_source() {
    print_info "下载项目源码..."
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "目录已存在，正在更新..."
        cd "$INSTALL_DIR"
        if [ -d ".git" ]; then
            git pull
        else
            cd ..
            rm -rf "$INSTALL_DIR"
            git clone "https://github.com/${GITHUB_REPO}.git" "$INSTALL_DIR"
        fi
    else
        git clone "https://github.com/${GITHUB_REPO}.git" "$INSTALL_DIR"
    fi
    
    cd "$INSTALL_DIR"
    print_success "源码下载完成!"
}

# 构建应用
build_app() {
    print_info "构建Go应用..."
    
    cd "$INSTALL_DIR"
    
    # 下载依赖
    go mod tidy
    
    # 构建应用
    go build -o "$PROJECT_NAME" .
    
    # 设置执行权限
    chmod +x "$PROJECT_NAME"
    
    print_success "应用构建完成!"
}

# 创建配置文件
create_config() {
    print_info "创建配置文件..."
    
    if [ ! -f "config.json" ]; then
        cat > config.json << EOF
{
    "port": 5000,
    "camera_ip": "192.168.1.100",
    "camera_username": "admin",
    "camera_password": "admin123",
    "log_level": "info",
    "max_log_size": 10,
    "max_log_files": 5
}
EOF
        print_success "配置文件创建完成!"
    else
        print_info "配置文件已存在，跳过创建"
    fi
}

# 创建启动脚本
create_startup_script() {
    print_info "创建启动脚本..."
    
    # 创建启动脚本
    cat > start.sh << 'EOF'
#!/bin/bash

# Go Web Panel 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "启动 Go Web Panel..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

./webserver-panel
EOF
    
    chmod +x start.sh
    
    # 创建systemd服务文件
    if command -v systemctl >/dev/null 2>&1; then
        cat > go-webserver-panel.service << EOF
[Unit]
Description=Go Web Server Panel
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/$PROJECT_NAME
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
        
        print_info "systemd服务文件已创建: go-webserver-panel.service"
        print_info "要安装服务，请运行: sudo cp go-webserver-panel.service /etc/systemd/system/"
        print_info "然后运行: sudo systemctl enable go-webserver-panel"
    fi
    
    print_success "启动脚本创建完成!"
}

# 主安装流程
main() {
    echo "======================================"
    echo "    Go Web Panel 一键安装脚本"
    echo "======================================"
    echo ""
    
    # 检测系统
    detect_os_arch
    
    # 检查Go环境
    if ! check_go; then
        read -p "是否安装Go环境? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_go
        else
            print_error "需要Go环境才能继续安装"
            exit 1
        fi
    fi
    
    # 检查git
    if ! command -v git >/dev/null 2>&1; then
        print_error "需要git来下载源码"
        print_info "请先安装git: sudo apt install git 或 brew install git"
        exit 1
    fi
    
    # 下载源码
    download_source
    
    # 构建应用
    build_app
    
    # 创建配置
    create_config
    
    # 创建启动脚本
    create_startup_script
    
    echo ""
    print_success "安装完成!"
    echo ""
    echo "使用方法:"
    echo "  启动服务: cd $INSTALL_DIR && ./start.sh"
    echo "  直接运行: cd $INSTALL_DIR && ./$PROJECT_NAME"
    echo "  访问地址: http://localhost:5000"
    echo ""
    
    # 询问是否立即启动
    read -p "是否立即启动服务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$INSTALL_DIR"
        print_info "启动服务..."
        ./$PROJECT_NAME
    fi
}

# 运行主函数
main "$@"