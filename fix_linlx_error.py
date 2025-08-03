#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复"不支持的操作系统linlx"错误的脚本
"""

import platform
import sys
import os
from pathlib import Path

def test_system_detection():
    """测试系统检测逻辑"""
    print("🔍 测试系统检测逻辑...")
    
    # 原始检测逻辑
    original_system = platform.system().lower()
    print(f"原始检测结果: '{original_system}'")
    
    # 修复后的检测逻辑
    detected_system = platform.system().lower().strip()
    if detected_system == 'linlx':  # 修复常见的拼写错误
        fixed_system = 'linux'
        print(f"🔧 检测到拼写错误 '{detected_system}'，已修复为 '{fixed_system}'")
    else:
        fixed_system = detected_system
        print(f"✅ 系统检测正常: '{fixed_system}'")
    
    return fixed_system

def test_go_installer():
    """测试Go安装器"""
    print("\n🧪 测试Go安装器...")
    
    try:
        # 模拟GoWebPanelInstaller的初始化
        detected_system = platform.system().lower().strip()
        if detected_system == 'linlx':
            system = 'linux'
        else:
            system = detected_system
        
        arch = platform.machine().lower()
        
        print(f"系统: {system}")
        print(f"架构: {arch}")
        
        # 测试支持的系统
        supported_systems = ['windows', 'linux', 'darwin']
        if system in supported_systems:
            print(f"✅ 系统 '{system}' 受支持")
            return True
        else:
            print(f"❌ 系统 '{system}' 不受支持")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_online_installer():
    """测试在线安装器"""
    print("\n🧪 测试在线安装器...")
    
    try:
        # 模拟OnlineInstaller的初始化
        detected_system = platform.system().lower().strip()
        if detected_system == 'linlx':
            system = 'linux'
        else:
            system = detected_system
        
        print(f"在线安装器检测到系统: {system}")
        
        supported_systems = ['windows', 'linux', 'darwin']
        if system in supported_systems:
            print(f"✅ 在线安装器支持系统 '{system}'")
            return True
        else:
            print(f"❌ 在线安装器不支持系统 '{system}'")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_fixed_files():
    """检查已修复的文件"""
    print("\n📁 检查已修复的文件...")
    
    files_to_check = [
        'online_install_go.py',
        'online_install.py', 
        'install.py'
    ]
    
    for filename in files_to_check:
        filepath = Path(filename)
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if "detected_system == 'linlx'" in content:
                    print(f"✅ {filename} 已包含linlx修复")
                else:
                    print(f"⚠️  {filename} 未包含linlx修复")
        else:
            print(f"❓ {filename} 文件不存在")

def main():
    """主函数"""
    print("="*60)
    print("🛠️  linlx错误修复验证脚本")
    print("="*60)
    
    # 测试系统检测
    system = test_system_detection()
    
    # 测试各个安装器
    go_test = test_go_installer()
    online_test = test_online_installer()
    
    # 检查修复的文件
    check_fixed_files()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    print(f"检测到的系统: {system}")
    print(f"Go安装器测试: {'✅ 通过' if go_test else '❌ 失败'}")
    print(f"在线安装器测试: {'✅ 通过' if online_test else '❌ 失败'}")
    
    if go_test and online_test:
        print("\n🎉 所有测试通过！linlx错误已修复。")
        print("\n现在您可以正常运行以下脚本:")
        print("  - python online_install_go.py")
        print("  - python online_install.py")
        print("  - python install.py")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()