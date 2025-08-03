// WebSocket连接
const socket = io();

// 图表实例
let cpuChart, memoryChart;

// 数据存储
let cpuData = [];
let memoryData = [];
let timeLabels = [];

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadInitialData();
    setupEventListeners();
});

// WebSocket事件处理
socket.on('connect', function() {
    console.log('Connected to server');
    document.getElementById('connection-status').textContent = '已连接';
    document.getElementById('connection-status').previousElementSibling.className = 'fas fa-circle text-success me-1';
});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
    document.getElementById('connection-status').textContent = '连接断开';
    document.getElementById('connection-status').previousElementSibling.className = 'fas fa-circle text-danger me-1';
});

socket.on('system_update', function(data) {
    updateDashboard(data);
    updateCharts(data);
});

// 初始化图表
function initCharts() {
    // CPU图表
    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    cpuChart = new Chart(cpuCtx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [{
                label: 'CPU使用率 (%)',
                data: cpuData,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // 内存图表
    const memoryCtx = document.getElementById('memoryChart').getContext('2d');
    memoryChart = new Chart(memoryCtx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [{
                label: '内存使用率 (%)',
                data: memoryData,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// 加载初始数据
function loadInitialData() {
    fetch('/api/system')
        .then(response => response.json())
        .then(data => {
            updateDashboard(data);
            updateSystemDetails(data);
        })
        .catch(error => console.error('Error loading system data:', error));

    refreshProcesses();
    refreshServices();
}

// 更新仪表板
function updateDashboard(data) {
    if (data.error) {
        console.error('System data error:', data.error);
        return;
    }

    // 更新指标卡片
    document.getElementById('cpu-usage').textContent = data.cpu.percent.toFixed(1) + '%';
    document.getElementById('memory-usage').textContent = data.memory.percent.toFixed(1) + '%';
    document.getElementById('disk-usage').textContent = data.disk.percent.toFixed(1) + '%';
    
    // 计算运行时间
    const days = Math.floor(data.uptime / 86400);
    const hours = Math.floor((data.uptime % 86400) / 3600);
    document.getElementById('uptime').textContent = `${days}天${hours}时`;
}

// 更新图表
function updateCharts(data) {
    if (data.error) return;

    const now = new Date().toLocaleTimeString();
    
    // 限制数据点数量
    if (timeLabels.length >= 20) {
        timeLabels.shift();
        cpuData.shift();
        memoryData.shift();
    }
    
    timeLabels.push(now);
    cpuData.push(data.cpu.percent);
    memoryData.push(data.memory.percent);
    
    cpuChart.update('none');
    memoryChart.update('none');
}

// 更新系统详情
function updateSystemDetails(data) {
    if (data.error) return;

    const systemDetails = document.getElementById('system-details');
    systemDetails.innerHTML = `
        <div class="row">
            <div class="col-6"><strong>CPU核心数:</strong></div>
            <div class="col-6">${data.cpu.count}</div>
        </div>
        <hr>
        <div class="row">
            <div class="col-6"><strong>总内存:</strong></div>
            <div class="col-6">${data.memory.total} GB</div>
        </div>
        <div class="row">
            <div class="col-6"><strong>已用内存:</strong></div>
            <div class="col-6">${data.memory.used} GB</div>
        </div>
        <div class="row">
            <div class="col-6"><strong>可用内存:</strong></div>
            <div class="col-6">${data.memory.available} GB</div>
        </div>
        <hr>
        <div class="row">
            <div class="col-6"><strong>总磁盘:</strong></div>
            <div class="col-6">${data.disk.total} GB</div>
        </div>
        <div class="row">
            <div class="col-6"><strong>已用磁盘:</strong></div>
            <div class="col-6">${data.disk.used} GB</div>
        </div>
        <div class="row">
            <div class="col-6"><strong>可用磁盘:</strong></div>
            <div class="col-6">${data.disk.free} GB</div>
        </div>
        <hr>
        <div class="row">
            <div class="col-6"><strong>系统负载:</strong></div>
            <div class="col-6">${data.load_avg[0].toFixed(2)}, ${data.load_avg[1].toFixed(2)}, ${data.load_avg[2].toFixed(2)}</div>
        </div>
    `;

    const networkStats = document.getElementById('network-stats');
    networkStats.innerHTML = `
        <div class="row">
            <div class="col-6"><strong>发送字节:</strong></div>
            <div class="col-6">${formatBytes(data.network.bytes_sent)}</div>
        </div>
        <div class="row">
            <div class="col-6"><strong>接收字节:</strong></div>
            <div class="col-6">${formatBytes(data.network.bytes_recv)}</div>
        </div>
        <div class="row">
            <div class="col-6"><strong>发送包数:</strong></div>
            <div class="col-6">${data.network.packets_sent.toLocaleString()}</div>
        </div>
        <div class="row">
            <div class="col-6"><strong>接收包数:</strong></div>
            <div class="col-6">${data.network.packets_recv.toLocaleString()}</div>
        </div>
    `;
}

// 刷新进程列表
function refreshProcesses() {
    fetch('/api/processes')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('processes-table');
            tbody.innerHTML = '';
            
            data.forEach(proc => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${proc.pid}</td>
                    <td>${proc.name || 'N/A'}</td>
                    <td>${(proc.cpu_percent || 0).toFixed(1)}%</td>
                    <td>${(proc.memory_percent || 0).toFixed(1)}%</td>
                    <td><span class="badge bg-${proc.status === 'running' ? 'success' : 'secondary'}">${proc.status || 'unknown'}</span></td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="killProcess(${proc.pid})" title="终止进程">
                            <i class="fas fa-times"></i>
                        </button>
                    </td>
                `;
            });
        })
        .catch(error => console.error('Error loading processes:', error));
}

// 刷新服务列表
function refreshServices() {
    fetch('/api/services')
        .then(response => response.json())
        .then(data => {
            const grid = document.getElementById('services-grid');
            grid.innerHTML = '';
            
            data.forEach(service => {
                const col = document.createElement('div');
                col.className = 'col-md-4 mb-3';
                col.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <h6 class="card-title">
                                    <i class="fas fa-cog me-2"></i>${service.name}
                                </h6>
                                <span class="badge bg-${service.active ? 'success' : 'danger'}">
                                    ${service.status}
                                </span>
                            </div>
                            <div class="btn-group btn-group-sm mt-2" role="group">
                                <button class="btn btn-outline-success" onclick="serviceAction('${service.name}', 'start')" title="启动">
                                    <i class="fas fa-play"></i>
                                </button>
                                <button class="btn btn-outline-warning" onclick="serviceAction('${service.name}', 'restart')" title="重启">
                                    <i class="fas fa-redo"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="serviceAction('${service.name}', 'stop')" title="停止">
                                    <i class="fas fa-stop"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                grid.appendChild(col);
            });
        })
        .catch(error => console.error('Error loading services:', error));
}

// 终止进程
function killProcess(pid) {
    if (confirm(`确定要终止进程 ${pid} 吗？`)) {
        fetch(`/api/kill/${pid}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', data.message);
                    refreshProcesses();
                } else {
                    showAlert('danger', data.error);
                }
            })
            .catch(error => {
                console.error('Error killing process:', error);
                showAlert('danger', '操作失败');
            });
    }
}

// 服务操作
function serviceAction(serviceName, action) {
    fetch(`/api/service/${serviceName}/${action}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('success', data.message);
                setTimeout(refreshServices, 1000);
            } else {
                showAlert('danger', data.error);
            }
        })
        .catch(error => {
            console.error('Error with service action:', error);
            showAlert('danger', '操作失败');
        });
}

// 显示警告消息
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// 格式化字节
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 设置事件监听器
function setupEventListeners() {
    // 标签页切换时刷新数据
    document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const target = e.target.getAttribute('href');
            if (target === '#processes') {
                refreshProcesses();
            } else if (target === '#services') {
                refreshServices();
            } else if (target === '#system') {
                fetch('/api/system')
                    .then(response => response.json())
                    .then(data => updateSystemDetails(data));
            } else if (target === '#cameras') {
                loadCameraConfig();
            }
        });
    });
    
    // 摄像头表单提交
    const cameraForm = document.getElementById('camera-form');
    if (cameraForm) {
        cameraForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveCameraConfig();
        });
    }
    
    // 默认显示摄像头页面
    const cameraTab = document.querySelector('a[href="#cameras"]');
    const cameraPane = document.querySelector('#cameras');
    if (cameraTab && cameraPane) {
        // 移除其他活动标签
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
        });
        
        // 激活摄像头标签
        cameraTab.classList.add('active');
        cameraPane.classList.add('show', 'active');
        
        // 加载摄像头配置
        loadCameraConfig();
    }
}

// 摄像头管理功能
function loadCameraConfig() {
    fetch('/api/camera/config')
        .then(response => response.json())
        .then(data => {
            const config = data.config || {};
            document.getElementById('camera-ip').value = config.ip || '';
            document.getElementById('camera-port').value = config.port || 80;
            document.getElementById('camera-username').value = config.username || '';
            document.getElementById('camera-stream-url').value = config.stream_url || '';
            
            // 密码字段处理：如果有配置则显示占位符，否则为空
            const passwordField = document.getElementById('camera-password');
            if (config.ip && config.username) {
                passwordField.placeholder = '当前密码已保存，留空保持不变';
                passwordField.value = '';
            } else {
                passwordField.placeholder = '请输入密码';
                passwordField.value = '';
            }
            
            // 更新连接状态
            updateCameraStatus(Object.keys(config).length > 0);
            
            // 总是尝试显示摄像头流（有配置时显示真实流，无配置时显示演示画面）
            showCameraStream();
        })
        .catch(error => {
            console.error('Error loading camera config:', error);
            updateCameraStatus(false);
        });
}

function saveCameraConfig() {
    const passwordValue = document.getElementById('camera-password').value;
    const formData = {
        ip: document.getElementById('camera-ip').value,
        port: parseInt(document.getElementById('camera-port').value) || 80,
        username: document.getElementById('camera-username').value,
        stream_url: document.getElementById('camera-stream-url').value || '/video'
    };
    
    // 只有在密码字段不为空时才包含密码
    if (passwordValue.trim() !== '') {
        formData.password = passwordValue;
    }
    
    // 验证必填字段（密码可选，如果为空则保持原密码）
    if (!formData.ip || !formData.username) {
        showAlert('danger', '请填写IP地址和用户名');
        return;
    }
    
    // 如果是新配置且没有输入密码，则要求输入密码
    const isNewConfig = !document.getElementById('camera-password').placeholder.includes('已保存');
    if (isNewConfig && !passwordValue.trim()) {
        showAlert('danger', '新配置需要输入密码');
        return;
    }
    
    fetch('/api/camera/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', '摄像头配置保存成功！');
            updateCameraStatus(true);
            showCameraStream();
        } else {
            showAlert('danger', data.error || '保存失败');
            updateCameraStatus(false);
        }
    })
    .catch(error => {
        console.error('Error saving camera config:', error);
        showAlert('danger', '保存摄像头配置失败，请检查网络连接');
        updateCameraStatus(false);
    });
}

function updateCameraStatus(isConfigured) {
    const statusElement = document.getElementById('camera-status');
    if (statusElement) {
        if (isConfigured) {
            statusElement.className = 'badge bg-success';
            statusElement.textContent = '已配置';
        } else {
            statusElement.className = 'badge bg-secondary';
            statusElement.textContent = '未配置';
        }
    }
}

function showCameraStream() {
    const streamContainer = document.getElementById('camera-stream-container');
    if (!streamContainer) return;
    
    const streamHtml = `
        <div class="position-relative">
            <img src="/api/camera/stream?t=${Date.now()}" 
                 class="img-fluid w-100" 
                 style="max-height: 500px; object-fit: contain; border-radius: 8px;"
                 onload="console.log('Camera stream loaded successfully')"
                 onerror="console.log('Camera stream error, but continuing to display content');">
            <div class="position-absolute top-0 start-0 p-2">
                <small class="badge bg-info">摄像头监控</small>
            </div>
        </div>
    `;
    streamContainer.innerHTML = streamHtml;
}

function refreshCamera() {
    const img = document.querySelector('#camera-stream-container img');
    if (img) {
        const baseSrc = img.src.split('?')[0];
        img.src = baseSrc + '?t=' + Date.now();
    }
}

function captureSnapshot() {
    fetch('/api/camera/snapshot')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.image) {
                // 在新窗口中显示快照
                const newWindow = window.open('', '_blank');
                if (newWindow) {
                    newWindow.document.write(`
                    <html>
                        <head><title>摄像头快照</title></head>
                        <body style="margin:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#000;">
                            <img src="${data.image}" style="max-width:100%; max-height:100vh;">
                            <div style="position:absolute; top:10px; right:10px;">
                                <a href="${data.image}" download="camera_snapshot_${Date.now()}.jpg" 
                                   style="color:white; background:rgba(0,0,0,0.5); padding:10px; text-decoration:none; border-radius:5px;">
                                   下载快照
                                </a>
                            </div>
                        </body>
                    </html>
                `);
                } else {
                    // 弹窗被阻止，使用下载方式
                    const link = document.createElement('a');
                    link.href = data.image;
                    link.download = `camera_snapshot_${Date.now()}.jpg`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    showAlert('success', '快照已下载到本地');
                }
            } else {
                showAlert('danger', data.error || '获取快照失败');
            }
        })
        .catch(error => {
            console.error('Error capturing snapshot:', error);
            showAlert('danger', '获取快照失败');
        });
}

// 录制状态管理
let isRecording = false;
let recordingStartTime = null;

function toggleRecording() {
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

function startRecording() {
    fetch('/api/camera/start-recording', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            isRecording = true;
            recordingStartTime = Date.now();
            updateRecordingButton();
            showAlert('success', '开始录制视频');
            
            // 开始显示录制时间
            updateRecordingTimer();
        } else {
            showAlert('danger', data.error || '开始录制失败');
        }
    })
    .catch(error => {
        console.error('Error starting recording:', error);
        showAlert('danger', '开始录制失败');
    });
}

function stopRecording() {
    fetch('/api/camera/stop-recording', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            isRecording = false;
            recordingStartTime = null;
            updateRecordingButton();
            
            if (data.filename) {
                showAlert('success', `录制完成，文件已保存: ${data.filename}`);
            } else {
                showAlert('success', '录制已停止');
            }
        } else {
            showAlert('danger', data.error || '停止录制失败');
        }
    })
    .catch(error => {
        console.error('Error stopping recording:', error);
        showAlert('danger', '停止录制失败');
    });
}

function updateRecordingButton() {
    const recordBtn = document.getElementById('record-btn');
    if (isRecording) {
        recordBtn.innerHTML = '<i class="fas fa-stop me-1"></i>停止录制';
        recordBtn.className = 'btn btn-danger btn-sm';
    } else {
        recordBtn.innerHTML = '<i class="fas fa-record-vinyl me-1"></i>开始录制';
        recordBtn.className = 'btn btn-outline-danger btn-sm';
    }
}

function updateRecordingTimer() {
    if (!isRecording || !recordingStartTime) return;
    
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const timeStr = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const recordBtn = document.getElementById('record-btn');
    recordBtn.innerHTML = `<i class="fas fa-stop me-1"></i>停止录制 (${timeStr})`;
    
    if (isRecording) {
        setTimeout(updateRecordingTimer, 1000);
    }
}

function testOnvifConnection() {
    // 更新ONVIF状态为测试中
    const onvifStatus = document.getElementById('onvif-status');
    onvifStatus.textContent = '测试中...';
    onvifStatus.className = 'badge bg-warning';
    
    fetch('/api/camera/test-onvif')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                onvifStatus.textContent = '连接成功';
                onvifStatus.className = 'badge bg-success';
                
                // 显示详细信息
                let message = 'ONVIF连接成功！\n\n';
                if (data.device_info) {
                    message += `设备信息:\n`;
                    message += `制造商: ${data.device_info.Manufacturer || 'N/A'}\n`;
                    message += `型号: ${data.device_info.Model || 'N/A'}\n`;
                    message += `固件版本: ${data.device_info.FirmwareVersion || 'N/A'}\n`;
                    message += `序列号: ${data.device_info.SerialNumber || 'N/A'}\n\n`;
                }
                if (data.stream_uri) {
                    message += `流地址: ${data.stream_uri}\n`;
                }
                if (data.profile_token) {
                    message += `配置文件令牌: ${data.profile_token}`;
                }
                
                showAlert('success', 'ONVIF连接测试成功');
                console.log('ONVIF连接详情:', data);
            } else {
                onvifStatus.textContent = '连接失败';
                onvifStatus.className = 'badge bg-danger';
                showAlert('danger', `ONVIF连接失败: ${data.error || data.message}`);
            }
        })
        .catch(error => {
            console.error('Error testing ONVIF connection:', error);
            onvifStatus.textContent = '测试失败';
            onvifStatus.className = 'badge bg-danger';
            showAlert('danger', 'ONVIF连接测试失败');
        });
}

function toggleFullscreen() {
    const streamContainer = document.getElementById('camera-stream-container');
    if (!document.fullscreenElement) {
        streamContainer.requestFullscreen().catch(err => {
            showAlert('danger', '无法进入全屏模式');
        });
    } else {
        document.exitFullscreen();
    }
}

// AI功能相关函数
function loadAIModels() {
    fetch('/api/ai/models')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('ai-model-select');
            select.innerHTML = '<option value="">请选择AI模型</option>';
            
            if (data.models && data.models.length > 0) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.path;
                    option.textContent = `${model.name} (${model.type.toUpperCase()}, ${formatBytes(model.size)})`;
                    select.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = '未找到模型文件';
                option.disabled = true;
                select.appendChild(option);
            }
        })
        .catch(error => {
            console.error('Error loading AI models:', error);
            showAlert('danger', '加载AI模型列表失败');
        });
}

function loadAIConfig() {
    fetch('/api/ai/config')
        .then(response => response.json())
        .then(data => {
            if (data.config) {
                const config = data.config;
                
                // 更新UI
                document.getElementById('ai-enabled').checked = config.enabled || false;
                document.getElementById('confidence-threshold').value = config.confidence_threshold || 0.5;
                document.getElementById('nms-threshold').value = config.nms_threshold || 0.4;
                document.getElementById('model-type').value = config.model_type || 'yolo';
                
                // 更新显示值
                document.getElementById('confidence-value').textContent = config.confidence_threshold || 0.5;
                document.getElementById('nms-value').textContent = config.nms_threshold || 0.4;
                
                // 更新状态
                updateAIStatus(config.loaded, config.enabled);
                
                // 如果有加载的模型，选中它
                if (config.model_path) {
                    const select = document.getElementById('ai-model-select');
                    for (let option of select.options) {
                        if (option.value === config.model_path) {
                            option.selected = true;
                            break;
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error loading AI config:', error);
        });
}

function loadAIModel() {
    const modelPath = document.getElementById('ai-model-select').value;
    const modelType = document.getElementById('model-type').value;
    
    if (!modelPath) {
        showAlert('warning', '请先选择一个AI模型');
        return;
    }
    
    const data = {
        model_path: modelPath,
        model_type: modelType
    };
    
    // 显示加载状态
    updateAIStatus(false, false, '加载中...');
    
    fetch('/api/ai/load', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', '模型加载成功');
            loadAIConfig(); // 重新加载配置
        } else {
            showAlert('danger', data.error || '模型加载失败');
            updateAIStatus(false, false);
        }
    })
    .catch(error => {
        console.error('Error loading AI model:', error);
        showAlert('danger', '模型加载失败');
        updateAIStatus(false, false);
    });
}

function saveAIConfig() {
    const data = {
        enabled: document.getElementById('ai-enabled').checked,
        confidence_threshold: parseFloat(document.getElementById('confidence-threshold').value),
        nms_threshold: parseFloat(document.getElementById('nms-threshold').value)
    };
    
    fetch('/api/ai/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'AI配置保存成功');
            loadAIConfig(); // 重新加载配置
        } else {
            showAlert('danger', data.error || 'AI配置保存失败');
        }
    })
    .catch(error => {
        console.error('Error saving AI config:', error);
        showAlert('danger', 'AI配置保存失败');
    });
}

function updateAIStatus(loaded, enabled, customText = null) {
    const statusElement = document.getElementById('ai-status');
    
    if (customText) {
        statusElement.textContent = customText;
        statusElement.className = 'badge bg-info';
        return;
    }
    
    if (loaded && enabled) {
        statusElement.textContent = '运行中';
        statusElement.className = 'badge bg-success';
    } else if (loaded && !enabled) {
        statusElement.textContent = '已加载';
        statusElement.className = 'badge bg-warning';
    } else {
        statusElement.textContent = '未加载';
        statusElement.className = 'badge bg-secondary';
    }
}

// 添加滑块事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 置信度阈值滑块
    const confidenceSlider = document.getElementById('confidence-threshold');
    if (confidenceSlider) {
        confidenceSlider.addEventListener('input', function() {
            document.getElementById('confidence-value').textContent = this.value;
        });
    }
    
    // NMS阈值滑块
    const nmsSlider = document.getElementById('nms-threshold');
    if (nmsSlider) {
        nmsSlider.addEventListener('input', function() {
            document.getElementById('nms-value').textContent = this.value;
        });
    }
    
    // 加载AI模型和配置
    loadAIModels();
    loadAIConfig();
    
    // 加载网络配置
    loadNetworkInterfaces();
    loadNetworkConfig();
    
    // 设置网络配置模式切换
    document.querySelectorAll('input[name="ip-config"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const staticConfig = document.getElementById('static-config');
            if (this.value === 'static') {
                staticConfig.style.display = 'block';
            } else {
                staticConfig.style.display = 'none';
            }
        });
    });
});

// 网络管理函数
function loadNetworkInterfaces() {
    fetch('/api/network/interfaces')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('network-interface');
            select.innerHTML = '<option value="">选择网络接口...</option>';
            
            if (data.success) {
                data.interfaces.forEach(iface => {
                    const option = document.createElement('option');
                    option.value = iface.name;
                    option.textContent = `${iface.name} (${iface.ip || '未配置'})`;
                    select.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('加载网络接口失败:', error);
            showAlert('danger', '加载网络接口失败');
        });
}

function loadNetworkConfig() {
    const interfaceName = document.getElementById('network-interface').value;
    if (!interfaceName) return;
    
    fetch(`/api/network/config/${interfaceName}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const config = data.config;
                
                // 设置IP配置模式
                if (config.dhcp) {
                    document.getElementById('dhcp-mode').checked = true;
                    document.getElementById('static-config').style.display = 'none';
                } else {
                    document.getElementById('static-mode').checked = true;
                    document.getElementById('static-config').style.display = 'block';
                    
                    // 填充静态IP配置
                    document.getElementById('ip-address').value = config.ip || '';
                    document.getElementById('subnet-mask').value = config.netmask || '';
                    document.getElementById('gateway').value = config.gateway || '';
                }
                
                // 填充DNS配置
                document.getElementById('primary-dns').value = config.dns1 || '';
                document.getElementById('secondary-dns').value = config.dns2 || '';
                document.getElementById('domain-suffix').value = config.domain || '';
                
                // 更新网络状态
                document.getElementById('current-ip').textContent = config.current_ip || '-';
                document.getElementById('network-status').textContent = config.status || '未知';
                document.getElementById('network-status').className = 
                    config.status === '已连接' ? 'metric-value text-success' : 'metric-value text-warning';
            }
        })
        .catch(error => {
            console.error('加载网络配置失败:', error);
            showAlert('danger', '加载网络配置失败');
        });
}

function applyNetworkConfig() {
    const interfaceName = document.getElementById('network-interface').value;
    if (!interfaceName) {
        showAlert('warning', '请先选择网络接口');
        return;
    }
    
    const isDHCP = document.getElementById('dhcp-mode').checked;
    const config = {
        interface: interfaceName,
        dhcp: isDHCP
    };
    
    if (!isDHCP) {
        config.ip = document.getElementById('ip-address').value;
        config.netmask = document.getElementById('subnet-mask').value;
        config.gateway = document.getElementById('gateway').value;
        
        // 验证IP地址格式
        if (!config.ip || !config.netmask || !config.gateway) {
            showAlert('warning', '请填写完整的静态IP配置');
            return;
        }
    }
    
    fetch('/api/network/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', '网络配置已应用，正在重启网络服务...');
            setTimeout(() => {
                loadNetworkConfig();
            }, 3000);
        } else {
            showAlert('danger', data.message || '应用网络配置失败');
        }
    })
    .catch(error => {
        console.error('应用网络配置失败:', error);
        showAlert('danger', '应用网络配置失败');
    });
}

