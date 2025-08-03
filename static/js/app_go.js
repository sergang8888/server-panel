// Go Web Panel JavaScript
class GoWebPanel {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingTimer = null;
        
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.updateCurrentTime();
        this.loadInitialData();
        
        // 每秒更新时间
        setInterval(() => this.updateCurrentTime(), 1000);
    }

    // WebSocket连接
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket连接已建立');
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                
                // 请求初始数据
                this.sendMessage('get_system_info', {});
                this.sendMessage('get_camera_status', {});
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    console.error('解析WebSocket消息失败:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket连接已关闭');
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.updateConnectionStatus(false);
            this.attemptReconnect();
        }
    }

    // 重连机制
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectInterval);
        } else {
            console.error('WebSocket重连失败，已达到最大重试次数');
        }
    }

    // 发送WebSocket消息
    sendMessage(type, data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = {
                type: type,
                data: data
            };
            this.ws.send(JSON.stringify(message));
        }
    }

    // 处理WebSocket消息
    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'system_info':
                this.updateSystemInfo(message.data);
                break;
            case 'camera_status':
                this.updateCameraStatus(message.data);
                break;
            case 'pong':
                console.log('收到pong响应');
                break;
            default:
                console.log('未知消息类型:', message.type);
        }
    }

    // 更新连接状态
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.innerHTML = '<i class="fas fa-circle"></i> 已连接';
                statusElement.className = 'status-indicator connected';
            } else {
                statusElement.innerHTML = '<i class="fas fa-circle"></i> 已断开';
                statusElement.className = 'status-indicator disconnected';
            }
        }
    }

    // 更新系统信息
    updateSystemInfo(data) {
        // 更新CPU使用率
        const cpuUsage = Math.round(data.cpu_usage);
        document.getElementById('cpu-usage').textContent = `${cpuUsage}%`;
        document.getElementById('cpu-progress').style.width = `${cpuUsage}%`;
        
        // 更新内存使用率
        const memoryUsage = Math.round(data.memory_usage);
        document.getElementById('memory-usage').textContent = `${memoryUsage}%`;
        document.getElementById('memory-progress').style.width = `${memoryUsage}%`;
        
        // 更新磁盘使用率
        const diskUsage = Math.round(data.disk_usage);
        document.getElementById('disk-usage').textContent = `${diskUsage}%`;
        document.getElementById('disk-progress').style.width = `${diskUsage}%`;
        
        // 更新运行时间
        document.getElementById('uptime').textContent = data.uptime;
    }

    // 更新摄像头状态
    updateCameraStatus(data) {
        document.getElementById('camera-status').textContent = '已连接';
        document.getElementById('recording-status').textContent = data.recording ? '录制中' : '未录制';
        document.getElementById('recording-file').textContent = data.filename || '无';
        
        this.isRecording = data.recording;
        this.updateRecordingButton();
        
        if (data.recording) {
            this.showRecordingIndicator();
            this.updateRecordingTimer(data.duration);
        } else {
            this.hideRecordingIndicator();
        }
    }

    // 设置事件监听器
    setupEventListeners() {
        // 页面可见性变化时重新连接
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && (!this.ws || this.ws.readyState !== WebSocket.OPEN)) {
                this.connectWebSocket();
            }
        });
    }

    // 加载初始数据
    loadInitialData() {
        this.loadProcesses();
        this.loadServices();
    }

    // 加载进程列表
    async loadProcesses() {
        try {
            const response = await fetch('/api/processes');
            const result = await response.json();
            
            if (result.success) {
                this.updateProcessesTable(result.data);
            }
        } catch (error) {
            console.error('加载进程列表失败:', error);
        }
    }

    // 更新进程表格
    updateProcessesTable(processes) {
        const tbody = document.getElementById('processes-tbody');
        tbody.innerHTML = '';
        
        // 只显示前20个进程
        const topProcesses = processes.slice(0, 20);
        
        topProcesses.forEach(process => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${process.pid}</td>
                <td>${process.name}</td>
                <td>${process.cpu.toFixed(1)}%</td>
                <td>${process.memory.toFixed(1)}%</td>
                <td><span class="status-badge ${process.status}">${process.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="webPanel.killProcess(${process.pid})">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // 加载服务列表
    async loadServices() {
        try {
            const response = await fetch('/api/services');
            const result = await response.json();
            
            if (result.success) {
                this.updateServicesGrid(result.data);
            }
        } catch (error) {
            console.error('加载服务列表失败:', error);
        }
    }

    // 更新服务网格
    updateServicesGrid(services) {
        const grid = document.getElementById('services-grid');
        grid.innerHTML = '';
        
        services.forEach(service => {
            const card = document.createElement('div');
            card.className = 'service-card';
            card.innerHTML = `
                <div class="service-name">${service.name}</div>
                <div class="service-status ${service.active ? 'active' : 'inactive'}">
                    <i class="fas fa-circle"></i> ${service.status}
                </div>
                <div class="service-actions">
                    <button class="btn btn-sm btn-success" onclick="webPanel.controlService('${service.name}', 'start')">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="webPanel.controlService('${service.name}', 'restart')">
                        <i class="fas fa-redo"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="webPanel.controlService('${service.name}', 'stop')">
                        <i class="fas fa-stop"></i>
                    </button>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    // 更新当前时间
    updateCurrentTime() {
        const now = new Date();
        const timeString = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }

    // 终止进程
    async killProcess(pid) {
        if (!confirm(`确定要终止进程 ${pid} 吗？`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/processes/${pid}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('进程已终止', 'success');
                this.loadProcesses(); // 重新加载进程列表
            } else {
                this.showNotification('终止进程失败: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('终止进程失败: ' + error.message, 'error');
        }
    }

    // 控制服务
    async controlService(serviceName, action) {
        try {
            const response = await fetch(`/api/services/${serviceName}/${action}`, {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`服务 ${serviceName} ${action} 成功`, 'success');
                this.loadServices(); // 重新加载服务列表
            } else {
                this.showNotification(`服务操作失败: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`服务操作失败: ${error.message}`, 'error');
        }
    }

    // 显示通知
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// 摄像头相关功能
function refreshStream() {
    const streamImg = document.getElementById('camera-stream');
    if (streamImg) {
        streamImg.src = '/api/camera/stream?t=' + Date.now();
    }
}

async function takeSnapshot() {
    try {
        const response = await fetch('/api/camera/snapshot', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            webPanel.showNotification('快照已保存: ' + result.filename, 'success');
        } else {
            webPanel.showNotification('快照失败: ' + result.error, 'error');
        }
    } catch (error) {
        webPanel.showNotification('快照失败: ' + error.message, 'error');
    }
}

async function toggleRecording() {
    try {
        const endpoint = webPanel.isRecording ? '/api/camera/stop-recording' : '/api/camera/start-recording';
        const response = await fetch(endpoint, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            webPanel.isRecording = !webPanel.isRecording;
            webPanel.updateRecordingButton();
            
            if (webPanel.isRecording) {
                webPanel.showRecordingIndicator();
                webPanel.startRecordingTimer();
                webPanel.showNotification('开始录制', 'success');
            } else {
                webPanel.hideRecordingIndicator();
                webPanel.stopRecordingTimer();
                webPanel.showNotification('录制已停止', 'success');
            }
        } else {
            webPanel.showNotification('录制操作失败: ' + result.error, 'error');
        }
    } catch (error) {
        webPanel.showNotification('录制操作失败: ' + error.message, 'error');
    }
}

function toggleFullscreen() {
    const streamImg = document.getElementById('camera-stream');
    if (streamImg) {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            streamImg.requestFullscreen();
        }
    }
}

// 扩展GoWebPanel类的录制相关方法
GoWebPanel.prototype.updateRecordingButton = function() {
    const recordBtn = document.getElementById('record-btn');
    if (recordBtn) {
        if (this.isRecording) {
            recordBtn.innerHTML = '<i class="fas fa-stop"></i> 停止录制';
            recordBtn.className = 'btn btn-warning';
        } else {
            recordBtn.innerHTML = '<i class="fas fa-record-vinyl"></i> 开始录制';
            recordBtn.className = 'btn btn-danger';
        }
    }
};

GoWebPanel.prototype.showRecordingIndicator = function() {
    const indicator = document.getElementById('recording-indicator');
    if (indicator) {
        indicator.style.display = 'block';
    }
};

GoWebPanel.prototype.hideRecordingIndicator = function() {
    const indicator = document.getElementById('recording-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
};

GoWebPanel.prototype.startRecordingTimer = function() {
    this.recordingStartTime = Date.now();
    this.recordingTimer = setInterval(() => {
        this.updateRecordingTimer();
    }, 1000);
};

GoWebPanel.prototype.stopRecordingTimer = function() {
    if (this.recordingTimer) {
        clearInterval(this.recordingTimer);
        this.recordingTimer = null;
    }
};

GoWebPanel.prototype.updateRecordingTimer = function(duration) {
    const timeElement = document.getElementById('recording-time');
    if (timeElement) {
        let seconds;
        if (duration !== undefined) {
            seconds = duration;
        } else if (this.recordingStartTime) {
            seconds = Math.floor((Date.now() - this.recordingStartTime) / 1000);
        } else {
            seconds = 0;
        }
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        timeElement.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
};

// 初始化应用
let webPanel;
document.addEventListener('DOMContentLoaded', () => {
    webPanel = new GoWebPanel();
});