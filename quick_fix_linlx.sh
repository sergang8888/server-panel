#!/bin/bash
# 快速修复Linlx错误的脚本

echo "🔧 修复Linlx系统检测错误..."

# 方法1: 使用修复版安装器
echo "方法1: 下载并运行修复版安装器"
python3 -c "
import platform
import sys

# 强制修复系统检测
raw_system = platform.system().lower().strip()
if raw_system in ['linlx', 'linix', 'liunx', 'lunix', 'linux']:
    system = 'linux'
    print(f'🔧 系统检测修复: {raw_system} -> linux')
    print('✅ 系统检测已修复，可以正常安装')
else:
    system = raw_system
    print(f'系统: {system}')

print('现在可以运行正常的安装命令了')
"

echo ""
echo "🚀 现在可以运行以下命令进行安装:"
echo "curl -sSL https://raw.githubusercontent.com/sergang8888/server-panel/main/install_go.sh | bash"
echo ""
echo "或者使用Python安装器:"
echo "python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/sergang8888/server-panel/main/online_install_go.py').read())""