function applyDNSConfig() {
    const config = {
        dns1: document.getElementById('primary-dns').value,
        dns2: document.getElementById('secondary-dns').value,
        domain: document.getElementById('domain-suffix').value
    };
    
    fetch('/api/network/dns', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'DNS配置已应用');
        } else {
            showAlert('danger', data.message || '应用DNS配置失败');
        }
    })
    .catch(error => {
        console.error('应用DNS配置失败:', error);
        showAlert('danger', '应用DNS配置失败');
    });
}

function testDNS() {
    const primaryDNS = document.getElementById('primary-dns').value || '8.8.8.8';
    
    showAlert('info', '正在测试DNS连接...');
    
    fetch('/api/network/test-dns', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ dns: primaryDNS })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', `DNS测试成功: ${data.result}`);
        } else {
            showAlert('danger', `DNS测试失败: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('DNS测试失败:', error);
        showAlert('danger', 'DNS测试失败');
    });
}

function pingTest() {
    const target = '8.8.8.8'; // Google DNS
    
    showAlert('info', '正在进行网络连通性测试...');
    
    fetch('/api/network/ping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ target: target })
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('ping-results');
        const outputPre = document.getElementById('ping-output');
        
        if (data.success) {
            outputPre.textContent = data.output;
            resultsDiv.style.display = 'block';
            showAlert('success', '网络连通性测试完成');
        } else {
            outputPre.textContent = data.message || '测试失败';
            resultsDiv.style.display = 'block';
            showAlert('danger', '网络连通性测试失败');
        }
    })
    .catch(error => {
        console.error('网络测试失败:', error);
        showAlert('danger', '网络测试失败');
    });
}

// 网络接口选择变化事件
document.addEventListener('DOMContentLoaded', function() {
    const interfaceSelect = document.getElementById('network-interface');
    if (interfaceSelect) {
        interfaceSelect.addEventListener('change', function() {
            if (this.value) {
                loadNetworkConfig();
            }
        });
    }
});