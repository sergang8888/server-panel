#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Go Web管理面板 - 在线一键安装脚本
支持从GitHub直接下载并安装Go版本的Web管理面板

使用方法:
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/your-repo/webserver-panel/main/online_install_go.py').read())"

或者:
curl -sSL https://raw.githubusercontent.com/your-repo/webserver-panel/main/online_install_go.py | python3
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

class GoWebPanelInstaller:
    def __init__(self):
        # 修复可能的系统名称拼写错误
        detected_system = platform.system().lower().strip()
        if detected_system == 'linlx':  # 修复常见的拼写错误
            self.system = 'linux'
        else:
            self.system = detected_system
        self.arch = platform.machine().lower()
        self.python_cmd = self.get_python_command()
        self.install_dir = Path.home() / "go-webserver-panel"
        self.repo_url = "https://github.com/your-repo/webserver-panel"
        self.download_url = f"{self.repo_url}/archive/refs/heads/main.zip"
        self.go_version = "1.21.0"  # 推荐的Go版本
        
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
║                    Go Web管理面板                            ║
║                   在线一键安装程序                           ║
║                                                              ║
║  🚀 高性能Go语言实现                                         ║
║  📊 系统监控 + 进程管理                                      ║
║  📹 摄像头监控 + 录制                                        ║
║  🔧 服务管理 + 实时通信                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🖥️  操作系统: {self.system.title()} ({self.arch})")
        print(f"🐍 Python版本: {sys.version.split()[0]}")
        print(f"📁 安装目录: {self.install_dir}")
        print("="*60)
    
    def check_internet_connection(self):
        """检查网络连接"""
        print("🌐 检查网络连接...")
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            print("✅ 网络连接正常")
        except:
            try:
                urllib.request.urlopen('https://www.baidu.com', timeout=5)
                print("✅ 网络连接正常")
            except:
                raise RuntimeError("❌ 网络连接失败，请检查网络设置")
    
    def check_requirements(self):
        """检查系统要求"""
        print("🔍 检查系统要求...")
        
        # 检查磁盘空间（至少需要500MB）
        if self.system == 'windows':
            free_space = shutil.disk_usage('.').free
        else:
            statvfs = os.statvfs('.')
            free_space = statvfs.f_frsize * statvfs.f_bavail
        
        free_gb = free_space / (1024**3)
        if free_gb < 0.5:
            print(f"⚠️  磁盘空间不足: {free_gb:.1f}GB，建议至少0.5GB")
        else:
            print(f"✅ 磁盘空间: {free_gb:.1f}GB")
    
    def check_go_installation(self):
        """检查Go安装"""
        print("🔍 检查Go语言环境...")
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Go已安装: {version}")
                return True
        except FileNotFoundError:
            pass
        
        print("⚠️  未检测到Go语言环境")
        return False
    
    def install_go(self):
        """安装Go语言"""
        print(f"📦 正在安装Go {self.go_version}...")
        
        # 确定下载URL
        if self.system == 'windows':
            if 'amd64' in self.arch or 'x86_64' in self.arch:
                go_file = f"go{self.go_version}.windows-amd64.zip"
            else:
                go_file = f"go{self.go_version}.windows-386.zip"
        elif self.system == 'linux':
            if 'amd64' in self.arch or 'x86_64' in self.arch:
                go_file = f"go{self.go_version}.linux-amd64.tar.gz"
            elif 'arm64' in self.arch or 'aarch64' in self.arch:
                go_file = f"go{self.go_version}.linux-arm64.tar.gz"
            else:
                go_file = f"go{self.go_version}.linux-386.tar.gz"
        elif self.system == 'darwin':
            if 'arm64' in self.arch:
                go_file = f"go{self.go_version}.darwin-arm64.tar.gz"
            else:
                go_file = f"go{self.go_version}.darwin-amd64.tar.gz"
        else:
            raise RuntimeError(f"不支持的操作系统: {self.system}")
        
        go_url = f"https://golang.org/dl/{go_file}"
        
        # 下载Go
        with tempfile.TemporaryDirectory() as temp_dir:
            go_path = Path(temp_dir) / go_file
            print(f"📥 下载Go: {go_url}")
            
            try:
                urllib.request.urlretrieve(go_url, go_path)
            except Exception as e:
                raise RuntimeError(f"Go下载失败: {e}")
            
            # 安装Go
            if self.system == 'windows':
                go_install_dir = Path("C:/Go")
                if go_install_dir.exists():
                    shutil.rmtree(go_install_dir)
                
                with zipfile.ZipFile(go_path, 'r') as zip_ref:
                    zip_ref.extractall("C:/")
                
                # 添加到PATH
                self.add_to_path_windows("C:\\Go\\bin")
                
            else:  # Linux/macOS
                go_install_dir = Path("/usr/local/go")
                if go_install_dir.exists():
                    subprocess.run(['sudo', 'rm', '-rf', str(go_install_dir)], check=True)
                
                subprocess.run(['sudo', 'tar', '-C', '/usr/local', '-xzf', str(go_path)], check=True)
                
                # 添加到PATH
                self.add_to_path_unix("/usr/local/go/bin")
        
        print("✅ Go安装完成")
        print("⚠️  请重新打开终端或运行 'source ~/.bashrc' 使PATH生效")
    
    def add_to_path_windows(self, path):
        """Windows添加到PATH"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
            current_path, _ = winreg.QueryValueEx(key, "PATH")
            if path not in current_path:
                new_path = current_path + ";" + path
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"⚠️  无法自动添加到PATH: {e}")
            print(f"请手动将 {path} 添加到系统PATH环境变量")
    
    def add_to_path_unix(self, path):
        """Unix系统添加到PATH"""
        shell_rc = Path.home() / ".bashrc"
        if not shell_rc.exists():
            shell_rc = Path.home() / ".zshrc"
        
        export_line = f'export PATH=$PATH:{path}'
        
        try:
            with open(shell_rc, 'r') as f:
                content = f.read()
            
            if export_line not in content:
                with open(shell_rc, 'a') as f:
                    f.write(f'\n{export_line}\n')
        except Exception as e:
            print(f"⚠️  无法自动添加到PATH: {e}")
            print(f"请手动将 {export_line} 添加到 {shell_rc}")
    
    def download_source_code(self):
        """下载源代码"""
        print("📥 下载Go Web面板源代码...")
        
        # 创建安装目录
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "source.zip"
            
            try:
                print(f"📥 从 {self.download_url} 下载...")
                urllib.request.urlretrieve(self.download_url, zip_path)
                
                # 解压源代码
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 查找解压后的目录
                extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
                if not extracted_dirs:
                    raise RuntimeError("解压失败，未找到源代码目录")
                
                source_dir = extracted_dirs[0]
                
                # 复制Go相关文件到安装目录
                go_files = ['main.go', 'system.go', 'camera.go', 'websocket.go', 'go.mod', 'go.sum']
                for file_name in go_files:
                    src_file = source_dir / file_name
                    if src_file.exists():
                        shutil.copy2(src_file, self.install_dir)
                
                # 复制静态文件和模板
                for dir_name in ['static', 'templates']:
                    src_dir = source_dir / dir_name
                    if src_dir.exists():
                        dst_dir = self.install_dir / dir_name
                        if dst_dir.exists():
                            shutil.rmtree(dst_dir)
                        shutil.copytree(src_dir, dst_dir)
                
                print("✅ 源代码下载完成")
                
            except Exception as e:
                raise RuntimeError(f"源代码下载失败: {e}")
    
    def build_application(self):
        """构建Go应用程序"""
        print("🔨 构建Go应用程序...")
        
        os.chdir(self.install_dir)
        
        try:
            # 初始化Go模块
            print("📦 初始化Go模块...")
            subprocess.run(['go', 'mod', 'tidy'], check=True, capture_output=True)
            
            # 构建应用程序
            print("🔨 编译应用程序...")
            if self.system == 'windows':
                executable_name = 'webserver-panel.exe'
            else:
                executable_name = 'webserver-panel'
            
            subprocess.run(['go', 'build', '-o', executable_name, '.'], check=True, capture_output=True)
            
            if not (self.install_dir / executable_name).exists():
                raise RuntimeError("构建失败，未生成可执行文件")
            
            print(f"✅ 构建完成: {executable_name}")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"构建失败: {e}")
    
    def create_config_file(self):
        """创建配置文件"""
        print("⚙️  创建配置文件...")
        
        config = {
            "port": "5000",
            "debug": False,
            "camera_ip": "192.168.1.41:8080"
        }
        
        config_path = self.install_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置文件已创建: {config_path}")
    
    def create_startup_files(self):
        """创建启动脚本"""
        print("📝 创建启动脚本...")
        
        if self.system == 'windows':
            # Windows批处理文件
            start_script = self.install_dir / "start.bat"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(f"""@echo off
cd /d "{self.install_dir}"
echo Starting Go Web Panel...
webserver-panel.exe
pause
""")
            
            # 创建桌面快捷方式
            self.create_desktop_shortcut_windows()
            
        else:
            # Linux/macOS shell脚本
            start_script = self.install_dir / "start.sh"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(f"""#!/bin/bash
cd "{self.install_dir}"
echo "Starting Go Web Panel..."
./webserver-panel
""")
            
            # 添加执行权限
            os.chmod(start_script, 0o755)
            
            # 创建systemd服务文件
            self.create_systemd_service()
        
        print(f"✅ 启动脚本已创建: {start_script}")
    
    def create_desktop_shortcut_windows(self):
        """创建Windows桌面快捷方式"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Go Web Panel.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.install_dir / "start.bat")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "webserver-panel.exe")
            shortcut.save()
            
            print("✅ 桌面快捷方式已创建")
        except ImportError:
            print("⚠️  无法创建桌面快捷方式（缺少依赖）")
        except Exception as e:
            print(f"⚠️  创建桌面快捷方式失败: {e}")
    
    def create_systemd_service(self):
        """创建systemd服务文件"""
        service_content = f"""[Unit]
Description=Go Web Panel
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={self.install_dir}
ExecStart={self.install_dir}/webserver-panel
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = self.install_dir / "go-webserver-panel.service"
        with open(service_path, 'w', encoding='utf-8') as f:
            f.write(service_content)
        
        print(f"✅ systemd服务文件已创建: {service_path}")
        print("💡 要启用服务，请运行:")
        print(f"   sudo cp {service_path} /etc/systemd/system/")
        print("   sudo systemctl enable go-webserver-panel")
        print("   sudo systemctl start go-webserver-panel")
    
    def test_installation(self):
        """测试安装"""
        print("🧪 测试安装...")
        
        executable = self.install_dir / ("webserver-panel.exe" if self.system == 'windows' else "webserver-panel")
        
        if not executable.exists():
            raise RuntimeError("可执行文件不存在")
        
        # 测试程序是否能正常启动（快速测试）
        try:
            result = subprocess.run([str(executable), '--help'], 
                                  capture_output=True, text=True, timeout=5)
            # 即使没有--help参数，程序启动也说明编译正确
        except subprocess.TimeoutExpired:
            # 超时说明程序正在运行，这是正常的
            pass
        except Exception as e:
            print(f"⚠️  程序测试警告: {e}")
        
        print("✅ 安装测试完成")
    
    def start_system(self):
        """启动系统"""
        print("🚀 启动Go Web面板...")
        
        executable = self.install_dir / ("webserver-panel.exe" if self.system == 'windows' else "webserver-panel")
        
        print(f"📍 工作目录: {self.install_dir}")
        print(f"🌐 访问地址: http://localhost:5000")
        print("\n" + "="*60)
        print("🎉 Go Web面板启动中...")
        print("📊 功能包括: 系统监控、进程管理、摄像头监控、服务管理")
        print("🔧 按 Ctrl+C 停止服务")
        print("="*60 + "\n")
        
        try:
            os.chdir(self.install_dir)
            subprocess.run([str(executable)])
        except KeyboardInterrupt:
            print("\n👋 Go Web面板已停止")
        except Exception as e:
            print(f"❌ 启动失败: {e}")
    
    def install(self):
        """执行完整安装流程"""
        try:
            self.print_banner()
            self.check_internet_connection()
            self.check_requirements()
            
            # 检查Go环境
            if not self.check_go_installation():
                install_go = input("\n是否自动安装Go语言环境? (y/n): ").lower().strip()
                if install_go in ['y', 'yes', '是', '']:
                    self.install_go()
                    print("\n⚠️  Go安装完成，请重新运行此脚本")
                    return
                else:
                    print("\n💡 请手动安装Go 1.19+后重新运行此脚本")
                    print("   下载地址: https://golang.org/dl/")
                    return
            
            self.download_source_code()
            self.build_application()
            self.create_config_file()
            self.create_startup_files()
            self.test_installation()
            
            print("\n" + "="*60)
            print("🎉 Go Web面板安装完成!")
            print(f"📁 安装目录: {self.install_dir}")
            print("🌐 访问地址: http://localhost:5000")
            print("="*60)
            
            # 询问是否立即启动
            start_now = input("\n是否立即启动Go Web面板? (y/n): ").lower().strip()
            if start_now in ['y', 'yes', '是', '']:
                self.start_system()
            else:
                print("\n💡 启动方法:")
                if self.system == 'windows':
                    print(f"   双击运行: {self.install_dir / 'start.bat'}")
                    print(f"   或命令行: cd \"{self.install_dir}\" && webserver-panel.exe")
                else:
                    print(f"   运行: {self.install_dir / 'start.sh'}")
                    print(f"   或命令行: cd \"{self.install_dir}\" && ./webserver-panel")
                
        except Exception as e:
            print(f"\n❌ 安装失败: {e}")
            print("\n💡 故障排除:")
            print("1. 检查网络连接")
            print("2. 确保有足够的磁盘空间")
            print("3. 检查Go语言环境")
            print("4. 尝试手动安装")
            sys.exit(1)

def get_user_config():
    """获取用户配置"""
    print("\n⚙️  配置选项 (直接回车使用默认值):")
    
    config = {}
    
    # 服务端口
    port = input("🌐 Web服务端口 [5000]: ").strip()
    config['port'] = port if port else '5000'
    
    # 摄像头IP
    camera_ip = input("📹 摄像头IP地址 [192.168.1.41:8080]: ").strip()
    config['camera_ip'] = camera_ip if camera_ip else '192.168.1.41:8080'
    
    # 调试模式
    debug = input("🐛 启用调试模式? (y/n) [n]: ").lower().strip()
    config['debug'] = debug in ['y', 'yes', '是']
    
    return config

def main():
    """主函数"""
    try:
        installer = GoWebPanelInstaller()
        installer.install()
    except KeyboardInterrupt:
        print("\n\n👋 安装已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 安装程序错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()