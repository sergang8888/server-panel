#!/bin/bash

# 头盔实时检测系统 - Linux一键安装脚本
# 支持Ubuntu/Debian/CentOS/RHEL等主流Linux发行版

set -e

echo "==========================================="
echo "    头盔实时检测系统 - 一键安装"
echo "==========================================="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ -f /etc/redhat-release ]; then
        OS="CentOS"
        VER=$(rpm -q --qf "%{VERSION}" $(rpm -q --whatprovides redhat-release))
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    echo -e "${GREEN}✅ 检测到操作系统: $OS $VER${NC}"
}

# 系统配置输入函数
get_user_config() {
    echo "==========================================="
    echo "           系统配置"
    echo "==========================================="
    echo
    echo "请输入系统配置信息（直接回车使用默认值）:"
    echo
    
    # 输入服务器端口
    read -p "请输入服务器端口 [默认: 5000]: " SERVER_PORT
    SERVER_PORT=${SERVER_PORT:-5000}
    echo "服务器端口: $SERVER_PORT"
    echo
    
    # 输入管理员账号
    read -p "请输入管理员账号 [默认: admin]: " ADMIN_USER
    ADMIN_USER=${ADMIN_USER:-admin}
    echo "管理员账号: $ADMIN_USER"
    echo
    
    # 输入管理员密码
    read -p "请输入管理员密码 [默认: admin123]: " ADMIN_PASS
    ADMIN_PASS=${ADMIN_PASS:-admin123}
    echo "管理员密码: $ADMIN_PASS"
    echo
    
    # 设置默认摄像头配置
    CAMERA_IP=192.168.1.100
    CAMERA_PORT=554
    CAMERA_USER=admin
    CAMERA_PASS=123456
    
    echo "==========================================="
    echo "           配置确认"
    echo "==========================================="
    echo "服务器端口: $SERVER_PORT"
    echo "管理员账号: $ADMIN_USER"
    echo "管理员密码: $ADMIN_PASS"
    echo "==========================================="
    echo
    
    read -p "确认以上配置？(y/n) [默认: y]: " CONFIRM
    CONFIRM=${CONFIRM:-y}
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "安装已取消"
        exit 0
    fi
    
    echo
    echo -e "${BLUE}🚀 开始安装...${NC}"
    echo
}

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo
    echo "=========================================="
    echo "    头盔实时检测系统 - 一键安装"
    echo "=========================================="
    echo
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Python版本
check_python() {
    print_info "检查Python环境..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "未找到Python，请先安装Python 3.8+"
        echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "Fedora: sudo dnf install python3 python3-pip"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 8 ]); then
        print_error "需要Python 3.8或更高版本，当前版本: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python版本: $PYTHON_VERSION"
}

# 检查pip
check_pip() {
    print_info "检查pip..."
    
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_warning "pip不可用，正在安装..."
        
        # 尝试安装pip
        if command_exists apt-get; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command_exists yum; then
            sudo yum install -y python3-pip
        elif command_exists dnf; then
            sudo dnf install -y python3-pip
        else
            print_error "无法自动安装pip，请手动安装"
            exit 1
        fi
        
        if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
            print_error "pip安装失败"
            exit 1
        fi
    fi
    
    print_success "pip可用"
}

# 安装系统依赖
install_system_deps() {
    print_info "安装系统依赖..."
    
    if command_exists apt-get; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y python3-venv python3-dev build-essential libopencv-dev
    elif command_exists yum; then
        # CentOS/RHEL
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3-devel opencv-devel
    elif command_exists dnf; then
        # Fedora
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y python3-devel opencv-devel
    else
        print_warning "无法识别的Linux发行版，跳过系统依赖安装"
    fi
    
    print_success "系统依赖安装完成"
}

# 创建虚拟环境
create_venv() {
    print_info "创建Python虚拟环境..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        if [ $? -ne 0 ]; then
            print_error "虚拟环境创建失败"
            exit 1
        fi
        print_success "虚拟环境创建成功"
    else
        print_success "虚拟环境已存在"
    fi
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖包..."
    
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装requirements.txt中的依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            print_error "依赖包安装失败"
            exit 1
        fi
        print_success "依赖包安装成功"
    else
        print_warning "requirements.txt不存在，跳过依赖安装"
    fi
    
    deactivate
}

# 创建启动脚本
create_scripts() {
    print_info "📝 创建启动脚本..."
    
    # 创建启动脚本
    cat > start_system.sh << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
echo "==========================================="
echo "    头盔实时检测系统"
echo "==========================================="
echo "🚀 正在启动系统..."
echo "服务器端口: $SERVER_PORT"
echo "管理员账号: $ADMIN_USER"
echo "访问地址: http://localhost:$SERVER_PORT"
echo "==========================================="
echo
source venv/bin/activate
python app.py
echo
echo "系统已停止运行"
read -p "按回车键退出..."
EOF
    
    chmod +x start_system.sh
    
    # 创建配置修改脚本
    cat > modify_config.sh << EOF
#!/bin/bash
echo "==========================================="
echo "       修改系统配置"
echo "==========================================="
echo "当前配置:"
echo "服务器端口: $SERVER_PORT"
echo "管理员账号: $ADMIN_USER"
echo "摄像头IP: $CAMERA_IP"
echo "==========================================="
echo "如需修改配置，请编辑 config_user.py 文件"
echo "修改后重新启动系统生效"
read -p "按回车键退出..."
EOF
    
    chmod +x modify_config.sh
    
    # 创建systemd服务安装脚本
    cat > install_service.sh << EOF
#!/bin/bash
# 安装systemd服务脚本

SERVICE_NAME="helmet-detection"
WORK_DIR="\$(pwd)"
USER="\$(whoami)"

# 创建systemd服务文件
sudo tee /etc/systemd/system/\${SERVICE_NAME}.service > /dev/null << EOL
[Unit]
Description=头盔实时检测系统
After=network.target

[Service]
Type=simple
User=\${USER}
WorkingDirectory=\${WORK_DIR}
Environment=PATH=\${WORK_DIR}/venv/bin
ExecStart=\${WORK_DIR}/venv/bin/python \${WORK_DIR}/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# 重新加载systemd并启用服务
sudo systemctl daemon-reload
sudo systemctl enable \${SERVICE_NAME}
sudo systemctl start \${SERVICE_NAME}

echo "✅ 系统服务安装完成"
echo "📋 服务管理命令:"
echo "  启动服务: sudo systemctl start \${SERVICE_NAME}"
echo "  停止服务: sudo systemctl stop \${SERVICE_NAME}"
echo "  重启服务: sudo systemctl restart \${SERVICE_NAME}"
echo "  查看状态: sudo systemctl status \${SERVICE_NAME}"
echo "  查看日志: sudo journalctl -u \${SERVICE_NAME} -f"
EOF
    
    chmod +x install_service.sh
    
    print_success "✅ 启动脚本创建完成"
}

