#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作系统检测调试脚本
用于诊断"不支持的操作系统linlx"错误
"""

import platform
import sys
import os

def debug_system_info():
    """调试系统信息"""
    print("="*50)
    print("系统信息调试")
    print("="*50)
    
    # 检查platform.system()的原始输出
    raw_system = platform.system()
    print(f"platform.system() 原始输出: '{raw_system}'")
    print(f"platform.system() 类型: {type(raw_system)}")
    print(f"platform.system() 长度: {len(raw_system)}")
    
    # 检查转换为小写后的输出
    lower_system = platform.system().lower()
    print(f"platform.system().lower() 输出: '{lower_system}'")
    print(f"platform.system().lower() 类型: {type(lower_system)}")
    print(f"platform.system().lower() 长度: {len(lower_system)}")
    
    # 检查每个字符
    print("\n字符分析:")
    for i, char in enumerate(lower_system):
        print(f"  位置 {i}: '{char}' (ASCII: {ord(char)})")
    
    # 检查是否包含隐藏字符
    print(f"\n是否包含空格: {' ' in lower_system}")
    print(f"是否包含制表符: {'\t' in lower_system}")
    print(f"是否包含换行符: {'\n' in lower_system}")
    print(f"是否包含回车符: {'\r' in lower_system}")
    
    # 清理后的系统名称
    clean_system = lower_system.strip()
    print(f"\n清理后的系统名称: '{clean_system}'")
    
    # 其他系统信息
    print("\n其他系统信息:")
    print(f"platform.machine(): '{platform.machine()}'")
    print(f"platform.machine().lower(): '{platform.machine().lower()}'")
    print(f"platform.platform(): '{platform.platform()}'")
    print(f"platform.release(): '{platform.release()}'")
    print(f"platform.version(): '{platform.version()}'")
    print(f"os.name: '{os.name}'")
    print(f"sys.platform: '{sys.platform}'")
    
    # 检查支持的系统
    supported_systems = ['windows', 'linux', 'darwin']
    print(f"\n支持的系统: {supported_systems}")
    print(f"当前系统是否支持: {clean_system in supported_systems}")
    
    # 如果系统不支持，提供建议
    if clean_system not in supported_systems:
        print("\n❌ 检测到不支持的操作系统!")
        print(f"检测到的系统: '{clean_system}'")
        
        # 检查是否是拼写错误
        if clean_system == 'linlx':
            print("\n🔍 发现问题: 'linlx' 应该是 'linux'")
            print("这可能是由于以下原因造成的:")
            print("1. 系统环境变量被错误修改")
            print("2. Python platform模块返回了错误的值")
            print("3. 运行环境存在问题")
            
            print("\n🛠️ 建议解决方案:")
            print("1. 重启终端/命令提示符")
            print("2. 检查系统环境变量")
            print("3. 尝试在不同的终端中运行")
            print("4. 如果问题持续存在，请手动修改脚本中的系统检测逻辑")
        
        # 提供手动修复建议
        print("\n🔧 手动修复方法:")
        print("在相关的Python脚本中，找到以下代码:")
        print("    self.system = platform.system().lower()")
        print("替换为:")
        print("    detected_system = platform.system().lower().strip()")
        print("    if detected_system == 'linlx':")
        print("        self.system = 'linux'")
        print("    else:")
        print("        self.system = detected_system")
    else:
        print("\n✅ 系统检测正常!")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    debug_system_info()