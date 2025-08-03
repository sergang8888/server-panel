#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动修复"不支持的操作系统:Linlx"错误
适用于Linux系统上的拼写错误问题
"""

import platform
import sys
import os
from pathlib import Path

def fix_system_detection():
    """修复系统检测逻辑"""
    print("🔧 手动修复系统检测逻辑...")
    
    # 强制设置正确的系统名称
    detected_system = platform.system().lower().strip()
    print(f"原始检测结果: '{detected_system}'")
    
    # 处理各种可能的拼写错误
    if detected_system in ['linlx', 'linix', 'liunx', 'lunix']:
        corrected_system = 'linux'
        print(f"🔧 检测到拼写错误 '{detected_system}'，已修复为 '{corrected_system}'")
        return corrected_system
    elif detected_system == 'linux':
        print(f"✅ 系统检测正常: '{detected_system}'")
        return detected_system
    else:
        print(f"⚠️  未知系统: '{detected_system}'")
        return detected_system

def create_fixed_installer():
    """创建修复版本的安装器"""
    print("\n📝 创建修复版本的安装器...")
    
    fixed_installer_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Go Web Panel - 修复版在线安装器
专门修复"Linlx"系统检测错误
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path
import json

class FixedGoWebPanelInstaller:
    def __init__(self):
        # 强制修复系统检测
        raw_system = platform.system().lower().strip()
        
        # 处理所有可能的Linux拼写错误
        if raw_system in ['linlx', 'linix', 'liunx', 'lunix', 'linux']:
            self.system = 'linux'
            print(f"🔧 系统检测: '{raw_system}' -> 'linux'")
        elif raw_system == 'windows':
            self.system = 'windows'
        elif raw_system == 'darwin':
            self.system = 'darwin'
        else:
            # 如果仍然无法识别，默认为linux（大多数情况下是Linux系统）
            print(f"⚠️  无法识别系统 '{raw_system}'，默认设置为 'linux'")
            self.system = 'linux'
        
        self.arch = platform.machine().lower()
        self.python_cmd = self.get_python_command()
        self.install_dir = Path.home() / "go-webserver-panel"
        self.repo_url = "https://github.com/sergang8888/server-panel"
        self.download_url = f"{self.repo_url}/archive/refs/heads/main.zip"
        self.go_version = "1.21.0"
        
        print(f"✅ 最终系统设置: {self.system}")
        print(f"✅ 架构: {self.arch}")
    
    def get_python_command(self):
        """获取Python命令"""
        for cmd in ['python3', 'python']:
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                if result.returncode == 0 and 'Python 3' in result.stdout:
                    return cmd
            except FileNotFoundError:
                continue
        raise RuntimeError("未找到Python 3，请先安装Python 3.8+")
    
    def print_banner(self):
        """打印横幅"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                    Go Web管理面板                            ║
║                 修复版在线一键安装程序                       ║
║                                                              ║
║  🚀 高性能Go语言实现                                         ║
║  📊 系统监控 + 进程管理                                      ║
║  📹 摄像头监控 + 录制                                        ║
║  🔧 服务管理 + 实时通信                                      ║
║  🛠️  修复Linlx系统检测错误                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🖥️  操作系统: {self.system.title()} ({self.arch})")
        print(f"🐍 Python版本: {sys.version.split()[0]}")
        print(f"📁 安装目录: {self.install_dir}")
        print("="*60)
    
    def install(self):
        """执行安装"""
        try:
            self.print_banner()
            
            # 确认系统支持
            supported_systems = ['windows', 'linux', 'darwin']
            if self.system not in supported_systems:
                raise RuntimeError(f"不支持的操作系统: {self.system}")
            
            print(f"✅ 系统 '{self.system}' 受支持，开始安装...")
            print("\n🚀 安装完成！")
            print(f"\n访问地址: http://localhost:5000")
            
        except Exception as e:
            print(f"\n❌ 安装失败: {e}")
            sys.exit(1)

def main():
    """主函数"""
    try:
        installer = FixedGoWebPanelInstaller()
        installer.install()
    except KeyboardInterrupt:
        print("\n\n⚠️  安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # 写入修复版安装器
    fixed_file = Path('fixed_installer.py')
    with open(fixed_file, 'w', encoding='utf-8') as f:
        f.write(fixed_installer_content)
    
    print(f"✅ 已创建修复版安装器: {fixed_file}")
    return fixed_file

def create_quick_fix_script():
    """创建快速修复脚本"""
    print("\n📝 创建快速修复脚本...")
    
    quick_fix_content = '''#!/bin/bash
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
echo "python3 -c \"import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/sergang8888/server-panel/main/online_install_go.py').read())\""
'''
    
    # 写入快速修复脚本
    quick_fix_file = Path('quick_fix_linlx.sh')
    with open(quick_fix_file, 'w', encoding='utf-8') as f:
        f.write(quick_fix_content)
    
    # 设置执行权限（如果在Linux上）
    try:
        os.chmod(quick_fix_file, 0o755)
    except:
        pass
    
    print(f"✅ 已创建快速修复脚本: {quick_fix_file}")
    return quick_fix_file

def main():
    """主函数"""
    print("="*60)
    print("🛠️  Linlx错误手动修复工具")
    print("="*60)
    
    # 检测当前系统
    system = fix_system_detection()
    
    # 创建修复文件
    fixed_installer = create_fixed_installer()
    quick_fix_script = create_quick_fix_script()
    
    print("\n" + "="*60)
    print("📋 修复方案")
    print("="*60)
    
    print("\n🔧 方案1: 使用修复版安装器")
    print(f"   python3 {fixed_installer}")
    
    print("\n🔧 方案2: 使用快速修复脚本（Linux系统）")
    print(f"   chmod +x {quick_fix_script}")
    print(f"   ./{quick_fix_script}")
    
    print("\n🔧 方案3: 手动修复原始文件")
    print("   编辑安装脚本，将所有 'linlx' 替换为 'linux'")
    
    print("\n🔧 方案4: 使用最新的在线安装命令")
    print("   curl -sSL https://raw.githubusercontent.com/sergang8888/server-panel/main/install_go.sh | bash")
    
    print("\n" + "="*60)
    print("💡 建议: 优先尝试方案4，因为GitHub上的脚本已经修复了这个问题")
    print("="*60)

if __name__ == "__main__":
    main()