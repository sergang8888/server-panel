package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
)

func main() {
    r := gin.Default()

    // 跨域配置，方便前端调用
    r.Use(func(c *gin.Context) {
        c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
        c.Next()
    })

    // 路由分组
    api := r.Group("/api")
    {
        // 监控相关接口
        api.GET("/monitor/cpu", getCPUUsage)
        api.GET("/monitor/memory", getMemoryUsage)

        // 文件管理相关接口
        api.GET("/files", listFiles)
        api.POST("/files/upload", uploadFile)
    }

    // 启动服务
    r.Run(":8080")
}