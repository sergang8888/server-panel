package main

import (
	"fmt"
	"net/http"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/host"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/process"
)

type ProcessInfo struct {
	PID     int32   `json:"pid"`
	Name    string  `json:"name"`
	CPU     float64 `json:"cpu"`
	Memory  float32 `json:"memory"`
	Status  string  `json:"status"`
	Command string  `json:"command"`
}

type ServiceInfo struct {
	Name   string `json:"name"`
	Status string `json:"status"`
	Active bool   `json:"active"`
}

// 获取系统信息
func getSystemInfo(c *gin.Context) {
	// CPU使用率
	cpuPercent, _ := cpu.Percent(time.Second, false)
	cpuUsage := 0.0
	if len(cpuPercent) > 0 {
		cpuUsage = cpuPercent[0]
	}

	// 内存使用率
	memInfo, _ := mem.VirtualMemory()
	memoryUsage := memInfo.UsedPercent

	// 磁盘使用率
	diskInfo, _ := disk.Usage("/")
	if runtime.GOOS == "windows" {
		diskInfo, _ = disk.Usage("C:")
	}
	diskUsage := diskInfo.UsedPercent

	// 系统运行时间
	hostInfo, _ := host.Info()
	uptime := time.Duration(hostInfo.Uptime) * time.Second

	sysInfo := SystemInfo{
		CPUUsage:    cpuUsage,
		MemoryUsage: memoryUsage,
		DiskUsage:   diskUsage,
		Uptime:      formatUptime(uptime),
		Timestamp:   time.Now().Unix(),
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    sysInfo,
	})
}

// 获取进程列表
func getProcesses(c *gin.Context) {
	processes, err := process.Processes()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	var processList []ProcessInfo
	for _, p := range processes {
		name, _ := p.Name()
		cpuPercent, _ := p.CPUPercent()
		memPercent, _ := p.MemoryPercent()
		status, _ := p.Status()
		cmdline, _ := p.Cmdline()

		// 限制命令行长度
		if len(cmdline) > 100 {
			cmdline = cmdline[:100] + "..."
		}

		processInfo := ProcessInfo{
			PID:     p.Pid,
			Name:    name,
			CPU:     cpuPercent,
			Memory:  memPercent,
			Status:  status[0], // 取第一个状态
			Command: cmdline,
		}

		processList = append(processList, processInfo)
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    processList,
	})
}

// 获取服务列表
func getServices(c *gin.Context) {
	var services []ServiceInfo

	// 常见服务列表
	serviceNames := []string{"nginx", "apache2", "mysql", "postgresql", "redis", "docker"}

	for _, serviceName := range serviceNames {
		status := getServiceStatus(serviceName)
		services = append(services, ServiceInfo{
			Name:   serviceName,
			Status: status,
			Active: status == "active" || status == "running",
		})
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    services,
	})
}

// 获取服务状态
func getServiceStatus(serviceName string) string {
	var cmd *exec.Cmd

	if runtime.GOOS == "windows" {
		// Windows服务查询
		cmd = exec.Command("sc", "query", serviceName)
	} else {
		// Linux systemctl查询
		cmd = exec.Command("systemctl", "is-active", serviceName)
	}

	output, err := cmd.Output()
	if err != nil {
		return "unknown"
	}

	outputStr := strings.TrimSpace(string(output))

	if runtime.GOOS == "windows" {
		if strings.Contains(outputStr, "RUNNING") {
			return "running"
		} else if strings.Contains(outputStr, "STOPPED") {
			return "stopped"
		}
		return "unknown"
	} else {
		if outputStr == "active" {
			return "active"
		} else if outputStr == "inactive" {
			return "inactive"
		}
		return outputStr
	}
}

// 格式化运行时间
func formatUptime(uptime time.Duration) string {
	days := int(uptime.Hours()) / 24
	hours := int(uptime.Hours()) % 24
	minutes := int(uptime.Minutes()) % 60

	if days > 0 {
		return fmt.Sprintf("%d天 %d小时 %d分钟", days, hours, minutes)
	} else if hours > 0 {
		return fmt.Sprintf("%d小时 %d分钟", hours, minutes)
	} else {
		return fmt.Sprintf("%d分钟", minutes)
	}
}

// 终止进程
func killProcess(c *gin.Context) {
	pidStr := c.Param("pid")
	pid, err := strconv.Atoi(pidStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"error":   "Invalid PID",
		})
		return
	}

	p, err := process.NewProcess(int32(pid))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{
			"success": false,
			"error":   "Process not found",
		})
		return
	}

	err = p.Kill()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"error":   err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Process killed successfully",
	})
}