package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

type Config struct {
	Port     string `json:"port"`
	Debug    bool   `json:"debug"`
	CameraIP string `json:"camera_ip"`
}

type SystemInfo struct {
	CPUUsage    float64 `json:"cpu_usage"`
	MemoryUsage float64 `json:"memory_usage"`
	DiskUsage   float64 `json:"disk_usage"`
	Uptime      string  `json:"uptime"`
	Timestamp   int64   `json:"timestamp"`
}

type CameraManager struct {
	Recording     bool   `json:"recording"`
	RecordingFile string `json:"recording_file"`
	StartTime     time.Time
}

var (
	config        Config
	cameraManager CameraManager
	upgrader      = websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}
)

func main() {
	// 加载配置
	loadConfig()

	// 创建录制目录
	os.MkdirAll("recordings", 0755)

	// 设置Gin模式
	if !config.Debug {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	// 静态文件服务
	r.Static("/static", "./static")
	r.LoadHTMLGlob("templates/*")

	// 路由设置
	setupRoutes(r)

	// 启动服务器
	port := config.Port
	if port == "" {
		port = "5000"
	}

	fmt.Printf("Starting Go Web Panel on 0.0.0.0:%s\n", port)
	log.Fatal(r.Run(":" + port))
}

func loadConfig() {
	// 默认配置
	config = Config{
		Port:     "5000",
		Debug:    false,
		CameraIP: "192.168.1.41:8080",
	}

	// 尝试从文件加载配置
	if data, err := os.ReadFile("config.json"); err == nil {
		json.Unmarshal(data, &config)
	}
}

func setupRoutes(r *gin.Engine) {
	// 主页
	r.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index_go.html", gin.H{
			"title": "Go Web Panel",
		})
	})

	// API路由组
	api := r.Group("/api")
	{
		// 系统信息API
		api.GET("/system", getSystemInfo)
		api.GET("/processes", getProcesses)
		api.GET("/services", getServices)

		// 摄像头API
		camera := api.Group("/camera")
		{
			camera.GET("/stream", getCameraStream)
			camera.POST("/snapshot", takeSnapshot)
			camera.POST("/start-recording", startRecording)
			camera.POST("/stop-recording", stopRecording)
			camera.GET("/status", getCameraStatus)
		}
	}

	// WebSocket连接
	r.GET("/ws", handleWebSocket)
}