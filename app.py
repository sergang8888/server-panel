#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
from flask_socketio import SocketIO, emit
import psutil
import os
import subprocess
import json
import logging
from datetime import datetime
import threading
import time
from config import config
import base64
from urllib.parse import quote
import requests
from io import BytesIO
import urllib.request
import urllib.error
import cv2
import numpy as np
from ai_processor import ai_processor
from onvif import ONVIFCamera
import socket

# 创建Flask应用
app = Flask(__name__)

# 加载配置
config_name = os.environ.get('FLASK_ENV') or 'default'
app.config.from_object(config[config_name])
config[config_name].init_app(app)

# 尝试加载用户配置
try:
    import config_user
    # 更新Flask配置
    if hasattr(config_user, 'HOST'):
        app.config['HOST'] = config_user.HOST
    if hasattr(config_user, 'PORT'):
        app.config['PORT'] = config_user.PORT
    if hasattr(config_user, 'DEBUG'):
        app.config['DEBUG'] = config_user.DEBUG
except ImportError:
    config_user = None

# 配置日志
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(app.config['LOG_FILE']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 记录配置加载状态
if config_user is None:
    logger.warning("config_user.py not found, using default configuration")

# 创建SocketIO实例
socketio = SocketIO(
    app, 
    cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'],
    async_mode=app.config['SOCKETIO_ASYNC_MODE']
)

# 摄像头配置存储
camera_config = {}

# 初始化默认摄像头配置
if config_user:
    try:
        camera_config.update({
            'name': 'Default Camera',
            'ip': getattr(config_user, 'DEFAULT_CAMERA_IP', '192.168.1.100'),
            'port': getattr(config_user, 'DEFAULT_CAMERA_PORT', 554),
            'username': getattr(config_user, 'DEFAULT_CAMERA_USERNAME', 'admin'),
            'password': getattr(config_user, 'DEFAULT_CAMERA_PASSWORD', '123456'),
            'stream_url': getattr(config_user, 'DEFAULT_STREAM_URL', '/video')
        })
        logger.info(f"Loaded default camera config: {camera_config['ip']}:{camera_config['port']}")
    except Exception as e:
        logger.error(f"Error loading default camera config: {e}")

# ONVIF摄像头连接函数
def connect_onvif_camera(ip, port, username, password):
    """连接ONVIF摄像头并获取流媒体URL"""
    try:
        # 创建ONVIF摄像头实例
        mycam = ONVIFCamera(ip, port, username, password)
        
        # 获取设备信息
        device_info = {}
        try:
            device_service = mycam.create_devicemgmt_service()
            device_information = device_service.GetDeviceInformation()
            device_info = {
                'Manufacturer': getattr(device_information, 'Manufacturer', 'Unknown'),
                'Model': getattr(device_information, 'Model', 'Unknown'),
                'FirmwareVersion': getattr(device_information, 'FirmwareVersion', 'Unknown'),
                'SerialNumber': getattr(device_information, 'SerialNumber', 'Unknown'),
                'HardwareId': getattr(device_information, 'HardwareId', 'Unknown')
            }
        except Exception as e:
            logger.warning(f"Failed to get device information: {e}")
            device_info = {'Manufacturer': 'Unknown', 'Model': 'Unknown', 'FirmwareVersion': 'Unknown', 'SerialNumber': 'Unknown'}
        
        # 获取媒体服务
        media_service = mycam.create_media_service()
        
        # 获取配置文件
        profiles = media_service.GetProfiles()
        
        if not profiles:
            logger.error("No media profiles found")
            return None
            
        # 使用第一个配置文件
        profile = profiles[0]
        
        # 获取流媒体URI
        stream_setup = media_service.create_type('GetStreamUri')
        stream_setup.ProfileToken = profile.token
        stream_setup.StreamSetup = {
            'Stream': 'RTP-Unicast',
            'Transport': {'Protocol': 'RTSP'}
        }
        
        stream_uri = media_service.GetStreamUri(stream_setup)
        
        logger.info(f"ONVIF camera connected: {ip}:{port}")
        logger.info(f"Stream URI: {stream_uri.Uri}")
        
        return {
            'camera': mycam,
            'media_service': media_service,
            'profile': profile,
            'stream_uri': stream_uri.Uri,
            'device_info': device_info
        }
        
    except Exception as e:
        logger.error(f"Failed to connect ONVIF camera {ip}:{port}: {str(e)}")
        return None

def get_onvif_snapshot(ip, port, username, password):
    """获取ONVIF摄像头快照"""
    try:
        onvif_info = connect_onvif_camera(ip, port, username, password)
        if not onvif_info:
            return None
            
        media_service = onvif_info['media_service']
        profile = onvif_info['profile']
        
        # 获取快照URI
        snapshot_uri = media_service.GetSnapshotUri({'ProfileToken': profile.token})
        
        # 下载快照
        response = requests.get(snapshot_uri.Uri, auth=(username, password), timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Failed to get snapshot: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting ONVIF snapshot: {str(e)}")
        return None

# 系统信息获取函数
def get_system_info():
    """获取系统基本信息"""
    try:
        # CPU信息
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
        except Exception as e:
            raise e
        
        # 内存信息
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total = round(memory.total / (1024**3), 2)  # GB
            memory_used = round(memory.used / (1024**3), 2)   # GB
        except Exception as e:
            raise e
        
        # 磁盘信息 - 使用shutil替代psutil避免格式化错误
        try:
            import shutil
            if os.name == 'nt':
                # Windows系统
                total, used, free = shutil.disk_usage('C:\\')
            else:
                # Linux系统
                total, used, free = shutil.disk_usage('/')
            
            disk_total = round(total / (1024**3), 2)  # GB
            disk_used = round(used / (1024**3), 2)   # GB
            disk_free = round(free / (1024**3), 2)  # GB
            disk_percent = round((used / total) * 100, 2)
        except Exception as e:
            # 如果磁盘信息获取失败，使用默认值
            disk_percent = 0
            disk_total = 0
            disk_used = 0
            disk_free = 0
        
        # 网络信息
        try:
            network = psutil.net_io_counters()
        except Exception as e:
            raise e
        
        # 系统负载（Windows系统不支持getloadavg）
        try:
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
            else:
                # Windows系统使用CPU使用率作为替代
                load_avg = [cpu_percent/100, cpu_percent/100, cpu_percent/100]
        except Exception as e:
            # 确保错误信息不包含格式化字符
            error_msg = str(e).replace('%', '%%')
            logger.warning(f"Could not get load average: {error_msg}")
            load_avg = [0, 0, 0]
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': {
                'percent': memory_percent,
                'total': memory_total,
                'used': memory_used,
                'available': round(memory.available / (1024**3), 2)
            },
            'disk': {
                'percent': disk_percent,
                'total': disk_total,
                'used': disk_used,
                'free': disk_free
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'load_avg': load_avg,
            'uptime': time.time() - psutil.boot_time()
        }
    except Exception as e:
        # 确保错误信息不包含格式化字符，避免日志记录时出现格式化错误
        error_msg = str(e).replace('%', '%%')
        return {'error': error_msg}

def get_processes():
    """获取进程列表"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:50]
    except Exception as e:
        return []

def get_services():
    """获取系统服务状态"""
    services = []
    monitored_services = app.config['MONITORED_SERVICES']
    
    # 检测操作系统
    is_windows = os.name == 'nt'
    
    for service in monitored_services:
        try:
            if is_windows:
                # Windows系统使用sc命令
                result = subprocess.run(['sc', 'query', service], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'RUNNING' in result.stdout:
                    status = 'active'
                    active = True
                elif result.returncode == 0 and 'STOPPED' in result.stdout:
                    status = 'inactive'
                    active = False
                else:
                    status = 'not-found'
                    active = False
            else:
                # Linux系统使用systemctl命令
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True, timeout=5)
                status = result.stdout.strip()
                active = status == 'active'
            
            services.append({
                'name': service,
                'status': status,
                'active': active
            })
            logger.debug(f"Service {service} status: {status}")
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout checking service {service}")
            services.append({
                'name': service,
                'status': 'timeout',
                'active': False
            })
        except Exception as e:
            logger.error(f"Error checking service {service}: {str(e)}")
            services.append({
                'name': service,
                'status': 'unknown',
                'active': False
            })
    
    return services

# 路由定义
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/system')
def api_system():
    """系统信息API"""
    return jsonify(get_system_info())

@app.route('/api/processes')
def api_processes():
    """进程信息API"""
    return jsonify(get_processes())

@app.route('/api/services')
def api_services():
    """服务信息API"""
    return jsonify(get_services())

@app.route('/api/service/<service_name>/<action>')
def api_service_action(service_name, action):
    """服务操作API"""
    # 验证操作类型
    if action not in app.config['ALLOWED_ACTIONS']:
        logger.warning(f"Invalid action attempted: {action}")
        return jsonify({'error': 'Invalid action'}), 400
    
    # 验证服务名称
    if service_name not in app.config['MONITORED_SERVICES']:
        logger.warning(f"Unauthorized service access attempted: {service_name}")
        return jsonify({'error': 'Service not allowed'}), 403
    
    try:
        logger.info(f"Executing {action} on service {service_name}")
        
        # 检测操作系统并构建命令
        is_windows = os.name == 'nt'
        
        if is_windows:
            # Windows系统使用sc命令
            if action == 'start':
                cmd = ['sc', 'start', service_name]
            elif action == 'stop':
                cmd = ['sc', 'stop', service_name]
            elif action == 'restart':
                # Windows重启需要先停止再启动
                stop_result = subprocess.run(['sc', 'stop', service_name], 
                                           capture_output=True, text=True, timeout=10)
                time.sleep(2)  # 等待服务停止
                cmd = ['sc', 'start', service_name]
            else:
                return jsonify({'error': f'Action {action} not supported on Windows'}), 400
        else:
            # Linux系统使用systemctl命令
            cmd = ['systemctl', action, service_name]
            if app.config['REQUIRE_SUDO']:
                cmd.insert(0, 'sudo')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            logger.info(f"Service {service_name} {action}ed successfully")
            return jsonify({
                'success': True, 
                'message': f'Service {service_name} {action}ed successfully'
            })
        else:
            logger.error(f"Service {service_name} {action} failed: {result.stderr}")
            return jsonify({'error': result.stderr or 'Operation failed'}), 500
            
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout executing {action} on service {service_name}")
        return jsonify({'error': 'Operation timeout'}), 500
    except Exception as e:
        logger.error(f"Error executing {action} on service {service_name}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 摄像头管理API
@app.route('/api/camera/config', methods=['GET'])
def get_camera_config():
    """获取摄像头配置"""
    try:
        # 返回摄像头配置，不包含密码
        config = camera_config.copy()
        config.pop('password', None)  # 移除密码字段
        return jsonify({'config': config})
    except Exception as e:
        logger.error(f"Get camera config error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/config', methods=['POST'])
def save_camera_config():
    """保存摄像头配置"""
    try:
        data = request.get_json()
        
        # 保存摄像头配置到内存
        update_data = {
            'name': data.get('name'),
            'ip': data.get('ip'),
            'port': data.get('port', 80),
            'username': data.get('username'),
            'stream_url': data.get('stream_url', '/video')
        }
        
        # 只有在提供了密码时才更新密码
        if 'password' in data and data.get('password'):
            update_data['password'] = data.get('password')
        
        camera_config.update(update_data)
        
        # 持久化保存到配置文件
        try:
            config_file_path = 'config_user.py'
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # 更新配置文件中的摄像头配置
            import re
            config_content = re.sub(r"DEFAULT_CAMERA_IP = '[^']*'", f"DEFAULT_CAMERA_IP = '{data.get('ip')}'", config_content)
            config_content = re.sub(r"DEFAULT_CAMERA_PORT = \d+", f"DEFAULT_CAMERA_PORT = {data.get('port', 80)}", config_content)
            config_content = re.sub(r"DEFAULT_CAMERA_USERNAME = '[^']*'", f"DEFAULT_CAMERA_USERNAME = '{data.get('username')}'", config_content)
            
            # 只有在提供了密码时才更新配置文件中的密码
            if 'password' in data and data.get('password'):
                config_content = re.sub(r"DEFAULT_CAMERA_PASSWORD = '[^']*'", f"DEFAULT_CAMERA_PASSWORD = '{data.get('password')}'", config_content)
            
            config_content = re.sub(r"DEFAULT_STREAM_URL = '[^']*'", f"DEFAULT_STREAM_URL = '{data.get('stream_url', '/video')}'", config_content)
            
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
                
            logger.info(f"Camera config persisted to file: {data.get('ip')}")
        except Exception as e:
            logger.warning(f"Failed to persist camera config to file: {e}")
        
        logger.info(f"Camera config saved: {data.get('name')}")
        return jsonify({'success': True, 'message': 'Camera config saved successfully'})
    except Exception as e:
        logger.error(f"Save camera config error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/stream')
def camera_stream():
    """摄像头流媒体代理"""
    try:
        # 即使没有配置也显示演示画面
        logger.info(f"Camera stream requested, config: {bool(camera_config)}")
        
        def generate_demo_frame():
            """生成演示帧"""
            try:
                from PIL import Image, ImageDraw, ImageFont
                import io
                
                # 创建一个640x480的演示图像
                img = Image.new('RGB', (640, 480), color=(64, 64, 64))
                draw = ImageDraw.Draw(img)
                
                # 添加文本
                try:
                    font_large = ImageFont.truetype("arial.ttf", 24)
                    font_small = ImageFont.truetype("arial.ttf", 16)
                except:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                
                text1 = "Camera Demo Mode"
                text2 = f"Time: {datetime.now().strftime('%H:%M:%S')}"
                text3 = f"IP: {camera_config.get('ip', 'N/A') if camera_config else 'Not Configured'}"
                text4 = "Camera not accessible" if camera_config else "No camera configured"
                
                draw.text((180, 200), text1, fill=(255, 255, 255), font=font_large)
                draw.text((200, 240), text2, fill=(0, 255, 0), font=font_small)
                draw.text((220, 280), text3, fill=(0, 255, 255), font=font_small)
                draw.text((180, 320), text4, fill=(255, 0, 0), font=font_small)
                
                # 编码为JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return buffer.getvalue()
            except Exception as e:
                logger.error(f"Demo frame generation error: {e}")
                # 返回一个简单的静态图像数据
                return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\'\" \x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\xff\xc0\x00\x11\x08\x01\xe0\x02\x80\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        
        def generate_frames():
            camera_accessible = False
            last_error_log = 0
            onvif_stream_uri = None
            cap = None
            
            # 如果没有摄像头配置，直接生成演示帧
            if not camera_config:
                logger.info("No camera configuration, generating demo frames only")
                while True:
                    try:
                        frame_data = generate_demo_frame()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                        time.sleep(1)
                    except:
                        break
                return
            
            try:
                # 首先尝试ONVIF协议连接
                logger.info(f"Attempting ONVIF connection to {camera_config['ip']}:{camera_config['port']}")
                onvif_info = connect_onvif_camera(
                    camera_config['ip'], 
                    camera_config['port'], 
                    camera_config['username'], 
                    camera_config['password']
                )
                
                if onvif_info:
                    onvif_stream_uri = onvif_info['stream_uri']
                    logger.info(f"ONVIF connection successful, stream URI: {onvif_stream_uri}")
                    
                    # 尝试使用OpenCV连接RTSP流
                    try:
                        cap = cv2.VideoCapture(onvif_stream_uri)
                        if cap.isOpened():
                            logger.info("RTSP stream opened successfully")
                            camera_accessible = True
                        else:
                            logger.warning("Failed to open RTSP stream")
                            cap = None
                    except Exception as e:
                        logger.error(f"Error opening RTSP stream: {e}")
                        cap = None
                else:
                    logger.warning("ONVIF connection failed, falling back to HTTP methods")
                
                # 如果ONVIF失败，尝试HTTP路径
                possible_paths = [
                    camera_config.get('stream_url', '/video'),
                    '/video',
                    '/mjpg/video.mjpg',
                    '/videostream.cgi',
                    '/video.cgi',
                    '/axis-cgi/mjpg/video.cgi',
                    '/cgi-bin/mjpg/video.cgi'
                ]
                
                while True:
                    frame_data = None
                    current_time = time.time()
                    
                    try:
                        # 优先使用ONVIF RTSP流
                        if cap and cap.isOpened():
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                if not camera_accessible:
                                    logger.info(f"ONVIF camera connected successfully: {camera_config['ip']}:{camera_config['port']}")
                                    camera_accessible = True
                                
                                # AI处理
                                if ai_processor.enabled and ai_processor.model is not None:
                                    try:
                                        processed_frame = ai_processor.process_frame(frame)
                                        frame = processed_frame
                                    except Exception as e:
                                        logger.error(f"AI processing error: {e}")
                                
                                # 录制处理
                                global recording_writer
                                if recording_writer is not None:
                                    try:
                                        recording_writer.write(frame)
                                    except Exception as e:
                                        logger.error(f"Recording write error: {e}")
                                
                                # 编码为JPEG
                                _, buffer = cv2.imencode('.jpg', frame)
                                frame_data = buffer.tobytes()
                                
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                                time.sleep(0.033)  # ~30 FPS
                                continue
                            else:
                                # RTSP流断开，尝试重连
                                if camera_accessible:
                                    logger.warning("RTSP stream disconnected, attempting reconnection")
                                    camera_accessible = False
                                if cap:
                                    cap.release()
                                cap = cv2.VideoCapture(onvif_stream_uri)
                        
                        # 如果ONVIF不可用，尝试HTTP方法（但减少尝试频率）
                        if not camera_accessible and not onvif_stream_uri:
                            # 只有在ONVIF完全失败时才尝试HTTP方法
                            for path in possible_paths:
                                try:
                                    url = f"http://{camera_config['ip']}:{camera_config['port']}{path}"
                                    
                                    # 创建认证处理器
                                    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                                    password_mgr.add_password(None, url, camera_config['username'], camera_config['password'])
                                    auth_handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
                                    opener = urllib.request.build_opener(auth_handler)
                                    
                                    req = urllib.request.Request(url)
                                    with opener.open(req, timeout=3) as response:
                                        if response.getcode() == 200:
                                            frame_data = response.read()
                                            
                                            # 检查是否是有效的图像数据
                                            if frame_data and len(frame_data) > 100:
                                                if not camera_accessible:
                                                    logger.info(f"HTTP camera connected successfully: {camera_config['ip']}:{camera_config['port']}{path}")
                                                    camera_accessible = True
                                                
                                                # AI处理
                                                if ai_processor.enabled and ai_processor.model is not None:
                                                    try:
                                                        # 将字节数据转换为numpy数组
                                                        nparr = np.frombuffer(frame_data, np.uint8)
                                                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                                        
                                                        if frame is not None:
                                                            # 应用AI处理
                                                            processed_frame = ai_processor.process_frame(frame)
                                                            
                                                            # 将处理后的帧编码回JPEG
                                                            _, buffer = cv2.imencode('.jpg', processed_frame)
                                                            frame_data = buffer.tobytes()
                                                    except Exception as e:
                                                        logger.error(f"AI processing error: {e}")
                                                        # 如果AI处理失败，使用原始帧
                                                        pass
                                                
                                                yield (b'--frame\r\n'
                                                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                                                break
                                except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                                    # 减少HTTP错误日志频率，特别是当ONVIF工作时
                                    if current_time - last_error_log > 300:  # 每5分钟记录一次错误
                                        if not onvif_stream_uri:  # 只有在ONVIF也失败时才记录HTTP错误
                                            logger.warning(f"HTTP camera connection failed for {camera_config['ip']}:{camera_config['port']}{path}: {str(e)}")
                                        last_error_log = current_time
                                    continue
                        
                        # 如果无法获取真实摄像头图像，使用演示帧
                        if frame_data is None:
                            if camera_accessible:
                                logger.warning(f"Camera disconnected: {camera_config['ip']}:{camera_config['port']}")
                                camera_accessible = False
                            
                            logger.info("Generating demo frame due to camera unavailability")
                            frame_data = generate_demo_frame()
                            if frame_data:
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                            else:
                                logger.error("Failed to generate demo frame")
                        
                        time.sleep(0.5)  # 控制帧率
                        
                    except Exception as e:
                        if current_time - last_error_log > 30:
                            logger.error(f"Frame capture error: {e}")
                            last_error_log = current_time
                        
                        # 发送演示帧
                        frame_data = generate_demo_frame()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                        time.sleep(1)
                
            except Exception as e:
                logger.error(f"Camera stream error: {e}")
                # 发送演示帧作为后备
                while True:
                    try:
                        frame_data = generate_demo_frame()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                        time.sleep(1)
                    except:
                        break
            finally:
                # 清理资源
                if cap:
                    cap.release()
        
        response = Response(generate_frames(),
                           mimetype='multipart/x-mixed-replace; boundary=frame')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Connection'] = 'keep-alive'
        return response
    except Exception as e:
        logger.error(f"Camera stream setup error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/snapshot')
def camera_snapshot():
    """获取摄像头快照"""
    try:
        if not camera_config:
            return jsonify({'error': 'Camera not configured'}), 404
        
        # 首先尝试ONVIF快照
        logger.info(f"Attempting ONVIF snapshot from {camera_config['ip']}:{camera_config['port']}")
        onvif_snapshot = get_onvif_snapshot(
            camera_config['ip'],
            camera_config['port'],
            camera_config['username'],
            camera_config['password']
        )
        
        if onvif_snapshot:
            logger.info("ONVIF snapshot captured successfully")
            img_base64 = base64.b64encode(onvif_snapshot).decode('utf-8')
            return jsonify({'success': True, 'image': f'data:image/jpeg;base64,{img_base64}'})
        else:
            logger.warning("ONVIF snapshot failed, falling back to HTTP methods")
        
        # 如果ONVIF失败，尝试多种常见的摄像头HTTP路径获取快照
        possible_paths = [
            '/snapshot.cgi',
            '/jpg/image.jpg',
            '/axis-cgi/jpg/image.cgi',
            '/cgi-bin/snapshot.cgi',
            '/video',
            '/mjpg/video.mjpg'
        ]
        
        for path in possible_paths:
            try:
                url = f"http://{camera_config['username']}:{camera_config['password']}@{camera_config['ip']}:{camera_config['port']}{path}"
                
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.getcode() == 200:
                        image_data = response.read()
                        
                        # 检查是否是有效的图像数据
                        if image_data and len(image_data) > 100:
                            logger.info(f"HTTP snapshot captured successfully from {path}")
                            img_base64 = base64.b64encode(image_data).decode('utf-8')
                            return jsonify({'success': True, 'image': f'data:image/jpeg;base64,{img_base64}'})
                            
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                logger.debug(f"Failed to get snapshot from {url}: {e}")
                continue
        
        return jsonify({'error': 'Failed to capture snapshot from camera'}), 500
            
    except Exception as e:
        logger.error(f"Camera snapshot error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/test-onvif')
def test_onvif_connection():
    """测试ONVIF连接状态"""
    try:
        if not camera_config:
            return jsonify({'error': 'Camera not configured'}), 404
        
        logger.info(f"Testing ONVIF connection to {camera_config['ip']}:{camera_config['port']}")
        
        # 尝试ONVIF连接
        onvif_info = connect_onvif_camera(
            camera_config['ip'],
            camera_config['port'],
            camera_config['username'],
            camera_config['password']
        )
        
        if onvif_info:
            return jsonify({
                'success': True,
                'message': 'ONVIF connection successful',
                'device_info': onvif_info.get('device_info', {}),
                'stream_uri': onvif_info.get('stream_uri', ''),
                'profile_token': onvif_info['profile'].token if onvif_info.get('profile') else None
            })
        else:
            return jsonify({
                'success': False,
                'message': 'ONVIF connection failed',
                'error': 'Unable to connect to ONVIF camera'
            })
            
    except Exception as e:
        logger.error(f"ONVIF test error: {e}")
        return jsonify({
            'success': False,
            'message': 'ONVIF test failed',
            'error': str(e)
        }), 500

# 录制功能相关变量
recording_writer = None
recording_filename = None
recording_start_time = None

@app.route('/api/camera/start-recording', methods=['POST'])
def start_recording():
    """开始录制视频"""
    global recording_writer, recording_filename, recording_start_time
    
    try:
        if not camera_config:
            return jsonify({'success': False, 'error': '摄像头未配置'}), 400
            
        if recording_writer is not None:
            return jsonify({'success': False, 'error': '录制已在进行中'}), 400
            
        # 创建录制文件夹
        recordings_dir = os.path.join(os.path.dirname(__file__), 'recordings')
        os.makedirs(recordings_dir, exist_ok=True)
        
        # 生成录制文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        recording_filename = f'camera_recording_{timestamp}.mp4'
        recording_path = os.path.join(recordings_dir, recording_filename)
        
        # 获取摄像头连接
        onvif_info = connect_onvif_camera(
            camera_config['ip'], 
            camera_config['port'], 
            camera_config['username'], 
            camera_config['password']
        )
        
        if onvif_info and onvif_info.get('stream_uri'):
            # 使用ONVIF RTSP流
            cap = cv2.VideoCapture(onvif_info['stream_uri'])
        else:
            # 尝试HTTP连接
            stream_url = f"http://{camera_config['ip']}:{camera_config['port']}{camera_config.get('stream_url', '/video')}"
            cap = cv2.VideoCapture(stream_url)
            
        if not cap.isOpened():
            return jsonify({'success': False, 'error': '无法连接到摄像头'}), 500
            
        # 获取视频参数
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        recording_writer = cv2.VideoWriter(recording_path, fourcc, fps, (width, height))
        recording_start_time = datetime.now()
        
        cap.release()
        
        logger.info(f"Started recording: {recording_filename}")
        return jsonify({
            'success': True, 
            'message': '开始录制',
            'filename': recording_filename
        })
        
    except Exception as e:
        logger.error(f"Start recording error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/camera/stop-recording', methods=['POST'])
def stop_recording():
    """停止录制视频"""
    global recording_writer, recording_filename, recording_start_time
    
    try:
        if recording_writer is None:
            return jsonify({'success': False, 'error': '当前没有录制在进行'}), 400
            
        # 停止录制
        recording_writer.release()
        recording_writer = None
        
        duration = None
        if recording_start_time:
            duration = (datetime.now() - recording_start_time).total_seconds()
            
        filename = recording_filename
        recording_filename = None
        recording_start_time = None
        
        logger.info(f"Stopped recording: {filename}, duration: {duration}s")
        return jsonify({
            'success': True, 
            'message': '录制已停止',
            'filename': filename,
            'duration': duration
        })
        
    except Exception as e:
        logger.error(f"Stop recording error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# AI模型管理API
@app.route('/api/ai/models', methods=['GET'])
def get_ai_models():
    """获取可用的AI模型列表"""
    try:
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        models = []
        
        if os.path.exists(models_dir):
            for file in os.listdir(models_dir):
                if file.endswith(('.weights', '.pb', '.onnx', '.pt')):
                    model_path = os.path.join(models_dir, file)
                    models.append({
                        'name': file,
                        'path': model_path,
                        'size': os.path.getsize(model_path),
                        'type': file.split('.')[-1]
                    })
        
        return jsonify({'models': models})
    except Exception as e:
        logger.error(f"Get AI models error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/load', methods=['POST'])
def load_ai_model():
    """加载AI模型"""
    try:
        data = request.get_json()
        model_path = data.get('model_path')
        config_path = data.get('config_path')
        model_type = data.get('model_type', 'yolo')
        
        if not model_path:
            return jsonify({'error': 'Model path is required'}), 400
        
        # 加载模型
        success = ai_processor.load_model(model_path, config_path, model_type)
        
        if success:
            return jsonify({'success': True, 'message': 'Model loaded successfully'})
        else:
            return jsonify({'error': 'Failed to load model'}), 500
            
    except Exception as e:
        logger.error(f"Load AI model error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/config', methods=['GET'])
def get_ai_config():
    """获取AI配置"""
    try:
        config = ai_processor.get_model_info()
        return jsonify({'config': config})
    except Exception as e:
        logger.error(f"Get AI config error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/config', methods=['POST'])
def update_ai_config():
    """更新AI配置"""
    try:
        data = request.get_json()
        
        if 'enabled' in data:
            ai_processor.set_enabled(data['enabled'])
        
        if 'confidence_threshold' in data:
            ai_processor.set_confidence_threshold(data['confidence_threshold'])
        
        if 'nms_threshold' in data:
            ai_processor.set_nms_threshold(data['nms_threshold'])
        
        return jsonify({'success': True, 'message': 'AI config updated successfully'})
    except Exception as e:
        logger.error(f"Update AI config error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/kill/<int:pid>')
def api_kill_process(pid):
    """终止进程API"""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return jsonify({'success': True, 'message': f'Process {pid} terminated'})
    except psutil.NoSuchProcess:
        return jsonify({'error': 'Process not found'}), 404
    except psutil.AccessDenied:
        return jsonify({'error': 'Access denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 网络管理API
@app.route('/api/network/interfaces', methods=['GET'])
def get_network_interfaces():
    """获取网络接口列表"""
    try:
        interfaces = []
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            interface_info = {'name': interface_name, 'ip': None}
            for addr in interface_addresses:
                if addr.family == 2:  # IPv4
                    interface_info['ip'] = addr.address
                    break
            interfaces.append(interface_info)
        
        return jsonify({'success': True, 'interfaces': interfaces})
    except Exception as e:
        logger.error(f"Failed to get network interfaces: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/network/config/<interface_name>', methods=['GET'])
def get_network_config(interface_name):
    """获取指定网络接口的配置"""
    try:
        config = {
            'dhcp': True,
            'ip': '',
            'netmask': '',
            'gateway': '',
            'dns1': '',
            'dns2': '',
            'domain': '',
            'current_ip': '',
            'status': '未知'
        }
        
        # 获取当前IP地址
        if interface_name in psutil.net_if_addrs():
            for addr in psutil.net_if_addrs()[interface_name]:
                if addr.family == 2:  # IPv4
                    config['current_ip'] = addr.address
                    config['netmask'] = addr.netmask
                    config['status'] = '已连接'
                    break
        
        # 获取默认网关
        try:
            gateways = psutil.net_if_stats()
            if interface_name in gateways and gateways[interface_name].isup:
                # 尝试获取路由表信息（Windows）
                if os.name == 'nt':
                    result = subprocess.run(['route', 'print', '0.0.0.0'], 
                                          capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if '0.0.0.0' in line and interface_name.lower() in line.lower():
                                parts = line.split()
                                if len(parts) >= 3:
                                    config['gateway'] = parts[2]
                                    break
        except Exception:
            pass
        
        # 读取DNS配置（Windows）
        try:
            if os.name == 'nt':
                result = subprocess.run(['nslookup', 'localhost'], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Address:' in line and '127.0.0.1' not in line:
                            dns_ip = line.split(':')[-1].strip()
                            if not config['dns1']:
                                config['dns1'] = dns_ip
                            elif not config['dns2']:
                                config['dns2'] = dns_ip
        except Exception:
            pass
        
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        logger.error(f"Failed to get network config for {interface_name}: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/network/config', methods=['POST'])
def apply_network_config():
    """应用网络配置"""
    try:
        data = request.get_json()
        interface_name = data.get('interface')
        is_dhcp = data.get('dhcp', True)
        
        if not interface_name:
            return jsonify({'success': False, 'message': '未指定网络接口'})
        
        if os.name == 'nt':  # Windows
            if is_dhcp:
                # 启用DHCP
                cmd = f'netsh interface ip set address "{interface_name}" dhcp'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return jsonify({'success': False, 'message': f'启用DHCP失败: {result.stderr}'})
            else:
                # 设置静态IP
                ip_address = data.get('ip')
                netmask = data.get('netmask')
                gateway = data.get('gateway')
                
                if not all([ip_address, netmask, gateway]):
                    return jsonify({'success': False, 'message': '静态IP配置不完整'})
                
                cmd = f'netsh interface ip set address "{interface_name}" static {ip_address} {netmask} {gateway}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return jsonify({'success': False, 'message': f'设置静态IP失败: {result.stderr}'})
        
        return jsonify({'success': True, 'message': '网络配置已应用'})
    except Exception as e:
        logger.error(f"Failed to apply network config: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/network/dns', methods=['POST'])
def apply_dns_config():
    """应用DNS配置"""
    try:
        data = request.get_json()
        dns1 = data.get('dns1')
        dns2 = data.get('dns2')
        
        if os.name == 'nt':  # Windows
            if dns1:
                cmd = f'netsh interface ip set dns "以太网" static {dns1}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return jsonify({'success': False, 'message': f'设置主DNS失败: {result.stderr}'})
            
            if dns2:
                cmd = f'netsh interface ip add dns "以太网" {dns2} index=2'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f'设置备用DNS失败: {result.stderr}')
        
        return jsonify({'success': True, 'message': 'DNS配置已应用'})
    except Exception as e:
        logger.error(f"Failed to apply DNS config: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/network/test-dns', methods=['POST'])
def test_dns():
    """测试DNS连接"""
    try:
        data = request.get_json()
        dns_server = data.get('dns', '8.8.8.8')
        
        # 使用nslookup测试DNS
        cmd = f'nslookup google.com {dns_server}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'result': f'DNS服务器 {dns_server} 响应正常'})
        else:
            return jsonify({'success': False, 'message': f'DNS服务器 {dns_server} 无响应'})
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'DNS测试超时'})
    except Exception as e:
        logger.error(f"DNS test failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/network/ping', methods=['POST'])
def ping_test():
    """网络连通性测试"""
    try:
        data = request.get_json()
        target = data.get('target', '8.8.8.8')
        
        # Windows ping命令
        if os.name == 'nt':
            cmd = f'ping -n 4 {target}'
        else:
            cmd = f'ping -c 4 {target}'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'Ping测试超时'})
    except Exception as e:
        logger.error(f"Ping test failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# WebSocket事件
@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print('Client connected')
    emit('status', {'msg': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    print('Client disconnected')

# 实时数据推送
def background_thread():
    """后台线程，定期推送系统信息"""
    logger.info("Background thread started")
    while True:
        try:
            socketio.sleep(app.config['SYSTEM_UPDATE_INTERVAL'])
            system_info = get_system_info()
            if 'error' not in system_info:
                socketio.emit('system_update', system_info)
            else:
                logger.error(f"System info error: {system_info['error']}")
                socketio.emit('system_update', {'error': system_info['error'].replace('%', '%%')})
        except Exception as e:
            logger.error(f"Background thread error: {str(e)}")
            socketio.sleep(5)  # 错误时等待更长时间

if __name__ == '__main__':
    # 启动后台线程
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    
    # 启动应用
    logger.info(f"Starting Ubuntu Web Panel on {app.config['HOST']}:{app.config['PORT']}")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    
    try:
        socketio.run(
            app, 
            host=app.config['HOST'], 
            port=app.config['PORT'], 
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise