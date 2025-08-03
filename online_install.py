#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头盔实时检测系统 - 在线一键安装脚本
支持从GitHub或其他源直接下载并安装

使用方法:
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/your-repo/helmet-detection/main/online_install.py').read())"

或者:
curl -sSL https://raw.githubusercontent.com/your-repo/helmet-detection/main/online_install.py | python
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

class OnlineInstaller:
    def __init__(self):
        # 修复可能的系统名称拼写错误
        detected_system = platform.system().lower().strip()
        if detected_system == 'linlx':  # 修复常见的拼写错误
            self.system = 'linux'
        else:
            self.system = detected_system
        self.python_cmd = self.get_python_command()
        self.install_dir = Path.home() / "helmet-detection-system"
        self.repo_url = "https://github.com/your-repo/helmet-detection-system"
        self.download_url = f"{self.repo_url}/archive/refs/heads/main.zip"
        
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
        """打印安装横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    头盔实时检测系统                          ║
║                   在线一键安装程序                           ║
║                                                              ║
║  🛡️  智能头盔检测  📹 摄像头管理  🌐 网络配置  📊 系统监控   ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
        print(f"🖥️  操作系统: {platform.system()} {platform.release()}")
        print(f"🐍 Python版本: {sys.version.split()[0]}")
        print(f"📁 安装目录: {self.install_dir}")
        print("\n" + "="*60)
    
    def check_internet_connection(self):
        """检查网络连接"""
        print("🌐 检查网络连接...")
        try:
            urllib.request.urlopen('https://www.github.com', timeout=10)
            print("✅ 网络连接正常")
        except Exception as e:
            print(f"❌ 网络连接失败: {e}")
            print("请检查网络连接后重试")
            sys.exit(1)
    
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
            print("⚠️  pip未安装，正在尝试安装...")
            self.install_pip()
        
        # 检查磁盘空间（至少需要1GB）
        if self.system == 'windows':
            import shutil
            free_space = shutil.disk_usage('.').free
        else:
            statvfs = os.statvfs('.')
            free_space = statvfs.f_frsize * statvfs.f_bavail
        
        free_gb = free_space / (1024**3)
        if free_gb < 1:
            print(f"⚠️  磁盘空间不足: {free_gb:.1f}GB，建议至少1GB")
        else:
            print(f"✅ 磁盘空间: {free_gb:.1f}GB")
    
    def install_pip(self):
        """安装pip"""
        try:
            if self.system == 'windows':
                subprocess.run([self.python_cmd, '-m', 'ensurepip', '--upgrade'], check=True)
            else:
                # Linux系统
                if shutil.which('apt-get'):
                    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'python3-pip'], check=True)
                elif shutil.which('yum'):
                    subprocess.run(['sudo', 'yum', 'install', '-y', 'python3-pip'], check=True)
                elif shutil.which('dnf'):
                    subprocess.run(['sudo', 'dnf', 'install', '-y', 'python3-pip'], check=True)
            print("✅ pip安装成功")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"pip安装失败: {e}")
    
    def download_source_code(self):
        """下载源代码"""
        print("📥 下载源代码...")
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "source.zip"
            
            try:
                # 下载ZIP文件
                print(f"正在从 {self.download_url} 下载...")
                urllib.request.urlretrieve(self.download_url, zip_path)
                
                # 解压文件
                print("正在解压文件...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 查找解压后的目录
                extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
                if not extracted_dirs:
                    raise RuntimeError("解压后未找到源代码目录")
                
                source_dir = extracted_dirs[0]
                
                # 创建安装目录
                self.install_dir.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                for item in source_dir.iterdir():
                    dest = self.install_dir / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    else:
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                
                print("✅ 源代码下载完成")
                
            except Exception as e:
                print(f"❌ 下载失败: {e}")
                print("正在尝试备用下载方式...")
                self.download_fallback()
    
    def download_fallback(self):
        """备用下载方式"""
        print("使用git克隆仓库...")
        try:
            if shutil.which('git'):
                subprocess.run(['git', 'clone', self.repo_url, str(self.install_dir)], check=True)
                print("✅ 使用git下载成功")
            else:
                raise RuntimeError("git未安装且直接下载失败")
        except subprocess.CalledProcessError:
            print("❌ git克隆失败")
            print("请手动下载源代码或安装git后重试")
            sys.exit(1)
    
    def setup_environment(self):
        """设置环境"""
        print("🐍 设置Python环境...")
        
        # 切换到安装目录
        os.chdir(self.install_dir)
        
        # 创建虚拟环境
        venv_path = self.install_dir / "venv"
        if not venv_path.exists():
            subprocess.run([self.python_cmd, '-m', 'venv', 'venv'], check=True)
            print("✅ 虚拟环境创建成功")
        else:
            print("✅ 虚拟环境已存在")
        
        # 获取虚拟环境中的Python路径
        if self.system == 'windows':
            venv_python = venv_path / "Scripts" / "python.exe"
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            venv_python = venv_path / "bin" / "python"
            venv_pip = venv_path / "bin" / "pip"
        
        # 升级pip
        subprocess.run([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        
        # 安装依赖
        requirements_file = self.install_dir / "requirements.txt"
        if requirements_file.exists():
            print("📦 安装依赖包...")
            subprocess.run([str(venv_pip), 'install', '-r', 'requirements.txt'], check=True)
            print("✅ 依赖包安装完成")
        else:
            print("⚠️  requirements.txt不存在，跳过依赖安装")
    
    def create_config_file(self):
        """创建配置文件"""
        print("📝 创建配置文件...")
        
        config_content = f'''# 头盔实时检测系统 - 用户配置文件

# 服务器配置
HOST = '0.0.0.0'
PORT = {self.config['SERVER_PORT']}
DEBUG = False

# 管理员账号配置
ADMIN_USERNAME = '{self.config['ADMIN_USER']}'
ADMIN_PASSWORD = '{self.config['ADMIN_PASS']}'

# 摄像头默认配置
DEFAULT_CAMERA_IP = '{self.config['CAMERA_IP']}'
DEFAULT_CAMERA_PORT = {self.config['CAMERA_PORT']}
DEFAULT_CAMERA_USERNAME = '{self.config['CAMERA_USER']}'
DEFAULT_CAMERA_PASSWORD = '{self.config['CAMERA_PASS']}'
DEFAULT_STREAM_URL = '/stream'

# AI模型配置
MODEL_PATH = 'models'
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'
'''
        
        config_file = self.install_dir / "config_user.py"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✅ 配置文件创建完成")

    def create_startup_files(self):
        """创建启动文件"""
        print("📝 创建启动文件...")
        
        if self.system == 'windows':
            # Windows启动脚本
            start_script = self.install_dir / "启动系统.bat"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(f"""@echo off
