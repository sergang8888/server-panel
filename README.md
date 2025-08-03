# Ubuntu 22 Web管理面板

一个基于Flask的现代化Web系统管理界面，专为Ubuntu 22.04 LTS设计。提供直观的系统监控、进程管理、服务控制等功能。

## 🚀 一键安装

### 在线一键安装（推荐）

**Windows系统：**
```cmd
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/your-repo/helmet-detection/main/online_install.py').read())"
```

**Linux系统：**
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/helmet-detection/main/online_install.py | python3
```

或者使用wget：
```bash
wget -qO- https://raw.githubusercontent.com/your-repo/helmet-detection/main/online_install.py | python3
```

### 本地一键安装

如果您已经下载了源代码：

**Windows系统：**
```cmd
# 双击运行或命令行执行
quick_install.bat
```

**Linux系统：**
```bash
chmod +x quick_install.sh
./quick_install.sh
```

### 安装特性

一键安装脚本将自动完成以下操作：
- ✅ 检查系统环境（Python 3.8+、pip、磁盘空间）
- ✅ 自动下载最新源代码
- ✅ 创建独立的Python虚拟环境
- ✅ 安装所有必需依赖包
- ✅ 创建启动脚本和快捷方式
- ✅ 配置目录结构和权限
- ✅ 测试安装完整性
- ✅ 可选择立即启动系统

## 功能特性

### 🖥️ 系统监控
- 实时CPU、内存、磁盘使用率监控
- 系统负载和运行时间显示
- 网络流量统计
- 交互式图表展示历史数据

### 📊 仪表板
- 美观的现代化界面设计
- 响应式布局，支持移动设备
- 实时数据更新（WebSocket）
- 直观的指标卡片和图表

### 🔧 进程管理
- 查看系统运行进程列表
- 显示进程CPU和内存占用
- 支持终止进程操作
- 实时进程状态更新

### ⚙️ 服务管理
- 常用系统服务状态监控
- 支持启动、停止、重启服务
- 服务状态可视化显示
- 包含nginx、apache2、mysql等常用服务

### 📈 系统信息
- 详细的硬件信息展示
- 网络接口统计
- 系统负载分析

## 系统要求

- **操作系统**: Ubuntu 22.04 LTS
- **Python**: 3.8+
- **权限**: 建议使用sudo权限运行以获得完整功能
- **浏览器**: 现代浏览器（Chrome、Firefox、Safari、Edge）

## 快速开始

### 1. 下载项目
```bash
git clone <repository-url>
cd Webserver-panel
```

### 2. 安装依赖
```bash
# 更新系统包
sudo apt update

# 安装Python3和pip（如果未安装）
sudo apt install python3 python3-pip python3-venv

# 给启动脚本执行权限
chmod +x start.sh
```

### 3. 启动服务
```bash
# 使用启动脚本（推荐）
sudo ./start.sh

# 或手动启动
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo python3 app.py
```

### 4. 访问界面
打开浏览器访问: `http://localhost:5000`

## 详细安装说明

### 手动安装步骤

1. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置权限（可选）**
   ```bash
   # 为了使用systemctl命令，需要sudo权限
   # 或者配置sudoers文件允许无密码执行特定命令
   sudo visudo
   # 添加行: username ALL=(ALL) NOPASSWD: /bin/systemctl
   ```

4. **启动应用**
   ```bash
   sudo python3 app.py
   ```

### 生产环境部署

使用Gunicorn部署到生产环境：

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

使用Nginx反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 使用说明

### 界面导航

- **仪表板**: 系统概览和实时监控图表
- **进程管理**: 查看和管理系统进程
- **服务管理**: 控制系统服务状态
- **系统信息**: 查看详细的系统和网络信息

### 功能说明

#### 仪表板
- 顶部显示CPU、内存、磁盘使用率和系统运行时间
- 下方展示CPU和内存使用率的实时趋势图
- 数据每2秒自动更新

#### 进程管理
- 显示前50个CPU占用最高的进程
- 点击"终止"按钮可以结束进程（需要确认）
- 支持实时刷新进程列表

#### 服务管理
- 显示常用系统服务的状态
- 支持启动、停止、重启操作
- 绿色表示服务运行中，红色表示服务已停止

## 安全注意事项

1. **权限控制**: 本应用需要较高的系统权限，请确保在安全的环境中运行
2. **网络访问**: 默认绑定到所有网络接口，生产环境建议配置防火墙
3. **认证**: 当前版本未包含用户认证，建议在反向代理层添加认证
4. **HTTPS**: 生产环境建议使用HTTPS加密传输

## 故障排除

### 常见问题

1. **权限错误**
   ```
   解决方案: 使用sudo运行应用
   sudo python3 app.py
   ```

2. **端口被占用**
   ```
   错误: Address already in use
   解决方案: 更改端口或停止占用进程
   sudo netstat -tlnp | grep :5000
   ```

3. **依赖安装失败**
   ```
   解决方案: 更新pip并重新安装
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **服务操作失败**
   ```
   原因: 缺少sudo权限
   解决方案: 确保以sudo权限运行应用
   ```

### 日志查看

应用运行时会在控制台输出日志信息，包括：
- 客户端连接状态
- API请求记录
- 错误信息

## 技术栈

- **后端**: Python Flask + Flask-SocketIO
- **前端**: Bootstrap 5 + Chart.js + Socket.IO
- **系统监控**: psutil
- **实时通信**: WebSocket

## 项目结构

```
Webserver-panel/
├── app.py              # 主应用文件
├── requirements.txt    # Python依赖
├── start.sh           # 启动脚本
├── README.md          # 说明文档
├── templates/         # HTML模板
│   └── index.html
└── static/           # 静态文件
    └── js/
        └── app.js    # 前端JavaScript
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 基础系统监控功能
- 进程和服务管理
- 响应式Web界面
- 实时数据更新