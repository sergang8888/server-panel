#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头盔实时检测系统 - 一键安装脚本
支持Windows和Linux系统的自动安装
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

class HelmetDetectionInstaller:
    def __init__(self):
        # 修复可能的系统名称拼写错误
        detected_system = platform.system().lower().strip()
        if detected_system == 'linlx':  # 修复常见的拼写错误
            self.system = 'linux'
        else:
            self.system = detected_system
        self.arch = platform.machine().lower()
        self.python_cmd = self.get_python_command()
        self.install_dir = Path.cwd() / "helmet-detection-system"
        
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
    
    def check_requirements(self):
        """检查系统要求"""
        print("🔍 检查系统要求...")
        
        # 检查Python版本
        version_info = sys.version_info
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            raise RuntimeError("需要Python 3.8或更高版本")
        print(f"✅ Python版本: {version_info.major}.{version_info.minor}.{version_info.micro}")
        
        # 检查pip
        try:
            subprocess.run([self.python_cmd, '-m', 'pip', '--version'], 
                         capture_output=True, check=True)
            print("✅ pip已安装")
        except subprocess.CalledProcessError:
            raise RuntimeError("pip未安装，请先安装pip")
    
    def create_directory(self):
        """创建安装目录"""
        print(f"📁 创建安装目录: {self.install_dir}")
        self.install_dir.mkdir(exist_ok=True)
        os.chdir(self.install_dir)
    
    def download_source(self):
        """下载源代码（模拟从GitHub下载）"""
        print("📥 下载源代码...")
        
        # 这里应该是实际的GitHub仓库地址
        # github_url = "https://github.com/your-repo/helmet-detection-system/archive/main.zip"
        
        # 由于这是演示，我们直接复制当前目录的文件
        source_dir = Path(__file__).parent
        files_to_copy = [
            'app.py', 'config.py', 'ai_processor.py', 'requirements.txt',
            'templates', 'static', 'models'
        ]
        
        for item in files_to_copy:
            src = source_dir / item
            if src.exists():
                if src.is_file():
                    shutil.copy2(src, self.install_dir)
                else:
                    shutil.copytree(src, self.install_dir / item, dirs_exist_ok=True)
        
        print("✅ 源代码下载完成")
    
    def create_virtual_environment(self):
        """创建虚拟环境"""
        print("🐍 创建Python虚拟环境...")
        
        venv_path = self.install_dir / "venv"
        if venv_path.exists():
            print("虚拟环境已存在，跳过创建")
            return
        
        subprocess.run([self.python_cmd, '-m', 'venv', 'venv'], check=True)
        print("✅ 虚拟环境创建完成")
    
    def get_venv_python(self):
        """获取虚拟环境中的Python命令"""
        if self.system == 'windows':
            return str(self.install_dir / "venv" / "Scripts" / "python.exe")
        else:
            return str(self.install_dir / "venv" / "bin" / "python")
    
    def install_dependencies(self):
        """安装依赖包"""
        print("📦 安装依赖包...")
        
        venv_python = self.get_venv_python()
        
        # 升级pip
        subprocess.run([venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True)
        
        # 安装requirements.txt中的依赖
        requirements_file = self.install_dir / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                          check=True)
        
        print("✅ 依赖包安装完成")
    
    def create_startup_scripts(self):
        """创建启动脚本"""
        print("📝 创建启动脚本...")
        
        if self.system == 'windows':
            # Windows批处理文件
            start_script = self.install_dir / "start.bat"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(f"""@echo off
cd /d "{self.install_dir}"
venv\\Scripts\\python.exe app.py
pause
""")
            
            # 创建桌面快捷方式脚本
            desktop_script = self.install_dir / "create_desktop_shortcut.bat"
            with open(desktop_script, 'w', encoding='utf-8') as f:
                f.write(f"""@echo off
set SCRIPT="%USERPROFILE%\\Desktop\\头盔检测系统.lnk"
set TARGET="{start_script}"
set PWS=powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile

%PWS% -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SCRIPT%'); $S.TargetPath = '%TARGET%'; $S.Save()"
echo 桌面快捷方式已创建
pause
""")
        
        else:
            # Linux shell脚本
            start_script = self.install_dir / "start.sh"
            with open(start_script, 'w') as f:
                f.write(f"""#!/bin/bash
cd "{self.install_dir}"
./venv/bin/python app.py
""")
            os.chmod(start_script, 0o755)
            
            # 创建systemd服务文件
            service_script = self.install_dir / "install_service.sh"
            with open(service_script, 'w') as f:
                f.write(f"""#!/bin/bash
sudo tee /etc/systemd/system/helmet-detection.service > /dev/null <<EOF
[Unit]
Description=Helmet Detection System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory={self.install_dir}
ExecStart={self.install_dir}/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable helmet-detection.service
echo "服务已安装，使用以下命令管理："
echo "启动服务: sudo systemctl start helmet-detection"
echo "停止服务: sudo systemctl stop helmet-detection"
echo "查看状态: sudo systemctl status helmet-detection"
""")
            os.chmod(service_script, 0o755)
        
        print("✅ 启动脚本创建完成")
    
    def create_config_file(self):
        """创建配置文件"""
        print("⚙️ 创建配置文件...")
        
        config_content = f"""# 头盔实时检测系统配置文件

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False

# AI模型配置
MODEL_PATH = '{self.install_dir}/models'
DEFAULT_MODEL = 'yolov5s.pt'
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# 摄像头配置
DEFAULT_CAMERA_IP = '192.168.1.100'
DEFAULT_CAMERA_PORT = 554
DEFAULT_STREAM_URL = '/stream'

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = '{self.install_dir}/logs/app.log'
"""
        
        config_file = self.install_dir / "config_local.py"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✅ 配置文件创建完成")
    
    def show_completion_info(self):
        """显示安装完成信息"""
        print("\n" + "="*60)
        print("🎉 头盔实时检测系统安装完成！")
        print("="*60)
        print(f"📁 安装目录: {self.install_dir}")
        print(f"🌐 访问地址: http://localhost:5000")
        print("\n📋 使用说明:")
        
        if self.system == 'windows':
            print("1. 双击 start.bat 启动系统")
            print("2. 运行 create_desktop_shortcut.bat 创建桌面快捷方式")
        else:
            print("1. 运行 ./start.sh 启动系统")
            print("2. 运行 ./install_service.sh 安装为系统服务")
        
        print("3. 在浏览器中打开 http://localhost:5000")
        print("4. 在'摄像头管理'中配置摄像头")
        print("5. 在'AI功能配置'中加载检测模型")
        print("6. 在'网络管理'中配置网络参数")
        
        print("\n📚 更多信息:")
        print(f"- 配置文件: {self.install_dir}/config_local.py")
        print(f"- 日志文件: {self.install_dir}/logs/app.log")
        print(f"- 模型目录: {self.install_dir}/models/")
        print("\n" + "="*60)
    
    def install(self):
        """执行完整安装流程"""
        try:
            print("🚀 开始安装头盔实时检测系统...")
            print("="*60)
            
            self.check_requirements()
            self.create_directory()
            self.download_source()
            self.create_virtual_environment()
            self.install_dependencies()
            self.create_startup_scripts()
            self.create_config_file()
            self.show_completion_info()
            
        except Exception as e:
            print(f"\n❌ 安装失败: {e}")
            print("请检查错误信息并重试")
            sys.exit(1)

def main():
    """主函数"""
    print("")
    print("🛡️  头盔实时检测系统 - 一键安装程序")
    print("")
    
    installer = HelmetDetectionInstaller()
    installer.install()

if __name__ == "__main__":
    main()