chcp 65001 >nul
title 头盔实时检测系统 - 端口:{self.config['SERVER_PORT']}
cd /d "{self.install_dir}"
echo ==========================================
echo    头盔实时检测系统
echo ==========================================
echo 🚀 正在启动系统...
echo 服务器端口: {self.config['SERVER_PORT']}
echo 管理员账号: {self.config['ADMIN_USER']}
echo 访问地址: http://localhost:{self.config['SERVER_PORT']}
echo ==========================================
echo.
call venv\\Scripts\\activate.bat
python app.py
echo.
echo 系统已停止运行
pause
""")
            
            # 创建配置修改脚本
            modify_script = self.install_dir / "修改配置.bat"
            with open(modify_script, 'w', encoding='utf-8') as f:
                f.write(f"""@echo off
chcp 65001 >nul
echo ==========================================
echo       修改系统配置
echo ==========================================
echo 当前配置:
echo 服务器端口: {self.config['SERVER_PORT']}
echo 管理员账号: {self.config['ADMIN_USER']}
echo 摄像头IP: {self.config['CAMERA_IP']}
echo ==========================================
echo 如需修改配置，请编辑 config_user.py 文件
echo 修改后重新启动系统生效
pause
""")
            
            # 创建桌面快捷方式脚本
            shortcut_script = self.install_dir / "创建桌面快捷方式.bat"
            with open(shortcut_script, 'w', encoding='utf-8') as f:
                f.write(f"""@echo off
set SCRIPT="%USERPROFILE%\\Desktop\\头盔检测系统.lnk"
set TARGET="{start_script}"
set PWS=powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile

%PWS% -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SCRIPT%'); $S.TargetPath = '%TARGET%'; $S.IconLocation = '%TARGET%'; $S.Save()"
echo ✅ 桌面快捷方式已创建
echo 您可以在桌面找到"头盔检测系统"快捷方式
pause
""")
        
        else:
            # Linux启动脚本
            start_script = self.install_dir / "start.sh"
            with open(start_script, 'w') as f:
                f.write(f"""#!/bin/bash
