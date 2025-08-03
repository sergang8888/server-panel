#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import timedelta

class Config:
    """应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ubuntu-web-panel-secret-key-2024'
    
    # 服务器配置
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # SocketIO配置
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # 系统监控配置
    SYSTEM_UPDATE_INTERVAL = 2  # 秒
    MAX_CHART_DATA_POINTS = 20  # 图表最大数据点数
    
    # 进程管理配置
    MAX_PROCESSES_DISPLAY = 50  # 显示的最大进程数
    
    # 监控的系统服务列表
    MONITORED_SERVICES = [
        'nginx',
        'apache2', 
        'mysql',
        'mariadb',
        'postgresql',
        'redis-server',
        'ssh',
        'ufw',
        'docker',
        'fail2ban',
        'cron',
        'rsyslog',
        # Windows服务
        'Spooler',
        'Themes',
        'AudioSrv',
        'BITS',
        'EventLog',
        'Winmgmt',
        'Schedule',
        'W32Time'
    ]
    
    # 安全配置
    REQUIRE_SUDO = True  # 是否需要sudo权限
    ALLOWED_ACTIONS = ['start', 'stop', 'restart', 'enable', 'disable']  # 允许的服务操作
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    
    # 性能配置
    CACHE_TIMEOUT = 5  # 缓存超时时间（秒）
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建日志目录
        log_dir = os.path.dirname(Config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SYSTEM_UPDATE_INTERVAL = 1  # 开发环境更快的更新频率

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    HOST = '127.0.0.1'  # 生产环境只绑定本地
    SOCKETIO_CORS_ALLOWED_ORIGINS = []  # 生产环境限制CORS

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    REQUIRE_SUDO = False  # 测试环境不需要sudo

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}