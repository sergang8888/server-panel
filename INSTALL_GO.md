# Go Web Panel - 一键安装指南

## 🚀 无Python依赖安装

本安装脚本完全独立，无需Python环境，直接安装Go并构建应用。

## ⚠️ 重要提示

**在使用在线安装脚本之前，请先配置正确的GitHub仓库地址：**

1. **本地安装（推荐）**: 直接在项目目录运行 `install_local.bat` 或 `install_local.sh`，无需配置仓库地址
2. **在线安装**: 需要将脚本中的 `your-username/webserver-panel` 替换为实际的GitHub仓库地址

### 配置GitHub仓库地址

编辑安装脚本，将以下行：
```bash
# Linux/macOS (install_go.sh)
GITHUB_REPO="your-username/webserver-panel"

# Windows (install_go.bat)
set GITHUB_REPO=your-username/webserver-panel
```

替换为您的实际仓库地址，例如：
```bash
GITHUB_REPO="myusername/my-webserver-panel"
```

### Windows 系统

#### 方法1: 本地安装（推荐）
```cmd
# 在项目目录下运行
install_local.bat
```

#### 方法2: 下载并运行安装脚本
```cmd
# 注意：需要先修改脚本中的GitHub仓库地址
curl -L https://raw.githubusercontent.com/your-username/webserver-panel/main/install_go.bat -o install_go.bat && install_go.bat
```

#### 方法3: PowerShell 一键安装
```powershell
# 注意：需要先修改脚本中的GitHub仓库地址
iwr -useb https://raw.githubusercontent.com/your-username/webserver-panel/main/install_go.bat | iex
```

#### 方法4: 手动下载
1. 下载 `install_go.bat` 文件
2. 修改其中的GitHub仓库地址
3. 右键以管理员身份运行

### Linux/macOS 系统

#### 方法1: 本地安装（推荐）
```bash
# 在项目目录下运行
chmod +x install_local.sh
./install_local.sh
```

#### 方法2: curl 安装
```bash
# 注意：需要先修改脚本中的GitHub仓库地址
curl -sSL https://raw.githubusercontent.com/your-username/webserver-panel/main/install_go.sh | bash
```

#### 方法3: wget 安装
```bash
# 注意：需要先修改脚本中的GitHub仓库地址
wget -qO- https://raw.githubusercontent.com/your-username/webserver-panel/main/install_go.sh | bash
```

#### 方法4: 手动下载
```bash
wget https://raw.githubusercontent.com/your-username/webserver-panel/main/install_go.sh
# 修改脚本中的GitHub仓库地址
chmod +x install_go.sh
./install_go.sh
```

## 📋 安装流程

### 自动化步骤
1. **系统检测** - 自动检测操作系统和架构
2. **Go环境检查** - 检测是否已安装Go
3. **Go自动安装** - 如未安装，自动下载并安装Go 1.21.0
4. **环境变量配置** - 自动配置PATH、GOPATH、GOROOT
5. **源码下载** - 从GitHub克隆最新源码
6. **依赖下载** - 运行 `go mod tidy`
7. **应用构建** - 编译生成可执行文件
8. **配置文件创建** - 生成默认配置
9. **启动脚本创建** - 生成启动脚本和服务文件
10. **快捷方式创建** - Windows创建桌面快捷方式

### 安装要求
- **磁盘空间**: 至少500MB可用空间
- **网络连接**: 下载Go环境和源码
- **Git**: 用于克隆源码（脚本会检查并提示安装）
- **权限**: Windows需管理员权限，Linux可能需要sudo

## 🎮 使用方法

### Windows
- **桌面快捷方式**: 双击"Go Web Panel"
- **批处理文件**: 运行 `start.bat`
- **直接运行**: `webserver-panel.exe`

### Linux/macOS
- **启动脚本**: `./start.sh`
- **systemd服务**: `sudo systemctl start go-webserver-panel`
- **直接运行**: `./webserver-panel`

### 访问地址
- **本地**: http://localhost:5000
- **网络**: http://您的IP:5000

## ⚙️ 配置说明

安装完成后会生成 `config.json` 配置文件：

```json
{
    "port": 5000,
    "camera_ip": "192.168.1.100",
    "camera_username": "admin",
    "camera_password": "admin123",
    "log_level": "info",
    "max_log_size": 10,
    "max_log_files": 5
}
```

可根据需要修改配置参数。

## 🔧 故障排除

### 常见问题

#### 1. "git不是内部或外部命令"
**解决方案**: 安装Git
- Windows: https://git-scm.com/download/win
- Linux: `sudo apt install git` 或 `sudo yum install git`
- macOS: `brew install git`

#### 2. 权限不足
**解决方案**:
- Windows: 右键以管理员身份运行
- Linux/macOS: 使用 `sudo` 或切换到有权限的用户

#### 3. 网络连接问题
**解决方案**:
- 检查防火墙设置
- 使用代理或VPN
- 手动下载文件后本地安装

#### 4. Go安装失败
**解决方案**:
- 手动从 https://golang.org/dl/ 下载Go
- 解压到指定目录并配置环境变量

#### 5. 构建失败
**解决方案**:
- 检查Go版本是否为1.18+
- 清理模块缓存: `go clean -modcache`
- 重新下载依赖: `go mod download`

## 🌟 优势特点

### 相比Python版本
- ✅ **无Python依赖** - 不需要Python环境
- ✅ **单文件部署** - 编译后只需一个可执行文件
- ✅ **更高性能** - 编译型语言，执行效率更高
- ✅ **更低资源占用** - 内存和CPU使用更少
- ✅ **更快启动** - 启动速度显著提升
- ✅ **更好并发** - Go的goroutine提供优秀的并发处理
- ✅ **跨平台** - 一次编译，多平台运行

### 安装脚本特点
- 🔍 **智能检测** - 自动检测系统环境
- 📦 **完全自动化** - 一键完成所有安装步骤
- 🛡️ **错误处理** - 完善的错误检查和提示
- 🎨 **友好界面** - 彩色输出和进度提示
- 🔧 **灵活配置** - 支持自定义安装路径和配置

## 📞 技术支持

如遇到问题，请：
1. 检查上述故障排除指南
2. 查看安装日志输出
3. 提交Issue到GitHub仓库
4. 联系技术支持

---

**注意**: 首次安装可能需要较长时间下载Go环境，请耐心等待。