cd "{self.install_dir}"
echo "==========================================="
echo "    头盔实时检测系统"
echo "==========================================="
echo "🚀 正在启动系统..."
echo "服务器端口: {self.config['SERVER_PORT']}"
echo "管理员账号: {self.config['ADMIN_USER']}"
echo "访问地址: http://localhost:{self.config['SERVER_PORT']}"
echo "==========================================="
echo
source venv/bin/activate
python app.py
echo
echo "系统已停止运行"
read -p "按回车键退出..."
""")
            os.chmod(start_script, 0o755)
            
            # 创建配置修改脚本
            modify_script = self.install_dir / "modify_config.sh"
            with open(modify_script, 'w') as f:
                f.write(f"""#!/bin/bash
echo "==========================================="
echo "       修改系统配置"
echo "==========================================="
echo "当前配置:"
echo "服务器端口: {self.config['SERVER_PORT']}"
echo "管理员账号: {self.config['ADMIN_USER']}"
echo "摄像头IP: {self.config['CAMERA_IP']}"
echo "==========================================="
echo "如需修改配置，请编辑 config_user.py 文件"
echo "修改后重新启动系统生效"
read -p "按回车键退出..."
""")
            os.chmod(modify_script, 0o755)
        
        print("✅ 启动文件创建完成")
    
    def create_directories(self):
        """创建必要的目录"""
        print("📁 创建目录结构...")
        
        directories = ['models', 'logs', 'uploads', 'temp']
        for dir_name in directories:
            dir_path = self.install_dir / dir_name
            dir_path.mkdir(exist_ok=True)
        
        print("✅ 目录结构创建完成")
    
    def test_installation(self):
        """测试安装"""
        print("🧪 测试安装...")
        
        try:
            # 检查关键文件
            required_files = ['app.py', 'config.py', 'templates/index.html']
            for file_path in required_files:
                if not (self.install_dir / file_path).exists():
                    raise FileNotFoundError(f"缺少关键文件: {file_path}")
            
            # 测试Python导入
            if self.system == 'windows':
                venv_python = self.install_dir / "venv" / "Scripts" / "python.exe"
            else:
                venv_python = self.install_dir / "venv" / "bin" / "python"
            
            test_cmd = [str(venv_python), '-c', 'import flask; import psutil; print("导入测试成功")']
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Python模块导入失败: {result.stderr}")
            
            print("✅ 安装测试通过")
            
        except Exception as e:
            print(f"⚠️  安装测试失败: {e}")
            print("系统可能无法正常运行，请检查错误信息")
    
    def show_completion_message(self):
        """显示安装完成信息"""
        completion_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 安装完成！                             ║
╚══════════════════════════════════════════════════════════════╝

📁 安装目录: {self.install_dir}
🌐 访问地址: http://localhost:{self.config['SERVER_PORT']}
👤 管理员账号: {self.config['ADMIN_USER']}
🔑 管理员密码: {self.config['ADMIN_PASS']}

🚀 启动方式:
"""
        
        if self.system == 'windows':
            completion_msg += f"""
   方式1: 双击 "启动系统.bat"
   方式2: 运行 "创建桌面快捷方式.bat" 后使用桌面快捷方式
   方式3: 命令行运行:
          cd "{self.install_dir}"
          venv\\Scripts\\activate
          python app.py

📝 配置管理:
   - 双击 "修改配置.bat" 查看当前配置
   - 编辑 config_user.py 文件修改配置
"""
        else:
            completion_msg += f"""
   方式1: 运行 ./start.sh
   方式2: 命令行运行:
          cd "{self.install_dir}"
          source venv/bin/activate
          python app.py

📝 配置管理:
   - 运行 ./modify_config.sh 查看当前配置
   - 编辑 config_user.py 文件修改配置
"""
        
        completion_msg += """

📋 系统功能:
   🛡️  AI头盔检测 - 实时检测头盔佩戴情况
   📹 摄像头管理 - 配置和管理IP摄像头
   🌐 网络管理   - 配置网络参数和连接
   📊 系统监控   - 实时监控系统资源

📚 使用说明:
   1. 启动系统后在浏览器打开 http://localhost:{self.config['SERVER_PORT']}
   2. 在"摄像头管理"中配置摄像头
   3. 在"AI功能配置"中加载检测模型
   4. 在"网络管理"中配置网络参数

💡 提示:
   - 首次使用需要下载AI模型文件
   - 建议使用Chrome或Edge浏览器
   - 如遇问题请查看 logs/app.log 日志文件

🆘 技术支持:
   📧 邮箱: support@helmet-detection.com
   🌐 官网: https://helmet-detection.com
   📖 文档: https://docs.helmet-detection.com

感谢使用头盔实时检测系统！
"""
        
        print(completion_msg)
        
        # 询问是否立即启动
        try:
            response = input("\n是否现在启动系统？(y/n): ").lower().strip()
            if response in ['y', 'yes', '是', '启动']:
                self.start_system()
        except KeyboardInterrupt:
            print("\n安装完成，稍后可手动启动系统")
    
    def start_system(self):
        """启动系统"""
        print("\n🚀 正在启动系统...")
        try:
            os.chdir(self.install_dir)
            if self.system == 'windows':
                subprocess.Popen(['cmd', '/c', 'start', '启动系统.bat'], shell=True)
            else:
                subprocess.Popen(['./start.sh'])
            print(f"✅ 系统启动中，请稍后在浏览器中访问 http://localhost:{self.config['SERVER_PORT']}")
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            print("请手动运行启动脚本")
    
    def install(self):
        """执行完整安装流程"""
        try:
            self.print_banner()
            self.check_internet_connection()
            self.check_requirements()
            self.download_source_code()
            self.setup_environment()
            self.create_config_file()
            self.create_startup_files()
            self.create_directories()
            self.test_installation()
            self.show_completion_message()
            
        except KeyboardInterrupt:
            print("\n\n❌ 安装被用户中断")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ 安装失败: {e}")
            print("\n请检查错误信息并重试，或访问官网获取技术支持")
            sys.exit(1)