# 创建目录结构
create_directories() {
    print_info "创建目录结构..."
    
    mkdir -p models logs
    
    print_success "目录结构创建完成"
}

# 检查系统文件
check_files() {
    print_info "检查系统文件..."
    
    missing_files=0
    
    if [ ! -f "app.py" ]; then
        print_error "app.py 缺失"
        missing_files=1
    fi
    
    if [ ! -f "templates/index.html" ]; then
        print_error "templates/index.html 缺失"
        missing_files=1
    fi
    
    if [ ! -d "static" ]; then
        print_error "static 目录缺失"
        missing_files=1
    fi
    
    if [ $missing_files -eq 1 ]; then
        print_warning "部分系统文件缺失，系统可能无法正常运行"
    else
        print_success "系统文件检查完成"
    fi
}

# 显示完成信息
show_completion() {
    echo
    echo "=========================================="
    echo "           🎉 安装完成！"
    echo "=========================================="
    echo
    echo "📋 系统配置:"
    echo "- 服务器端口: $SERVER_PORT"
    echo "- 管理员账号: $ADMIN_USER"
    echo "- 摄像头IP: $CAMERA_IP:$CAMERA_PORT"
    echo "- 访问地址: http://localhost:$SERVER_PORT"
    echo
    echo "📋 使用说明:"
    echo "1. 运行 ./start_system.sh 启动系统"
    echo "2. 运行 ./modify_config.sh 查看/修改配置"
    echo "3. 运行 ./install_service.sh 安装为系统服务"
    echo "4. 在浏览器中访问 http://localhost:$SERVER_PORT"
    echo
    echo "📁 重要目录:"
    echo "- 模型文件: models/"
    echo "- 日志文件: logs/"
    echo "- 配置文件: config_user.py"
    echo
    echo "🌐 系统功能:"
    echo "- 摄像头管理: 配置IP摄像头"
    echo "- AI功能配置: 加载检测模型"
    echo "- 网络管理: 配置网络参数"
    echo "- 系统监控: 查看系统状态"
    echo
    
    echo "🔐 登录信息:"
    echo "- 用户名: $ADMIN_USER"
    echo "- 密码: $ADMIN_PASS"
    echo
    
    read -p "是否立即启动系统？(y/n) [默认: y]: " START_NOW
    START_NOW=${START_NOW:-y}
    
    if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
        echo
        print_info "🚀 正在启动系统..."
        ./start_system.sh &
        sleep 2
        echo
        print_success "✅ 系统已在后台启动"
        print_info "🌐 请在浏览器中访问: http://localhost:$SERVER_PORT"
        print_info "🔐 使用账号 $ADMIN_USER 和密码 $ADMIN_PASS 登录"
        echo
    fi
    
    echo "如需停止系统，请使用 Ctrl+C 或关闭终端"
    echo "如需修改配置，请运行 ./modify_config.sh"
    echo
}

# 创建配置文件
create_config_file() {
    print_info "📝 创建配置文件..."
    
    cat > config_user.py << EOF
# 头盔实时检测系统 - 用户配置文件

# 服务器配置
HOST = '0.0.0.0'
PORT = $SERVER_PORT
DEBUG = False

# 管理员账号配置
ADMIN_USERNAME = '$ADMIN_USER'
ADMIN_PASSWORD = '$ADMIN_PASS'

# 摄像头默认配置
DEFAULT_CAMERA_IP = '$CAMERA_IP'
DEFAULT_CAMERA_PORT = $CAMERA_PORT
DEFAULT_CAMERA_USERNAME = '$CAMERA_USER'
DEFAULT_CAMERA_PASSWORD = '$CAMERA_PASS'
DEFAULT_STREAM_URL = '/stream'

# AI模型配置
MODEL_PATH = 'models'
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'
EOF
    
    print_success "✅ 配置文件创建完成"
}

# 主安装流程
main() {
    print_header
    
    # 检查是否为root用户
    if [ "$EUID" -eq 0 ]; then
        print_warning "不建议使用root用户运行此脚本"
        read -p "是否继续？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    detect_os
    get_user_config
    check_python
    check_pip
    install_system_deps
    create_venv
    install_python_deps
    create_config_file
    create_scripts
    create_directories
    check_files
    show_completion
}

# 错误处理
set -e
trap 'print_error "安装过程中发生错误，请检查上面的错误信息"' ERR

# 运行主函数
main "$@"