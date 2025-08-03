#!/bin/bash

# Ubuntu Web管理面板安装脚本
# 适用于Ubuntu 22.04 LTS

set -e

echo "=== Ubuntu Web管理面板安装脚本 ==="
echo "适用于Ubuntu 22.04 LTS"
echo

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "错误: 请使用root权限运行此脚本"
    echo "使用: sudo ./install.sh"
    exit 1
fi

# 检查系统版本
if ! grep -q "Ubuntu 22" /etc/os-release; then
    echo "警告: 此脚本专为Ubuntu 22.04设计，其他版本可能不兼容"
    read -p "是否继续安装? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1. 更新系统包..."
apt update
apt upgrade -y

echo "2. 安装必要的系统包..."
apt install -y python3 python3-pip python3-venv git curl wget

echo "3. 创建安装目录..."
INSTALL_DIR="/opt/ubuntu-web-panel"
mkdir -p $INSTALL_DIR

echo "4. 复制文件到安装目录..."
cp -r . $INSTALL_DIR/
cd $INSTALL_DIR

echo "5. 设置文件权限..."
chown -R root:root $INSTALL_DIR
chmod +x start.sh
chmod +x install.sh

echo "6. 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

echo "7. 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

echo "8. 创建日志目录..."
mkdir -p logs
chown -R root:root logs

echo "9. 安装systemd服务..."
cp ubuntu-web-panel.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ubuntu-web-panel

echo "10. 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 5000/tcp
    echo "已允许端口5000通过防火墙"
fi

echo "11. 启动服务..."
systemctl start ubuntu-web-panel

echo
echo "=== 安装完成 ==="
echo
echo "服务状态:"
systemctl status ubuntu-web-panel --no-pager -l
echo
echo "访问地址: http://$(hostname -I | awk '{print $1}'):5000"
echo "本地访问: http://localhost:5000"
echo
echo "常用命令:"
echo "  启动服务: sudo systemctl start ubuntu-web-panel"
echo "  停止服务: sudo systemctl stop ubuntu-web-panel"
echo "  重启服务: sudo systemctl restart ubuntu-web-panel"
echo "  查看状态: sudo systemctl status ubuntu-web-panel"
echo "  查看日志: sudo journalctl -u ubuntu-web-panel -f"
echo
echo "配置文件位置: $INSTALL_DIR"
echo "日志文件位置: $INSTALL_DIR/logs/"
echo
echo "如需卸载，请运行: sudo systemctl stop ubuntu-web-panel && sudo systemctl disable ubuntu-web-panel && sudo rm -rf $INSTALL_DIR && sudo rm /etc/systemd/system/ubuntu-web-panel.service"
echo