def get_user_config():
    """获取用户配置"""
    print("\n" + "="*50)
    print("           系统配置")
    print("="*50)
    print("\n请输入系统配置信息（直接回车使用默认值）:\n")
    
    config = {}
    
    # 输入服务器端口
    port = input("请输入服务器端口 [默认: 5000]: ").strip()
    config['SERVER_PORT'] = port if port else '5000'
    print(f"服务器端口: {config['SERVER_PORT']}\n")
    
    # 输入管理员账号
    admin_user = input("请输入管理员账号 [默认: admin]: ").strip()
    config['ADMIN_USER'] = admin_user if admin_user else 'admin'
    print(f"管理员账号: {config['ADMIN_USER']}\n")
    
    # 输入管理员密码
    admin_pass = input("请输入管理员密码 [默认: admin123]: ").strip()
    config['ADMIN_PASS'] = admin_pass if admin_pass else 'admin123'
    print(f"管理员密码: {config['ADMIN_PASS']}\n")
    
    # 设置默认摄像头配置
    config['CAMERA_IP'] = '192.168.1.100'
    config['CAMERA_PORT'] = '554'
    config['CAMERA_USER'] = 'admin'
    config['CAMERA_PASS'] = '123456'
    
    # 配置确认
    print("="*50)
    print("           配置确认")
    print("="*50)
    print(f"服务器端口: {config['SERVER_PORT']}")
    print(f"管理员账号: {config['ADMIN_USER']}")
    print(f"管理员密码: {config['ADMIN_PASS']}")
    print("="*50)
    print()
    
    confirm = input("确认以上配置？(y/n) [默认: y]: ").strip().lower()
    if confirm and confirm not in ['y', 'yes']:
        print("安装已取消")
        return None
    
    print("\n🚀 开始安装...\n")
    return config

def main():
    """主函数"""
    # 获取用户配置
    config = get_user_config()
    if config is None:
        return
    
    installer = OnlineInstaller()
    installer.config = config
    
    # 执行安装流程
    try:
        print("📦 检查系统要求...")
        installer.check_requirements()
        
        print("🌐 检查网络连接...")
        installer.check_network()
        
        print("📥 下载源代码...")
        installer.download_source_code()
        
        print("🐍 设置Python环境...")
        installer.setup_environment()
        
        print("📝 创建配置文件...")
        installer.create_config_file()
        
        print("🚀 创建启动文件...")
        installer.create_startup_files()
        
        print("📁 创建目录结构...")
        installer.create_directories()
        
        print("🧪 测试安装...")
        installer.test_installation()
        
        print("🎉 显示完成信息...")
        installer.show_completion_message()
        
        print("\n✅ 安装完成！")
        
    except Exception as e:
        print(f"\n❌ 安装失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()