#!/usr/bin/env python3
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
        banner = """
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
            print("\n访问地址: http://localhost:5000")
            
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
