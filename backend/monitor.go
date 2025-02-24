package main

import (
    "os/exec"
    "strings"
    "github.com/gin-gonic/gin"
)

// 获取CPU使用率（简单实现，仅示例）
func getCPUUsage(c *gin.Context) {
    cmd := exec.Command("top", "-bn1")
    output, err := cmd.Output()
    if err != nil {
        c.JSON(500, gin.H{"error": "Failed to get CPU usage"})
        return
    }

    // 解析top输出，提取CPU使用率（这里简化处理）
    lines := strings.Split(string(output), "\n")
    for _, line := range lines {
        if strings.Contains(line, "%Cpu") {
            fields := strings.Fields(line)
            if len(fields) > 1 {
                c.JSON(200, gin.H{"cpu_usage": fields[1]})
                return
            }
        }
    }
    c.JSON(500, gin.H{"error": "CPU usage not found"})
}

// 获取内存使用情况
func getMemoryUsage(c *gin.Context) {
    cmd := exec.Command("free", "-m")
    output, err := cmd.Output()
    if err != nil {
        c.JSON(500, gin.H{"error": "Failed to get memory usage"})
        return
    }

    // 解析free输出
    lines := strings.Split(string(output), "\n")
    if len(lines) > 1 {
        fields := strings.Fields(lines[1]) // 取Mem行
        if len(fields) >= 3 {
            c.JSON(200, gin.H{
                "total":  fields[1],
                "used":   fields[2],
                "free":   fields[3],
            })
            return
        }
    }
    c.JSON(500, gin.H{"error": "Memory usage not found"})
}